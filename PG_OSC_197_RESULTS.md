# Actual pg-osc #197 permission validation

Date:2026-10-18 (Asia/Hong_Kong). **REPRODUCED under the controlled fixture below**, on PostgreSQL16.15 and17.11. This is a known upstream report, not a first discovery or a claim about every pg-osc configuration. [Upstream issue197](https://github.com/shayonj/pg-osc/issues/197) remains open; it does not specify its original versions/roles/schema, so environment identity with the reporter is UNKNOWN.

## Fixed environment and unmodified upstream

pg-osc0.9.10 release commit `0a439a873f9df1bf474cfe13060a115278b94658`; Ruby3.3.0 commit `5124f9ac7513eb590c37717337c430cb93caa151`; Bundler2.3.24; original Gemfile.lock and runtime versions retained. See [PG_OSC_PROVENANCE.json](PG_OSC_PROVENANCE.json) and [reproduction procedure](env/PG_OSC_REPRODUCTION.md). All52 source archive files, including the lockfile, were byte-verified unchanged after installation. No upstream patch or modified copy query.

Docker client29.8.0 was checked first, but the daemon pipe was absent; official Docker execution is NOT RUN. A new prefix inside the existing dedicated MigrationWitness Alpine3.24.2 WSL lab holds the separately compiled Ruby. The initial pinned pg_query4.2.3 build failed under GCC15's C23 default; selecting GNU C11 via its supported `--with-cflags=-std=gnu11` build option succeeded. Dependency versions, source code and assertions were not changed. Earlier Ruby3.4/Alpine failures and this initial build failure remain in separate raw logs.

## Fixture, independent checks and result

Each run creates a fresh private cluster and disposable database. `migration_user` is a LOGIN owner without superuser/createdb/createrole privileges; it has schema CREATE. `business_user` is a separate restricted LOGIN role with explicit SELECT,INSERT,UPDATE on `public.business`, no DELETE or inherited/default table grants. Initial data is100 synthetic integer rows `(id,g*10)`.

Before/after snapshots include `pg_class` OID/OWNER/ACL, `information_schema.role_table_grants`, `has_table_privilege`, type and every business row. Actual SELECT/INSERT/UPDATE/DELETE are run through independent authenticated business-user connections, asserting session_user=current_user=business_user; probe writes rollback. Catalog checks are not substituted for actual SQL permissions. The actual migration changes value integer->bigint and uses pg-osc's real copy/replay/shadow swap; no `--kill-backends`.

| Platform | Fresh pg-osc runs | Tool exit | Completed bigint/OID swap | SELECT/INSERT/UPDATE afterward | Native ALTER controls |
| --- | --- | --- | --- | --- | --- |
| PG16.15 |3 |0 each |3/3 |42501 for all three,3/3 runs |3/3 PASS, original grants/OID retained |
| PG17.11 |3 |0 each |3/3 |42501 for all three,3/3 runs |3/3 PASS, original grants/OID retained |

All runs retained the intended owner and exact100 business rows. pg-osc changed the logical table OID (observed16387->16405 in these clusters); the new table ACL was NULL and its business privilege bits changed `[true,true,true,false]` to `[false,false,false,false]`. The retained original table still held the old explicit grant. Native ALTER preserved OID and all three grants. Forbidden DELETE remained forbidden in both arms.

The independent business permission invariant therefore reports **FAIL** for all six completed pg-osc migrations despite tool exit0. After that untouched-tool evidence was captured, an explicit caller `GRANT SELECT,INSERT,UPDATE` restored the three actual operations in all six cases; this is a tested local mitigation, not an upstream fix or a guarantee for other grants/roles.

## Evidence and reproducibility

[scripts/pgosc_197_probe.py](scripts/pgosc_197_probe.py) uses MigrationWitness's private Cluster, SQL capture, Evidence, SHA256 sealing and HTML/Markdown renderer. It reports actual tool completion separately from invariant failure. Its exit0 means the investigation completed; inspect `outcome` for correctness. Main CLI0/2/1 semantics remain unchanged.

[examples/pgosc-197-summary.json](examples/pgosc-197-summary.json) is explicitly derived from the twelve real runs, not synthetic execution output. It excludes raw hostnames, stdout and absolute local paths. Original complete logs/input/SQLSTATE events and sealed reports stay private in `E:/final/migrationwitness-final-evidence-20261018/linux/runs/pg{16,17}-{pgosc,native}-r{0,1,2}/`. Failed builds are under `linux/logs/`; previous acceptance evidence remains untouched.

These are small permission-focused fixtures, without concurrent business writes during the pg-osc run. Concurrent INSERT/UPDATE/DELETE and lock/interruption behavior are separately tested by the native core suite. No workload-level pg-osc accuracy, arbitrary ACL preservation, production rate or semantic migration guarantee is inferred.
