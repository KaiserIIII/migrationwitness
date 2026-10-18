"""Breaks caught: overwritten run, undetected tampering, unsafe rendered data."""
import json
from pathlib import Path
import pytest


def test_evidence_api_is_available():
    import importlib.util
    assert importlib.util.find_spec('migrationwitness') is not None, 'Evidence package not implemented'


def test_evidence_is_sealed_and_tampering_detected(tmp_path):
    from migrationwitness.evidence import Evidence, verify
    run = tmp_path / 'run'
    e = Evidence(run)
    e.event('sql', query='select 1', status='OK')
    e.write_json('result.json', {'outcome': 'PASS'})
    e.seal()
    assert verify(run) == []
    (run/'events.jsonl').write_text('{}\n')
    assert any('events.jsonl' in x for x in verify(run))


def test_existing_directory_and_path_escape_rejected(tmp_path):
    from migrationwitness.evidence import Evidence
    with pytest.raises(FileExistsError):
        Evidence(tmp_path)
    e = Evidence(tmp_path/'run')
    with pytest.raises(ValueError):
        e.write_json('../outside.json', {})
    with pytest.raises(ValueError):
        e.write_json('events.jsonl', {})


def test_html_cannot_execute_values_and_seal_is_final(tmp_path):
    from migrationwitness.evidence import Evidence, render
    e = Evidence(tmp_path/'run')
    e.write_json('result.json', {'outcome':'FAIL','value':'<script>alert(1)</script>', 'unicode':'中文'})
    render(e.root)
    html = (e.root/'report.html').read_text(encoding='utf8')
    assert '<script>' not in html and '&lt;script&gt;' in html and '中文' in html
    e.seal()
    with pytest.raises(RuntimeError):
        e.event('late')


def test_verifier_rejects_unlisted_file_and_unsafe_manifest(tmp_path):
    from migrationwitness.evidence import Evidence, verify
    e = Evidence(tmp_path/'run'); e.seal()
    (e.root/'extra').write_text('x')
    assert verify(e.root)
    (e.root/'manifest.json').write_text(json.dumps({'files':{'../secret':'abc'}}))
    assert verify(e.root)


def test_command_duration_does_not_collide_with_timeline_clock(tmp_path):
    from migrationwitness.evidence import Evidence
    e=Evidence(tmp_path/'run')
    e.event('trusted_command',elapsed_s=.25,returncode=0)
    row=json.loads((e.root/'events.jsonl').read_text())
    assert row['elapsed_s']==.25 and row['timeline_s']>=0


def test_nonobject_manifest_fails_closed(tmp_path):
    from migrationwitness.evidence import verify
    (tmp_path/'manifest.json').write_text('[]')
    assert verify(tmp_path)
