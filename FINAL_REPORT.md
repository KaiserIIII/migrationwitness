# MigrationWitness engineering delivery

**READY_WITH_LIMITATIONS.** A working local prototype and real PostgreSQL evidence have been delivered. This is an experimental engineering tool, not a migration engine, scientific result or production reliability certificate. No public repository or package was created.

## What actually runs

- Private disposable Linux PostgreSQL clusters and deterministic concurrent INSERT/UPDATE/DELETE workload with independently replayed acknowledged-operation ledger.
- Twelve predefined long-transaction, lock timeout, old/new client, canceled concurrent index, backfill, FK/unique, role-privilege and partial-recovery controls.
- Trusted editable JSON/SQL scenarios and explicit opt-in literal external command argv; independent committed-state assertions, SQLSTATE/transaction status, blocker/activity/lock and catalog evidence.
- CLI/Python API and JSON/HTML/Markdown reports with per-file SHA256 verification. Windows installs and runs offline evidence/CLI operations; actual DB lifecycle uses Linux/WSL.

## Actual verification

| Scope | Actual result |
| --- | --- |
| Fresh isolated PG16.15 +17.11 selected controls |72/72 expected-control agreement:48 safe PASS,24 deliberately broken FAIL; all hashes valid |
| Clean Git checkout + fresh Linux venv, PG16 |38 passed,1 root-only skip |
| Same clean environment, PG17 |38 passed,1 root-only skip |
| Root initdb refusal |1 passed separately |
| Fresh Windows11/Python3.13 venv |20 passed,19 explicitly skipped/NOT RUN; offline CLI/Unicode exercised |
| Installed Linux package outside source checkout |6 actual API cases across both majors and2 CLI good runs; site-packages path asserted |
| Independent review |4 reproduced defects fixed and independently rechecked; no unresolved reviewed P1/P2 |

The72 controls are selected development fixtures, not production accuracy data. Their0/48 false-alarm and0/24 miss counts are scoped to those injected controls only. Six observer measurements and raw times are in docs/TEST_RESULTS.md; no production overhead claim. In-process measured core statement coverage91% excludes CLI subprocess coverage and unsupported Windows-native branches; coverage alone does not establish correctness.

## Real upstream results

- pgroll0.16.3 exact source: related#1013 held-writer/lock-timeout/retry “index already exists” path reproduced on both majors. Observed invalid index before failure, rollback cleanup, then successful quiet retry. Original issue workload/version identity is not claimed.
- pg-schema-diff1.0.9 exact source: #316 reproduced on both majors. **Default validation protects the live DB**. Only an explicitly unsafe disabled-validation/allowed-hazards control partially applies before failure.
- Atlas Community1.3.0 Apache source: actual checksumming, dry-run and apply on17. Deliberately lossy caller backfill exited0 and failed the independent business invariant. This is caller SQL, not an Atlas bug. Comparable pg-schema-diff caller-UPDATE test first refused IS_USER_GENERATED, then executed only after explicit hazard authorization.
- pg-osc#197: actual migration **NOT RUN** due pinned native dependency build limitations. Inspected source plus native ACL-loss controls are labeled separately and do not establish a pg-osc reproduction.

## Incremental value and limits

Mature tools already provide schema hazards, scratch validation, ACL diffs, old/new schemas, retries, catalog checks and customizable assertions. MigrationWitness's practical scope is a common disposable workload/fault/committed-state witness with linked raw evidence across tools. No individual check is claimed new, and custom Atlas/pgbench workflows can implement comparable behavior.

Native Windows PostgreSQL, pg-osc, Docker daemon, other PG versions, production/replication/failover, arbitrary schedules and exhaustive object metadata remain unvalidated. Trusted SQL/commands are not sandboxed and can ignore timeouts or change resources; no hard memory/disk/CPU quota or universal descendant isolation. Full arbitrary-script wall deadlines are not guaranteed. Hashes are unsigned. README and SECURITY.md state these limits.

## Artifacts and freeze

`PUBLIC_FILES.json` is the reviewed source inventory. `DEPENDENCY_PROVENANCE.json` and acceptance locks capture dependency sources/licenses/commits and immutable wheel hashes. Raw original experimental JSON/logs, official metadata, failed recipe/build attempts and independent review are external, never inserted into the MIT source ZIP. Reproduction steps are in HANDOFF.md and env/README.md.

Final full Git SHA/tree, clean state, source ZIP/Git Bundle hashes and backup-restore verification are recorded in external `E:/final/migrationwitness-evidence-20261018/DELIVERY.json` because a commit cannot contain its own final SHA. Runtime code is unchanged from the tested implementation commit recorded there. No remote exists. Stop feature work after this local freeze.
