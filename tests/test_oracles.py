"""Breaks caught: false pass on missing rows, duplicate keys, unknown checks."""
def test_rows_and_outcome_contract():
    import importlib.util
    assert importlib.util.find_spec('migrationwitness') is not None, 'Oracles not implemented'


def test_ledger_diff_is_exact_and_rejects_duplicate_keys():
    from migrationwitness.oracles import compare_rows
    assert compare_rows({1:'a',2:'中文'}, [(1,'a'),(2,'中文')])['ok'] is True
    d = compare_rows({1:'a',2:'b'}, [(1,'WRONG'),(3,'x')])
    assert d['ok'] is False and d['missing']==[2] and d['extra']==[3] and d['changed']==[1]
    assert compare_rows({1:'a'}, [(1,'a'),(1,'a')])['ok'] is False


def test_unknown_not_pass_and_fail_not_masked_by_unknown():
    from migrationwitness.oracles import evaluate
    assert evaluate([{'ok': True}]) == 'PASS'
    assert evaluate([{'ok': None}]) == 'INCONCLUSIVE'
    assert evaluate([]) == 'INCONCLUSIVE'
    assert evaluate([{'ok': None}, {'ok': False}]) == 'FAIL'
