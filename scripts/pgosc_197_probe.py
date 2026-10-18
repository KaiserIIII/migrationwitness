"""Preregistered actual upstream permission test. Synthetic private clusters only."""
import pathlib,sys,json,threading,time,hashlib,argparse,os
from migrationwitness.cluster import Cluster
from migrationwitness.evidence import Evidence,render
from migrationwitness.runtime import Context
from migrationwitness.commands import execute_command
from migrationwitness.oracles import compare_rows
import psycopg

p=argparse.ArgumentParser()
p.add_argument('--pg-bin',type=pathlib.Path,required=True)
p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--mode',choices=['pgosc','native'],required=True)
p.add_argument('--tool-launcher',required=True)
a=p.parse_args()
e=Evidence(a.output)
r={'format':1,'scenario':'pg-osc-197-'+a.mode,'classification':'actual upstream execution' if a.mode=='pgosc' else 'native PostgreSQL control','outcome':'ERROR','mode':a.mode,'checks':[],'source_commit':'0a439a873f9df1bf474cfe13060a115278b94658','fixture':'100 synthetic integer rows; migration role owns table; business role explicit SELECT INSERT UPDATE, no DELETE; no default grants'}
checks=r['checks']
def check(name,ok,**evidence):
    item=dict(name=name,ok=ok,**evidence);checks.append(item);e.event('invariant',**item)
