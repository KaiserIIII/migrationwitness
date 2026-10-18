# MigrationWitness

Run a PostgreSQL migration against a disposable database while checking application contracts, lock waits and recovery state. MigrationWitness is an experimental test harness, not a migration engine or a production database monitor.

It creates its own private local cluster, seeds synthetic business rows, runs controlled clients, observes PostgreSQL and evaluates declared invariants independently of migration exit codes. JSON, HTML and Markdown reports link checks to raw SQL and catalog events. Nothing connects to an existing database.

## Supported scope

- PostgreSQL 16 and 17 on Linux, including a dedicated WSL environment on Windows.
- Python 3.12+; the actual tested versions and counts are recorded in [TEST_RESULTS.md](docs/TEST_RESULTS.md).
- Windows can install the Python package, list scenarios and verify/render offline evidence. Native Windows PostgreSQL cluster execution is deliberately refused; use WSL/Linux. Native Windows PostgreSQL acceptance is **NOT RUN**.
- Twelve native control scenarios, editable trusted SQL/JSON cases, opt-in external argv, independent committed-data/role/constraint checks, SQLSTATE and lock evidence.

## Install

Use a normal, unprivileged Linux user with official PostgreSQL server binaries (`initdb`, `pg_ctl`, `postgres`) installed. Do not run PostgreSQL as root.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
python -m migrationwitness list
python -m migrationwitness run concurrent_dml --pg-bin /usr/lib/postgresql/17/bin --output runs/dml-001
python -m migrationwitness verify runs/dml-001
```

On Alpine the binary path is `/usr/libexec/postgresql17`. On Debian/Ubuntu it is commonly `/usr/lib/postgresql/17/bin`; point to the actual installed version. Every output directory must be new.

Windows PowerShell (offline operations):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m migrationwitness list
.\.venv\Scripts\python.exe -m migrationwitness verify C:\path\to\copied-run
```

Python dependencies are pinned in `pyproject.toml`; acceptance artifacts and source commits are listed in [DEPENDENCIES.md](docs/DEPENDENCIES.md). Installation needs package-index access; an audit manifest accompanies the local delivery, not vendored executables.

## Reproduce a controlled failure

```sh
python -m migrationwitness run privileges_bad --pg-bin /usr/lib/postgresql/17/bin --output runs/acl-bad
python -m migrationwitness run privileges_safe --pg-bin /usr/lib/postgresql/17/bin --output runs/acl-safe
python -m migrationwitness run index_cancel --pg-bin /usr/lib/postgresql/17/bin --output runs/index-interrupted
python -m migrationwitness run examples/add-column.json --pg-bin /usr/lib/postgresql/17/bin --output runs/custom
```

`privileges_bad` intentionally recreates a table without restoring SELECT for an existing role: migration SQL succeeds, but the old reader gets SQLSTATE 42501. `index_cancel` waits until PostgreSQL reports the concurrent-index lock barrier, cancels that connection and records the invalid index before cleanup. These demonstrate expected native behaviors. They are not newly discovered PostgreSQL bugs.

CLI exit codes: **0** contract PASS; **2** contract FAIL/INCONCLUSIVE or evidence verification failure; **1** invalid input, environment or framework ERROR. Broken controls intentionally return 2. `control_agreement` records whether an intentionally broken/fixed fixture behaved as expected; it is not a correctness verdict for a real migration.

## Caller cases and API

`examples/*.json` are editable. SQL is trusted executable input. The built-in fixture is `public.business(id integer PRIMARY KEY, value text NOT NULL)` with 100 deterministic rows. A custom case may supply `setup_sql`, exactly one of `migration_sql` or `migration_argv`, optional `concurrent_workload`, and boolean SQL `assertions`. Assertions must return one boolean cell; ambiguous results are INCONCLUSIVE. Leaving a transaction open fails the commit boundary; final business rows and assertions use separate connections. Setup SQL must not alter the fixture's initial business rows unless a changed-data failure is intended.

```python
from pathlib import Path
from migrationwitness.runner import run
result = run('index_recover', Path('/usr/lib/postgresql/17/bin'), Path('runs/recovered'))
assert result['outcome'] == 'PASS'
```

For an external migration command, provide a literal argv list in a reviewed JSON case and explicitly pass `--allow-trusted-command`. Its environment points to the newly created cluster through PostgreSQL environment variables. Commands must honor those variables. No shell expansion is performed. A trusted command can still ignore that connection and access other resources: review it and run inside an isolated lab. This is not an OS sandbox.

## Evidence and limitations

- Reports retain SQL text, synthetic raw values, outcomes, SQLSTATE, transaction status, query elapsed time, `pg_locks`, `pg_stat_activity`, blocker PIDs and before/after definitions/ACLs. Caller scripts could expose private data or secrets: never supply them.
- SHA-256 manifests detect changed or missing files relative to a supplied manifest. They are not signatures and do not prove who generated evidence. Keep the manifest/hash through a trusted channel.
- Bounded selected controls do not establish production false-positive/false-negative rates, arbitrary schedule coverage, or migration safety under all workloads. Sampling can miss short waits. Backfill controls exercise an explicit deterministic interleaving, not all possible concurrent executions.
- Trusted custom SQL can change timeouts, allocate large results or create descendants. There is no hard CPU/memory/disk quota or security isolation. Built-in workloads have fixed budgets; arbitrary trusted scripts do not have a hard whole-run deadline. POSIX ordinary process groups are cleaned up; detached descendants and Windows descendants are not contained.
- A final-state check does not prove full transactional isolation, linearizability, replication/failover correctness or preservation of all object metadata.
- The original environments of reported upstream issues are not fully specified. Exact status and actual reproductions are distinguished in [UPSTREAM_VALIDATION.md](docs/UPSTREAM_VALIDATION.md).
- Existing tools already implement schema validation, hazards, privilege diffs, recovery and client-version mechanisms. The value here is an engine-independent runtime witness bundle; no new algorithm, scientific innovation or superiority claim. See [COMPETITORS.md](docs/COMPETITORS.md).

## Tests

```sh
python -m pip install pytest==9.0.3
MW_PG_BIN=/usr/lib/postgresql/17/bin python -m pytest -q
```

Without `MW_PG_BIN`, real-database tests are skipped and must be reported NOT RUN. [EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md) defines selected controls before execution. [ARCHITECTURE.md](docs/ARCHITECTURE.md), [SECURITY.md](docs/SECURITY.md), [FINAL_REPORT.md](FINAL_REPORT.md) and [RESUME.md](RESUME.md) describe the delivery and evidence locations.

MIT licensed. Third-party tools and PostgreSQL are not bundled; their own licenses apply.
