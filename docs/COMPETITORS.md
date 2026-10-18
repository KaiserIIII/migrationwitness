# Existing tools and incremental scope

Official pinned sources and licenses were actually read; raw sources/API responses and hash manifests are preserved in the external `competitors` dossier.

| Tool | Existing capabilities credited | Actual lab scope |
| --- | --- | --- |
| [pgroll](https://github.com/xataio/pgroll/tree/777a5350e09012b29d26b9611122046d8a96fc1c) | Version schemas/old-new clients, triggers/backfill, lock retry, rollback, some invalid unique-index recovery | Built exact source; actual held-writer index migration and lock evidence. #1013 qualification in upstream report. |
| [pg-schema-diff](https://github.com/stripe/pg-schema-diff/tree/9ada4710c28718312557c84cca1be4b2557eed54) | Plan hazards, scratch DB validation, privilege diffs, invalid-index handling, timeouts, phased constraints | Exact v1.0.9 actual plan/default refusal/explicit unsafe apply on both majors; caller backfill contrast. |
| [Atlas Community](https://github.com/ariga/atlas/tree/9a6bc601212130aaaefcbc8dd36c710baf9716ff) | Versioned migrations, checksums, dry runs; ecosystem supports assertions/external programs | Apache source community build, actual hash/dry-run/apply. No Pro/login/standard MSA binary. |
| [pg-osc](https://github.com/shayonj/pg-osc/tree/042c6eefd7e5eb59044fd99cf1c42d26ddf022cf) | Shadow table/copy/replay/swap, explicit lock retries and pgbench concurrency examples | Pinned source/gem read, native dependency build attempts; see exact execution status in upstream report. |
| [PostgreSQL](https://www.postgresql.org/docs/17/sql-createindex.html) | pgbench, lock/activity catalogs, SQLSTATE, transaction controls, invalid-index recovery documented | Real16.15/17.11 native controls, no attempt to replace these facilities. |

The runtime witness unifies a controlled workload ledger, observed fault barrier, old-client/role contract and raw timeline across engines. Individual checks are not new; an experienced engineer can script them. This is practical integration value rather than scientific novelty or a new migration method. No superiority or exhaustive survey claim. Atlas custom assertions/exec can express comparable workflows, so it would be inaccurate to claim existing systems cannot do this.

Fair comparison: pg-schema-diff's default validation DID catch #316; disabling it explicitly was an unsafe control. Both pg-schema-diff and Atlas execute deliberately lossy user SQL only when their relevant authorization/options permit it. Their schemas can be correct while application business invariants fail; that is outside arbitrary semantic correctness guarantees and is not presented as a tool bug. Existing hazards are printed and retained.

Atlas commercial standard distribution terms restrict competitive benchmarking; only Apache Community source was built/run. Official binary download returned403; source fallback was legal and successful. Current CE docs and pinned v1.3.0 source differ about lint capabilities; no unsupported capability comparison is inferred from that discrepancy.