try:
    with Cluster(a.pg_bin,e) as cluster:
        ctx=Context(cluster,e);admin=ctx.admin
        r['postgres_version']=admin.execute('select version()').fetchone()[0]
        for sql in ['CREATE ROLE migration_user LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION',
                    'CREATE ROLE business_user LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION',
                    'GRANT CREATE ON SCHEMA public TO migration_user',
                    'CREATE TABLE business(id integer PRIMARY KEY,value integer NOT NULL)',
                    'ALTER TABLE business OWNER TO migration_user',
                    'INSERT INTO business SELECT g,g*10 FROM generate_series(1,100) g',
                    'GRANT SELECT,INSERT,UPDATE ON business TO business_user']:
            ctx.sql(admin,sql)
        # Real authentication as the restricted LOGIN user over the owned private socket.
        kwargs=dict(host=str(cluster.root),dbname='mw_test',user='business_user',autocommit=True,connect_timeout=5,options='-c statement_timeout=10000 -c lock_timeout=2000')
        expected={i:i*10 for i in range(1,101)}
        def catalog(label):
            tables=ctx.sql(admin,"SELECT c.oid,c.relname,c.relowner::regrole::text,c.relacl::text FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' ORDER BY c.relname")
            grants=ctx.sql(admin,"SELECT grantee,privilege_type,is_grantable FROM information_schema.role_table_grants WHERE table_schema='public' AND table_name='business' ORDER BY grantee,privilege_type")
            data=ctx.sql(admin,'SELECT id,value FROM business ORDER BY id')
            ty=ctx.sql(admin,"SELECT atttypid::regtype::text FROM pg_attribute WHERE attrelid='business'::regclass AND attname='value' AND NOT attisdropped")
            bits=ctx.sql(admin,"SELECT has_table_privilege('business_user','business','SELECT'),has_table_privilege('business_user','business','INSERT'),has_table_privilege('business_user','business','UPDATE'),has_table_privilege('business_user','business','DELETE')")
            out=dict(tables=tables['rows'],grants=grants['rows'],data=data['rows'],value_type=ty['rows'][0][0],privilege_bits=bits['rows'][0],events=[x['event'] for x in (tables,grants,data,ty,bits)])
            e.event('catalog_checkpoint',label=label,**out)
            return out
        def business_probes(label):
            outputs=[]
            for name,sql in [('SELECT','SELECT count(*),sum(value) FROM business'),('INSERT','INSERT INTO business(id,value) VALUES(1001,123)'),('UPDATE','UPDATE business SET value=value+1 WHERE id=1'),('DELETE','DELETE FROM business WHERE id=1')]:
                with psycopg.connect(**kwargs) as c:
                    who=c.execute('SELECT session_user,current_user').fetchone()
                    assert who==('business_user','business_user')
                    ctx.sql(c,'BEGIN')
                    result=ctx.sql(c,sql,required=False)
                    outputs.append(dict(privilege=name,ok=result['ok'],sqlstate=result['sqlstate'],event=result['event'],identity=who))
                    ctx.sql(c,'ROLLBACK')
            e.event('restricted_user_probes',label=label,results=outputs)
            return outputs
        before=catalog('before');before_probes=business_probes('before')
        check('fixture privileges really granted before migration',list(before['privilege_bits'])==[True,True,True,False] and [x['ok'] for x in before_probes]==[True,True,True,False])
        old_oid=next(t[0] for t in before['tables'] if t[1]=='business')
        env=cluster.command_env();env['PGUSER']='migration_user'
        if a.mode=='pgosc':
            argv=[a.tool_launcher,'perform','--alter-statement','ALTER TABLE business ALTER COLUMN value TYPE bigint','--dbname','mw_test','--host',str(cluster.root),'--username','migration_user','--port','5432','--wait-time-for-lock','2','--verbose']
        else:argv=[str(a.pg_bin/'psql'),'-X','-v','ON_ERROR_STOP=1','-c','ALTER TABLE business ALTER COLUMN value TYPE bigint']
        holder={}
        def command():
            try:holder.update(execute_command(argv,env,allowed=True,timeout=35))
            except BaseException as ex:holder['exception']=repr(ex)
        t=threading.Thread(target=command,daemon=True);t.start()
        samples=0
        while t.is_alive() and samples<80:
            ctx.snapshot('actual migration running');samples+=1
            t.join(.05)
        t.join(40)
        if t.is_alive():raise TimeoutError('tool worker did not stop')
        if 'exception' in holder:raise RuntimeError(holder['exception'])
        tool_event=e.event('actual_migration_command',**holder)
        r['command']={k:v for k,v in holder.items() if k not in ('stdout_base64','stderr_base64')}
        after=catalog('after');after_probes=business_probes('after')
        new_oid=next(t[0] for t in after['tables'] if t[1]=='business')
        new_owner=next(t[2] for t in after['tables'] if t[1]=='business')
        complete=holder['returncode']==0 and not any(holder[k] for k in ('timed_out','truncated','capture_incomplete','descendants_terminated')) and after['value_type']=='bigint'
        swapped=(new_oid!=old_oid)
        check('actual migration completed target type',complete,event=tool_event)
        check('shadow swap observed' if a.mode=='pgosc' else 'native OID preserved',swapped if a.mode=='pgosc' else not swapped,old_oid=old_oid,new_oid=new_oid)
        check('owner preserved',new_owner=='migration_user',actual=new_owner)
        check('original business data preserved',compare_rows(expected,after['data'])['ok'])
        allowed_after=[x['ok'] for x in after_probes[:3]]
        check('business SELECT INSERT UPDATE preserved',all(allowed_after),probe_events=[x['event'] for x in after_probes[:3]],actual=allowed_after)
        check('forbidden DELETE remains forbidden',after_probes[3]['sqlstate']=='42501',event=after_probes[3]['event'])
        loss=complete and (swapped if a.mode=='pgosc' else True) and any(x['sqlstate']=='42501' for x in after_probes[:3]) and not all(after['privilege_bits'][:3])
        r.update(before=before,after=after,before_probes=before_probes,after_probes=after_probes,original_oid=old_oid,new_oid=new_oid,completed_shadow_swap=complete and swapped,permission_loss_reproduced=loss,samples=samples)
        # Explicit independent mitigation, after untouched-tool evidence is complete.
        if loss:
            ctx.sql(admin,'GRANT SELECT,INSERT,UPDATE ON business TO business_user')
            restored=business_probes('after explicit caller GRANT mitigation')
            r['explicit_grant_mitigation_restored']=[x['ok'] for x in restored]==[True,True,True,False]
        r['outcome']='FAIL' if any(c['ok'] is False for c in checks) else 'PASS'
        r['status']='REPRODUCED' if a.mode=='pgosc' and loss else 'NATIVE_CONTROL_PASS' if a.mode=='native' and r['outcome']=='PASS' else 'NOT_REPRODUCED' if complete else 'INCOMPLETE_NOT_A_REPRODUCTION'
except Exception as ex:
    r.update(outcome='ERROR',status='BLOCKED',error=repr(ex));e.event('framework_or_environment_error',error=repr(ex))
e.write_json('result.json',r);render(e.root);e.seal()
print(json.dumps(r,indent=2,ensure_ascii=False,default=str))
raise SystemExit(0 if r.get('status') in ('REPRODUCED','NATIVE_CONTROL_PASS','NOT_REPRODUCED') else 1)
