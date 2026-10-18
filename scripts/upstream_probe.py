"""Actual pinned pgroll and Atlas Community executions, new disposable clusters."""
import json,pathlib,sys,threading,time,os,argparse

from migrationwitness.cluster import Cluster
from migrationwitness.evidence import Evidence,render
from migrationwitness.commands import execute_command
from migrationwitness.runtime import Context

parser=argparse.ArgumentParser(description='Actual trusted pgroll or Atlas Community probe on a private cluster')
parser.add_argument('tool',choices=['pgroll','atlas'])
parser.add_argument('--pg-bin',type=pathlib.Path,required=True)
parser.add_argument('--tool-path',required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
major='see postgres_version';kind=args.tool
e=Evidence(args.output)
result={'tool':kind,'major':major,'status':'ERROR'}
def cmd(cluster,argv,required=True):
    r=execute_command(argv,cluster.command_env(),allowed=True,timeout=35)
    e.event('actual_tool_command',**r)
    if required and (r['returncode'] or r['timed_out']):raise RuntimeError(r['stderr'])
    return r
try:
    with Cluster(args.pg_bin,e) as cluster:
        ctx=Context(cluster,e);c=ctx.admin
        result['postgres_version']=c.execute('select version()').fetchone()[0]
        dsn='host='+str(cluster.root)+' dbname=mw_test user=mw_owner sslmode=disable'
        if kind=='pgroll':
            c.execute('CREATE TABLE client(id serial PRIMARY KEY,api_key varchar NOT NULL,name varchar NOT NULL,created_at timestamptz NOT NULL DEFAULT now(),updated_at timestamptz NOT NULL DEFAULT now());CREATE UNIQUE INDEX client_name_idx ON client(name);CREATE TABLE email(id serial PRIMARY KEY,fk_client_id int REFERENCES client(id))')
            c.execute("INSERT INTO client(api_key,name) SELECT 'api-'||g,'name-'||g FROM generate_series(1,100) g")
            tool=args.tool_path
            common=[tool,'--postgres-url',dsn,'--lock-timeout','200','--verbose']
            cmd(cluster,common+['init'])
            cmd(cluster,common+['baseline','baseline',str(e.root/'baseline'),'--yes'])
            migration=e.root/'index.json'
            migration.write_text(json.dumps({'operations':[{'create_index':{'name':'client_api_key_idx','table':'client','columns':[{'column':'api_key'}],'method':'btree'}}]}))
            blocker=cluster.connect('held_writer');blocker.execute('BEGIN');blocker.execute('UPDATE client SET api_key=api_key WHERE id=1')
            r={};t=threading.Thread(target=lambda:r.update(cmd(cluster,common+['start',str(migration),'--complete'],False)),daemon=True);t.start()
            # Capture actual pgroll lock wait and index registration before releasing.
            deadline=time.monotonic()+6
            observed=False
            while time.monotonic()<deadline and t.is_alive():
                row=c.execute("select pid from pg_stat_activity where datname=current_database() and wait_event_type='Lock' and query ilike '%CREATE%INDEX%'").fetchone()
                if row:
                    ctx.snapshot('pgroll index waiting on held writer');observed=True
                    result['index_during_wait']=c.execute("select cl.relname,i.indisvalid,i.indisready from pg_index i join pg_class cl on cl.oid=i.indexrelid where cl.relname='client_api_key_idx'").fetchall()
                    time.sleep(.8);break
                time.sleep(.02)
            blocker.execute('ROLLBACK');t.join(35)
            if t.is_alive():raise TimeoutError('pgroll did not finish')
            result.update(tool_returncode=r.get('returncode'),lock_wait_observed=observed,stderr=r.get('stderr'),stdout=r.get('stdout'))
            result['index_catalog']=c.execute("select c.relname,i.indisvalid,i.indisready from pg_index i join pg_class c on c.oid=i.indexrelid where c.relname='client_api_key_idx'").fetchall()
            result['business_checksum']=c.execute('select count(*),sum(id),count(distinct api_key) from client').fetchone()
            result['issue_1013_status']='REPRODUCED_RELATED_TIMEOUT_PATH' if 'already exists' in (r.get('stdout','')+r.get('stderr','')) else 'NOT_REPRODUCED_UNDER_STATED_CONDITIONS'
            result['qualification']='Controlled held-writer/lock-timeout path is not the original reporter workload; no historical environment identity claimed.'
            retry=cmd(cluster,common+['start',str(migration),'--complete'],False)
            result['quiet_retry_returncode']=retry['returncode']
            result['index_after_quiet_retry']=c.execute("select c.relname,i.indisvalid,i.indisready from pg_index i join pg_class c on c.oid=i.indexrelid where c.relname='client_api_key_idx'").fetchall()
        elif kind=='atlas':
            c.execute("CREATE TABLE business(id int primary key,value text);INSERT INTO business VALUES(1,'00001234567890123456'),(2,'中文')")
            migrations=e.root/'migrations';migrations.mkdir()
            (migrations/'202610180001_backfill.sql').write_text("UPDATE business SET value=left(value,5);",encoding='utf8')
            tool=args.tool_path
            cmd(cluster,[tool,'migrate','hash','--dir','file://'+str(migrations)])
            # Public Unix-socket URL, no network listener or external DB.
            url='postgres://mw_owner@/mw_test?host='+str(cluster.root)+'&sslmode=disable'
            common=[tool,'migrate','apply','--url',url,'--dir','file://'+str(migrations),'--allow-dirty','--tx-mode','none']
            cmd(cluster,common+['--dry-run'])
            before=c.execute('select * from business order by id').fetchall()
            r=cmd(cluster,common,False)
            after=c.execute('select * from business order by id').fetchall()
            result.update(tool_returncode=r['returncode'],before=before,after=after,business_invariant='PASS' if before==after else 'FAIL',qualification='Deliberately bad caller migration; Community migration execution does not promise arbitrary business correctness; not Atlas defect.')
        result['status']='EXECUTED'
        ctx.metadata('after actual tool')
except Exception as ex:
    result.update(status='BLOCKED',error=repr(ex));e.event('environment_or_recipe_error',error=repr(ex))
e.write_json('result.json',result);render(e.root);e.seal()
print(json.dumps(result,indent=2,ensure_ascii=False,default=str))
raise SystemExit(0 if result['status']=='EXECUTED' else 1)
