# Local handoff

Decision: **READY_WITH_LIMITATIONS**, local source prototype only. No remote repository, push, Release, package publication or production connection.

Start with README.md, docs/EXPERIMENT_PROTOCOL.md and docs/UPSTREAM_VALIDATION.md. Runtime implementation was frozen at669062b9def25a338d95b21b3541d70196881970. Later local commit adds delivery documentation, provenance locks and reproducible experiment adapters; no product runtime algorithm change.

Source: `E:/final/migrationwitness-20261018`. External evidence/artifacts: `E:/final/migrationwitness-evidence-20261018`. Dedicated WSL distro: `MigrationWitness-20261018`, lab root `/opt/migrationwitness`. Other projects were not modified.

Install into a clean matching interpreter. Default `pip install .` resolves pinned primary dependencies; exact accepted Windows3.13/Alpine3.14 wheel locks include transitive dependencies and hashes. For that matching platform:

```sh
python -m pip install --require-hashes -r requirements-py314-alpine.lock
python -m pip install --no-build-isolation --no-deps .
```

Use the Windows lock in a Windows3.13 venv. Other platforms/Python versions need their own reviewed lock and acceptance; do not assume these wheel hashes are universal. Official source commits/licenses for Python dependencies are included in `DEPENDENCY_PROVENANCE.json`. The runtime package itself is original source, not a published PyPI artifact.

Run `python -m migrationwitness list`, then one of the README commands on a newly created output directory as an unprivileged Linux user. Use `scripts/acceptance.py` for12 selected controls. `scripts/schema_diff_probe.py` and `scripts/upstream_probe.py` rerun actual trusted tool comparisons with explicit binary paths; install reviewed pinned tools separately. These adapters record expected broken-tool paths, so their script exit code concerns probe execution; inspect JSON/catalog evidence for migration correctness. A failed recipe is not a reproduced upstream bug.

Reports: `result.json`, `events.jsonl` event sequence references, `business-ledger.json`, `postgres-log.json`, `report.html`, `report.md`, `manifest.json`. Run `python -m migrationwitness verify PATH` on Linux or Windows after copying evidence. Keep trusted manifest hashes externally. The raw SQL/values and command argv are not automatically redacted.

Recovery: use the final external `migrationwitness.bundle` with `git clone migrationwitness.bundle restored`; compare HEAD/tree with `DELIVERY.json`, inspect PUBLIC_FILES.json and run tests. The source ZIP is a Git-archive of that final tree, excluding runtime/evidence/binaries/caches. Preserve the evidence directory separately; source archive is not a replacement for raw logs. The WSL lab is retained; all owned experiment databases are stopped/removed except preserved stopped pilot data directories in the dedicated lab. Do not reset Docker or remove unrelated resources.

No further feature development is needed for this delivery. The single highest-value remaining validation is a genuine pg-osc#197 run in a compatible pinned upstream Ruby environment. Native Windows PG is unsupported; production/failover validation remains outside accepted scope.
