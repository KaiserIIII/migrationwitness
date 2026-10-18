"""Selected broken/fixed controls. A harness ERROR cannot satisfy an expected FAIL."""
import os
import pytest

CONTROLS = {
    'lock_timeout':'PASS', 'concurrent_dml':'PASS', 'old_new_clients_safe':'PASS',
    'old_new_clients_break':'FAIL', 'index_cancel':'FAIL', 'index_recover':'PASS',
    'backfill_bad':'FAIL', 'backfill_safe':'PASS', 'constraints_safe':'PASS',
    'privileges_bad':'FAIL', 'privileges_safe':'PASS', 'partial_recovery':'PASS',
}


@pytest.mark.parametrize('scenario,want', CONTROLS.items())
def test_real_disposable_control(pg_bin, tmp_path, scenario, want):
    if hasattr(os,'geteuid') and os.geteuid()==0:
        pytest.skip('Integration requires unprivileged initdb')
    from migrationwitness.runner import run
    from migrationwitness.evidence import verify
    result=run(scenario,pg_bin,tmp_path/scenario)
    assert result['outcome']==want, result
    assert result['control_agreement'] is True
    assert verify(tmp_path/scenario)==[]
    assert (tmp_path/scenario/'postgres-log.json').exists()
    if scenario.startswith('index_'):
        assert result['details']['cancel_sqlstate']=='57014'
        assert result['details']['intermediate_indexes'][0]['indisvalid'] is False
    if scenario=='lock_timeout':
        assert result['details']['sqlstate']=='55P03'
        assert result['details']['blocker_observed'] is True
    if scenario=='concurrent_dml':
        assert result['details']['acknowledged_operations']==60
        assert result['details']['observer_samples']>0
    if scenario.startswith('backfill_'):
        assert result['details']['intervening_updates']==10


def test_runner_api_exists():
    from importlib.util import find_spec
    assert find_spec('migrationwitness.runner') is not None


def test_uncommitted_migration_cannot_pass(pg_bin,tmp_path):
    if hasattr(os,'geteuid') and os.geteuid()==0:pytest.skip('Unprivileged initdb required')
    from migrationwitness.runner import run
    case={'name':'uncommitted','migration_sql':['BEGIN','ALTER TABLE business ADD COLUMN note text'],
          'assertions':[{'name':'committed note','sql':"SELECT EXISTS(SELECT FROM information_schema.columns WHERE table_name='business' AND column_name='note')"}]}
    r=run(case,pg_bin,tmp_path/'run')
    assert r['outcome']=='FAIL'
    assert any(c['name']=='migration transaction completed' and c['ok'] is False for c in r['checks'])
