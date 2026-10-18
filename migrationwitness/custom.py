"""Small editable JSON scenarios over the documented business(id,value) fixture."""
import json
from pathlib import Path
from .commands import execute_command


def validate_case(case):
    if not isinstance(case,dict):raise ValueError('Scenario must be an object')
    allowed={'name','setup_sql','migration_sql','migration_argv','assertions','concurrent_workload','expected_control','command_timeout_s'}
    if set(case)-allowed:raise ValueError('Unknown scenario fields')
    if not isinstance(case.get('name'),str) or not 1<=len(case['name'])<=100:
        raise ValueError('Scenario name required, max 100 chars')
    if bool(case.get('migration_sql'))==bool(case.get('migration_argv')):
        raise ValueError('Specify exactly one nonempty SQL list or command argv')
    for key in ('setup_sql','migration_sql'):
        value=case.get(key,[])
        if not isinstance(value,list) or len(value)>20 or not all(isinstance(s,str) and 0<len(s)<100000 for s in value):
            raise ValueError('Invalid trusted SQL list')
    assertions=case.get('assertions',[])
    if not isinstance(assertions,list) or len(assertions)>20:
        raise ValueError('Invalid assertions')
    for a in assertions:
        if not isinstance(a,dict) or set(a)!={'name','sql'} or not isinstance(a['name'],str) or not isinstance(a['sql'],str) or not 0<len(a['sql'])<100000:
            raise ValueError('Assertion requires name and SQL')
    if case.get('expected_control') not in (None,'PASS','FAIL'):
        raise ValueError('Invalid expected control')
    if 'concurrent_workload' in case and not isinstance(case['concurrent_workload'],bool):
        raise ValueError('concurrent_workload must be boolean')
    timeout=case.get('command_timeout_s',20)
    if not isinstance(timeout,(int,float)) or isinstance(timeout,bool) or not 0<timeout<=40:
        raise ValueError('Invalid command timeout')
    return case


def load_case(path):
    path=Path(path)
    if path.stat().st_size>1_000_000:raise ValueError('Scenario file exceeds 1 MB')
    return validate_case(json.loads(path.read_text(encoding='utf-8-sig')))


def execute_case(case,ctx,allow_command):
    for sql in case.get('setup_sql',[]):ctx.sql(ctx.admin,sql)
    threads=ctx.workload() if case.get('concurrent_workload') else []
    ctx.snapshot('before caller migration')
    if case.get('migration_argv'):
        c=execute_command(case['migration_argv'],ctx.cluster.command_env(),allowed=allow_command,
                          timeout=case.get('command_timeout_s',20))
        seq=ctx.evidence.event('trusted_command',**c)
        ctx.check('trusted command execution completed',c['returncode']==0 and not any(c[k] for k in ('timed_out','truncated','capture_incomplete','descendants_terminated','decode_errors')),event=seq)
    else:
        for sql in case['migration_sql']:
            o=ctx.sql(ctx.admin,sql,required=False)
            ctx.check('caller migration statement succeeded',o['ok'],event=o['event'])
    committed=ctx.admin.info.transaction_status.name=='IDLE'
    ctx.check('migration transaction completed',committed,transaction_status=ctx.admin.info.transaction_status.name)
    if not committed:
        ctx.sql(ctx.admin,'ROLLBACK')
    for t in threads:ctx.join(t)
    ctx.snapshot('after caller migration')
    validator=ctx.cluster.connect('independent_validator')
    for a in case.get('assertions',[]):
        o=ctx.sql(validator,a['sql'],required=False)
        if not o['ok']:
            ok=False
        elif o['result_set_count']==1 and len(o['rows'])==1 and len(o['rows'][0])==1 and isinstance(o['rows'][0][0],bool):
            ok=o['rows'][0][0]
        else:ok=None
        ctx.check(a['name'],ok,event=o['event'])
