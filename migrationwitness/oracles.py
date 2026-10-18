"""Independent expectations; no correctness inferred from command exit status."""
def compare_rows(expected: dict, rows: list) -> dict:
    actual = {}
    duplicates = []
    for key, value in rows:
        if key in actual:
            duplicates.append(key)
        actual[key] = value
    missing = sorted(set(expected)-set(actual))
    extra = sorted(set(actual)-set(expected))
    changed = sorted(k for k in set(actual)&set(expected) if actual[k] != expected[k])
    return dict(ok=not (missing or extra or changed or duplicates), missing=missing, extra=extra,
                changed=changed, duplicates=duplicates, expected_rows=len(expected), actual_rows=len(rows))


def evaluate(checks: list[dict]) -> str:
    if any(c.get('ok') is False for c in checks):
        return 'FAIL'
    if not checks or any(c.get('ok') is not True for c in checks):
        return 'INCONCLUSIVE'
    return 'PASS'
