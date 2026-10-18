"""Breaks caught: shell expansion, hung migration, hidden nonzero exit, silent opt-in."""
import sys
import os
import time
import pytest


def test_trusted_command_needs_explicit_opt_in():
    from migrationwitness.commands import execute_command
    with pytest.raises(ValueError,match='trusted'):
        execute_command([sys.executable,'-c','print(1)'],{},allowed=False)


def test_argv_is_literal_and_exit_preserved():
    from migrationwitness.commands import execute_command
    r=execute_command([sys.executable,'-c','import sys; print(sys.argv[1]); sys.exit(7)','$(never); & 中文'],None,allowed=True)
    assert r['returncode']==7 and r['stdout'].strip()=='$(never); & 中文'


def test_command_timeout_is_not_success():
    from migrationwitness.commands import execute_command
    r=execute_command([sys.executable,'-c','import time; time.sleep(10)'],None,allowed=True,timeout=.1)
    assert r['timed_out'] is True and r['returncode']!=0


def test_output_budget_is_explicit():
    from migrationwitness.commands import execute_command
    r=execute_command([sys.executable,'-c','print("x"*10000)'],None,allowed=True,output_limit=100)
    assert r['truncated'] is True and len(r['stdout'])==100


def test_non_utf8_output_retains_raw_evidence():
    from migrationwitness.commands import execute_command
    r=execute_command([sys.executable,'-c','import sys; sys.stdout.buffer.write(bytes([255,254]))'],None,allowed=True)
    assert r['decode_errors'] is True and r['stdout_base64']=='//4='


def test_scenario_rejects_ambiguous_migration_and_large_input(tmp_path):
    from migrationwitness.custom import validate_case, load_case
    with pytest.raises(ValueError):
        validate_case({'name':'bad','migration_sql':['select 1'],'migration_argv':['tool']})
    p=tmp_path/'big.json';p.write_bytes(b' ' * 1_000_001)
    with pytest.raises(ValueError):load_case(p)


@pytest.mark.skipif(os.name=='nt',reason='POSIX process group containment only')
def test_parent_exit_does_not_leave_child_running(tmp_path):
    from migrationwitness.commands import execute_command
    target=tmp_path/'late'
    child='import time,pathlib; time.sleep(.5); pathlib.Path('+repr(str(target))+').write_text("escaped")'
    parent='import subprocess,sys; subprocess.Popen([sys.executable,"-c",'+repr(child)+'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)'
    r=execute_command([sys.executable,'-c',parent],None,allowed=True,timeout=.1)
    time.sleep(.7)
    assert not target.exists()
    assert r['descendants_terminated'] is True
