"""Experiment API. A selected-control agreement is distinct from database correctness."""
from __future__ import annotations
import datetime
import platform
import time
from pathlib import Path
from .cluster import Cluster
from .evidence import Evidence, render
from .oracles import evaluate
from .runtime import Context
from .scenarios import CONTROLS, execute


def run(scenario: str | dict, pg_bin: Path, output: Path, *, observe=True, allow_command=False) -> dict:
    from .custom import validate_case, execute_case
    case=validate_case(scenario) if isinstance(scenario,dict) else None
    if case is None and scenario not in CONTROLS:
        raise ValueError('Unknown scenario')
    if case and case.get('migration_argv') and not allow_command:
        raise ValueError('Explicit trusted command opt-in is required')
    evidence=Evidence(output)
    start=time.monotonic()
    result=dict(format=1,scenario=case['name'] if case else scenario,expected_control=case.get('expected_control') if case else CONTROLS[scenario],outcome='ERROR',
                classification='caller-provided trusted scenario; tool attribution requires investigation' if case else 'constructed native PostgreSQL control, not an upstream tool bug',
                utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                environment=dict(python=platform.python_version(),platform=platform.platform()),
                checks=[],details={},observer_enabled=observe)
    try:
        with Cluster(pg_bin,evidence) as cluster:
            ctx=Context(cluster,evidence,observe)
            result['postgres_version']=ctx.sql(ctx.admin,'SELECT version()')['rows'][0][0]
            try:
                ctx.setup();ctx.metadata('before')
                if case:execute_case(case,ctx,allow_command)
                else:execute(scenario,ctx)
                ctx.close_workers();ctx.final_data();ctx.metadata('after')
                result.update(outcome=evaluate(ctx.checks),checks=ctx.checks,details=ctx.details)
            finally:
                ctx.close_workers()
    except Exception as e:
        result.update(outcome='ERROR',error_type=type(e).__name__,error=str(e))
        evidence.event('framework_or_environment_error',error_type=type(e).__name__,error=str(e))
    result['elapsed_s']=time.monotonic()-start
    result['control_agreement']=(result['outcome']==result['expected_control']) if result['expected_control'] else None
    evidence.write_json('result.json',result);render(evidence.root);evidence.seal()
    return result
