"""Append-only run events and offline integrity checks. Hashes are not signatures."""
from __future__ import annotations
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import threading
import time


def _path(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    if not name or '\\' in name or p.is_absolute() or '..' in p.parts or ':' in name:
        raise ValueError('Unsafe evidence path')
    result = root.joinpath(*p.parts)
    if result.is_symlink() or not result.resolve().is_relative_to(root.resolve()):
        raise ValueError('Evidence path escapes run')
    return result


class Evidence:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, mode=0o700, exist_ok=False)
        self._lock = threading.Lock()
        self._sealed = False
        self._start = time.monotonic()
        self._seq = 0
        (self.root/'events.jsonl').touch()

    def event(self, kind: str, **fields):
        with self._lock:
            if self._sealed:
                raise RuntimeError('Run sealed')
            self._seq += 1
            item = dict(fields)
            item.update(seq=self._seq, timeline_s=time.monotonic()-self._start, kind=kind)
            with (self.root/'events.jsonl').open('a', encoding='utf8') as f:
                f.write(json.dumps(item, ensure_ascii=False, default=str)+'\n')
            return self._seq

    def write_json(self, name: str, value):
        if self._sealed:
            raise RuntimeError('Run sealed')
        if name in ('events.jsonl', 'manifest.json'):
            raise ValueError('Reserved evidence path')
        path = _path(self.root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False, default=str)
            f.write('\n')

    def seal(self):
        with self._lock:
            if self._sealed:
                raise RuntimeError('Already sealed')
            files = {}
            for p in sorted(self.root.rglob('*')):
                if p.is_symlink():
                    raise ValueError('Symlink in evidence')
                if p.is_file():
                    files[p.relative_to(self.root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
            manifest = {'format': 1, 'algorithm': 'sha256', 'files': files}
            with (self.root/'manifest.json').open('x', encoding='utf8') as f:
                json.dump(manifest, f, indent=2)
            self._sealed = True


def verify(root: Path) -> list[str]:
    root = Path(root)
    errors = []
    try:
        manifest_path = _path(root, 'manifest.json')
        if manifest_path.stat().st_size > 2_000_000:
            raise ValueError('Manifest too large')
        data = json.loads(manifest_path.read_text(encoding='utf8'))
        if not isinstance(data,dict) or data.get('format') != 1 or data.get('algorithm') != 'sha256' or not isinstance(data.get('files'), dict):
            raise ValueError('Invalid manifest')
        for name, expected in data['files'].items():
            p = _path(root, name)
            if not isinstance(expected, str) or len(expected) != 64 or name == 'manifest.json':
                raise ValueError('Invalid hash entry')
            h = hashlib.sha256()
            try:
                with p.open('rb') as f:
                    for chunk in iter(lambda: f.read(65536), b''):
                        h.update(chunk)
                if h.hexdigest() != expected:
                    errors.append('Hash mismatch: '+name)
            except OSError:
                errors.append('Missing/unreadable: '+name)
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
        if actual != set(data['files']) | {'manifest.json'}:
            errors.append('File inventory mismatch')
    except (OSError, ValueError, TypeError) as e:
        errors.append(str(e))
    return errors


def render(root: Path):
    """Render once before sealing; never overwrite an existing report."""
    root = Path(root)
    if (root/'manifest.json').exists():
        raise RuntimeError('Cannot modify sealed evidence')
    value = json.loads((root/'result.json').read_text(encoding='utf8'))
    body = json.dumps(value, indent=2, ensure_ascii=False)
    with (root/'report.html').open('x', encoding='utf8') as f:
        f.write('<!doctype html><html lang="en"><meta charset="utf-8">'
                '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">'
                '<title>MigrationWitness evidence</title><style>body{max-width:1000px;margin:2em auto;font:16px system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
                '<h1>MigrationWitness</h1><p>Bounded disposable experiment; no production guarantee.</p><pre>'
                +html.escape(body)+'</pre></html>')
    with (root/'report.md').open('x', encoding='utf8') as f:
        status=value.get('outcome','UNKNOWN')
        if status not in ('PASS','FAIL','INCONCLUSIVE','ERROR','UNKNOWN'):
            status='UNKNOWN'
        f.write('# MigrationWitness evidence\n\nOutcome: '+status+'\n\n')
        # HTML escaped inside a pre element; no Markdown links/raw tags from SQL.
        f.write('<pre>'+html.escape(body)+'</pre>\n')
