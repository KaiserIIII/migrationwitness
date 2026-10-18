# Competitor comparison and tested boundaries

MigrationWitness is a disposable runtime-contract harness alongside migration engines. It does not generate or optimize migration plans. Individual checks are not novel, and comparable workflows can be scripted using pgbench, catalog queries, Atlas assertions and existing test tools.

| Tool and fixed source | Existing capability credited | Actual evidence and boundary |
| --- | --- | --- |
| pg-osc0.9.10 /0a439a873f9df1bf474cfe13060a115278b94658 | Real shadow table/copy/replay/swap, short lock windows, pgbench examples, FK/index support | Genuine integer->bigint swap on16/17; completed commands lose restricted role's explicit grants in the selected fixture. Six native ALTER controls preserve them. See [actual results](PG_OSC_197_RESULTS.md). |
| pgroll0.16.3 /777a5350e09012b29d26b9611122046d8a96fc1c | Old/new schemas, triggers/backfill, lock retry, rollback, some invalid-index recovery | Prior actual16/17 controlled held-writer timeout/retry path matches#1013 symptom; observed invalid index, rollback and successful quiet retry. Not the reporter's unspecified workload. |
| pg-schema-diff1.0.9 /9ada4710c28718312557c84cca1be4b2557eed54 | Hazard reporting, temporary-DB plan validation, invalid-index/ACL diffing, constraints/timeouts | Prior actual#316 on16/17: default validation DID protect live DB. Explicitly disabled validation/allowed hazards caused partial apply. Arbitrary faulty caller backfill is outside schema validation guarantees. |
| Atlas Community1.3.0 /9a6bc601212130aaaefcbc8dd36c710baf9716ff | Versioned migrations/checksums/dry runs; ecosystem assertions/exec can express custom tests | Prior actual Apache Community hash/dry-run/apply17. Lossy caller UPDATE exited0 but failed independent business invariant; no Atlas defect alleged. Commercial standard binary/Pro was not used. |
| PostgreSQL16.15/17.11 native | Transaction controls, pgbench, SQLSTATE, lock/activity/catalog views and documented index recovery | Actual ALTER/index/role/constraint controls. Invalid indexes after cancellation are documented native behavior, not new PG bugs. |

The increment is one engine-independent experiment envelope: private cluster, intended-operation ledger, observed interruption phase, actual old-role/client probe, catalog/SQLSTATE timeline and portable sealed reports. It can reveal a declared application contract failure even when schema execution completes, while crediting tools' existing warnings and default protections. It does not prove superiority or replace their safety checks.

All upstream issues remain known prior reports. [docs/UPSTREAM_VALIDATION.md](docs/UPSTREAM_VALIDATION.md) distinguishes current supplemental pg-osc evidence from historical runs. Atlas commercial distribution has restrictive competitive-benchmark terms; only Apache source Community was used. No scientific innovation, new detection algorithm or production detection rate is claimed.
