# MigrationWitness Implementation Plan

> For agentic workers: execute tasks inline with executing-plans; independent reviewers use requesting-code-review. User has authorized autonomous execution without intermediate approval.

**Goal:** Deliver reproducible disposable PostgreSQL migration witnesses if the preimplementation value gate passes.

**Architecture:** Private local cluster lifecycle, psycopg sessions, declared SQL contracts, bounded workload ledger, observed barriers, evidence writer and offline render/verification. Raw experiment evidence stays outside the source tree; selected synthetic examples have explicit provenance.

**Tech Stack:** Python 3.13/3.14, PostgreSQL 16/17, psycopg 3.3.4, pytest. Official upstream binaries/source pinned in dependency provenance.

## Global Constraints

- No existing DSN, production database, private data, publishing, upstream PR, or old project modification.
- Separate experimental failures from native behavior, tool issues and framework failures.
- No product implementation until value gate evidence exists. Preserve unsuccessful runs.

### Task 1: Environment and pilot

- [x] Install official signed Alpine packages in dedicated WSL; record versions, hashes and source commits.
- [x] Run native index interruption and one actual tool plan; save commands/stdout/stderr/catalog evidence; write VALUE_GATE.md.

### Task 2: Evidence and safety core (TDD)

Files: tests/test_evidence.py, tests/test_safety.py, migrationwitness/evidence.py, cluster.py.
Interfaces: Evidence(root).event(kind, **fields), seal(), verify(root); Cluster(pg_bin, root) context manager yielding connect() for its own database only.

- [x] Test refuses existing evidence directory, detects modified evidence, escapes HTML values, refuses missing PostgreSQL executables and root initdb; run failing tests.
- [x] Implement minimal append-only evidence, hashes/renderer and private lifecycle; rerun tests.

### Task 3: Runtime contracts (TDD)

Files: tests/test_oracles.py, tests/test_integration.py, migrationwitness/oracles.py, runner.py, scenarios.py.
Interfaces: compare_rows(expected, actual), evaluate(checks) -> PASS/FAIL/INCONCLUSIVE; run(scenario, pg_bin, output) -> JSON result.

- [x] Test ledger detects dropped and wrong values, unknown is not pass, all 12 expected controls on actual PG; watch missing behavior fail.
- [x] Implement bounded observers, SQL outcome capture, contracts and scenarios; run PG16/17.

### Task 4: Trusted external commands and reports (TDD)

Files: tests/test_cli.py, migrationwitness/cli.py, commands.py, __main__.py, examples/.
Interfaces: CLI list/run/verify/render; explicit trusted argv opt-in and outer timeout; command result is evidence, never correctness oracle.

- [x] Test no-shell argv, timeout/nonzero exits and report verification/CLI status behavior; run red then green.
- [x] Compare actual tool outputs with independent oracles; record issue-specific limitations.

### Task 5: Independent acceptance and freeze

- [x] Fresh-install tests and all native scenarios on both majors; measure selected controls and observer overhead under protocol.
- [x] Independent code/security/claim review; reproduce and fix real important defects with regression tests.
- [x] Windows core/CLI tests and WSL distinction, report actual NOT RUN cases.
- [x] English README, architecture, safety, dependency/competitor/upstream results and resume; local Git commit and verified source ZIP/Git bundle.
