# Local handoff

**PUBLICATION_READY — source experimental edition only.** No remote repository, push, Release, package publication or production connection. Publishing is pending user authorization; see [PUBLISHING.md](PUBLISHING.md).

Read [README.md](README.md), [README_ZH.md](README_ZH.md), [CROSS_VERSION_RESULTS.md](CROSS_VERSION_RESULTS.md), [PG_OSC_197_RESULTS.md](PG_OSC_197_RESULTS.md) and [PUBLICATION_READINESS.md](PUBLICATION_READINESS.md). Baseline c9edadf is preserved; accepted runtime/test fixes are commit445e7ff18c529d51e73aa6962138f3f10a838b5f. The final candidate adds documentation, CI and a reproduction adapter, with no further core change. Final SHA/tree and artifact hashes are external because a commit cannot contain its own hash.

## Install and reproduce

Use a fresh matching interpreter/venv and official PostgreSQL binaries in an isolated Linux environment as a non-root user. Exact accepted Windows3.13 and Alpine3.14 dependency locks are platform-specific, not universal wheel hashes:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes --only-binary=:all: -r requirements-py314-alpine.lock
python -m pip install --no-build-isolation --no-deps .
python -m migrationwitness list
MW_PG_BIN=/usr/libexec/postgresql17 python -m pytest -q
python -m migrationwitness run concurrent_dml --pg-bin /usr/libexec/postgresql17 --output runs/new-dml
python -m migrationwitness verify runs/new-dml
```

On Windows3.13 use `requirements-py313-windows.lock` and `.venv/Scripts/python.exe`. Windows supports offline commands/reports; native Windows DB execution is refused. For general installs on other platforms `pip install .` resolves pinned primary dependencies, but those environments have not been accepted. Hash-locked installs retain install reports/freeze in the external acceptance evidence.

Every evidence output directory must be new. CLI0=PASS,2=FAIL/INCONCLUSIVE or verification failure,1=invalid input/environment/framework ERROR. Broken controls should return2. `scripts/acceptance.py` runs12 native controls; the earlier72-run experiment is historical. The current full small suite passed40/1 on both PG majors. See [env/README.md](env/README.md) for the dedicated environment.

`scripts/schema_diff_probe.py` and `scripts/upstream_probe.py` are optional trusted-tool adapters with explicit binary paths. [env/PG_OSC_REPRODUCTION.md](env/PG_OSC_REPRODUCTION.md) gives compatible pinned legacy Ruby and the actual `scripts/pgosc_197_probe.py` commands. Probe exit0 means investigation completed, not migration correctness: inspect outcome/catalog/role evidence. `examples/pgosc-197-summary.json` is derived evidence, not editable input.

## Evidence and recovery

Reports include result.json, ordered events.jsonl, optional business-ledger.json, postgres-log.json, report.html, report.md and manifest.json. Offline `verify` checks integrity relative to a supplied unsigned manifest, not authenticity. Raw caller SQL/values/argv are not automatically redacted. Public archives contain no raw environment/stdout or third-party binary.

Source: `E:/final/migrationwitness-20261018`. New private evidence/artifacts: `E:/final/migrationwitness-final-evidence-20261018`; original evidence `E:/final/migrationwitness-evidence-20261018` is untouched. Dedicated WSL `MigrationWitness-20261018`, supplemental prefix `/opt/migrationwitness-final-20261018`. All experiment-owned active clusters have been stopped/cleaned; retain the lab for recovery, not production use.

Read external DELIVERY.json and SHA256SUMS. Restore `migrationwitness-source-experiment.bundle` using `git clone BUNDLE new-restored-directory`; compare final HEAD/tree, run `git fsck --full` and independently verify each PUBLIC_FILES.json file hash. The ZIP is a Git archive of exactly that public tree. Manifest self-hash is intentionally null; external tree/archive hashes bind it. Raw evidence is retained separately and is not for automatic publication. Baseline backup and original freeze packages remain separate.

Hosted CI/Docker lifecycle is NOT RUN; workflow is prepared and local Windows/static checks passed. CI quotas are not product hard isolation. No hard resource/descendant sandbox, production accuracy, exhaustive metadata, replication/failover or arbitrary-schedule guarantee. Stop features here. Highest-value next action is hosted CI after separately authorized publication, with only real CI/compatibility fixes if needed.
