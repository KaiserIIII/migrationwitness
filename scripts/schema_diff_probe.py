"""Actual #316 default-protection / deliberately unsafe partial-apply probe.

Trusted pinned pg-schema-diff binary only. The live DB is newly initialized.
The unsafe control is intentional and NEVER an instruction for production.
"""
import argparse
import json
from pathlib import Path
from migrationwitness.cluster import Cluster
from migrationwitness.evidence import Evidence,render
from migrationwitness.commands import execute_command
from migrationwitness.runtime import Context

p=argparse.ArgumentParser()
p.add_argument('--pg-bin',required=True,type=Path)
p.add_argument('--tool-path',required=True)
p.add_argument('--output',required=True,type=Path)
a=p.parse_args()
e=Evidence(a.output)
r={'tool':'pg-schema-diff','status':'ERROR'}
try:
    with Cluster(a.pg_bin,e) as cluster:
        ctx=Context(cluster,e);c=ctx.admin
        r['postgres_version']=c.execute('select version()').fetchone()[0]
        dsn='host='+str(cluster.root)+' dbname=mw_test user=mw_owner sslmode=disable'
        desired=e.root/'desired';desired.mkdir()
        (desired/'schema.sql').write_text('CREATE TABLE t(id int PRIMARY KEY,u int);',encoding='utf8')
        c.execute('CREATE TABLE t(id int PRIMARY KEY,u int,c int);CREATE INDEX t_u ON t(u) WHERE c IS NULL;INSERT INTO t VALUES(1,2,3)')
        def command(args):
            result=execute_command([a.tool_path,*args],cluster.command_env(),allowed=True,timeout=35)
            e.event('actual_tool_command',**result)
            return result
        plan=command(['plan','--from-dsn',dsn,'--to-dir',str(desired)])
        r['validated_plan_returncode']=plan['returncode']
        r['validated_plan_has_42704']='42704' in (plan['stdout']+plan['stderr'])
        r['live_columns_after_validation']=c.execute("SELECT attname FROM pg_attribute WHERE attrelid='t'::regclass AND attnum>0 AND NOT attisdropped ORDER BY attnum").fetchall()
        unvalidated=command(['plan','--from-dsn',dsn,'--to-dir',str(desired),'--disable-plan-validation'])
        r['unvalidated_plan_returncode']=unvalidated['returncode']
        applied=command(['apply','--from-dsn',dsn,'--to-dir',str(desired),'--disable-plan-validation','--allow-hazards','DELETES_DATA,ACQUIRES_ACCESS_EXCLUSIVE_LOCK,INDEX_DROPPED','--skip-confirm-prompt'])
        r['unsafe_apply_returncode']=applied['returncode']
        r['live_columns_after_unsafe_apply']=c.execute("SELECT attname FROM pg_attribute WHERE attrelid='t'::regclass AND attnum>0 AND NOT attisdropped ORDER BY attnum").fetchall()
        r['rows_after_unsafe_apply']=c.execute('SELECT * FROM t').fetchall()
        r['status']='EXECUTED'
        r['expected_control_observed']=(plan['returncode']!=0 and r['validated_plan_has_42704'] and r['live_columns_after_validation']==[('id',),('u',),('c',)] and applied['returncode']!=0 and r['live_columns_after_unsafe_apply']==[('id',),('u',)])
        ctx.metadata('after actual unsafe tool apply')
except Exception as ex:
    r.update(status='BLOCKED',error=repr(ex));e.event('environment_or_recipe_error',error=repr(ex))
e.write_json('result.json',r);render(e.root);e.seal()
print(json.dumps(r,indent=2))
raise SystemExit(0 if r.get('expected_control_observed') else 1)
