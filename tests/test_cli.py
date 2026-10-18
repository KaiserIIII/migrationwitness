import json
import os
import subprocess
import sys
import pytest


def cli(*args):
    return subprocess.run([sys.executable,'-m','migrationwitness',*map(str,args)],capture_output=True,text=True,encoding='utf8',timeout=30)


def test_cli_lists_scenarios_and_rejects_invalid_choice():
    r=cli('list')
    assert r.returncode==0 and 'index_cancel' in json.loads(r.stdout)
    assert cli('run','nonexistent','--pg-bin','x','--output','x').returncode==1


def test_cli_verifies_unicode_evidence_and_rejects_tampering(tmp_path):
    from migrationwitness.evidence import Evidence,render
    e=Evidence(tmp_path/'中文');e.write_json('result.json',{'outcome':'PASS','value':'中文'});render(e.root);e.seal()
    assert cli('verify',e.root).returncode==0
    (e.root/'result.json').write_text('{}',encoding='utf8')
    assert cli('verify',e.root).returncode==2


def test_cli_real_good_and_bad_codes(pg_bin,tmp_path):
    if hasattr(os,'geteuid') and os.geteuid()==0:pytest.skip('Unprivileged initdb required')
    good=cli('run','privileges_safe','--pg-bin',pg_bin,'--output',tmp_path/'good')
    bad=cli('run','privileges_bad','--pg-bin',pg_bin,'--output',tmp_path/'bad')
    assert good.returncode==0,good.stderr
    assert bad.returncode==2,bad.stderr
    assert json.loads(bad.stdout)['outcome']=='FAIL'


def test_custom_nonboolean_assertion_is_inconclusive(pg_bin,tmp_path):
    if hasattr(os,'geteuid') and os.geteuid()==0:pytest.skip('Unprivileged initdb required')
    from migrationwitness.runner import run
    r=run({'name':'ambiguous','migration_sql':['SELECT 1'],'assertions':[{'name':'must return bool','sql':'SELECT 1'}]},pg_bin,tmp_path/'run')
    assert r['outcome']=='INCONCLUSIVE'
