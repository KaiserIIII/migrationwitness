# MigrationWitness bounded design (before experiments)

Date: 2026-10-18. Engineering exercise, no research novelty claim.

Three options were considered: (1) static SQL linting (already mature, cannot observe concurrent histories); (2) another migration engine (out of scope); (3) an ephemeral PostgreSQL experiment runner with independent business and catalog oracles. Choose (3) only if the pilot demonstrates a real runtime gap against a runnable migration-tool baseline. A failure of native PostgreSQL to meet a deliberately unsafe contract is NOT a PostgreSQL bug.

## Value gate

Before implementing the reusable runner, run a native interrupted concurrent index and a migration-tool plan/apply baseline. Require actual evidence that successful schema planning/application alone does not establish a declared runtime/business/privilege invariant. Compare fairly with documented hazards and existing checks. Product value is a reproducible cross-tool witness, not a new detection algorithm. If the baseline already verifies all target contracts, stop with NO-GO and preserve the experiment package.

## Architecture if gate passes

Python, psycopg, official PostgreSQL binaries. Cluster lifecycle owns a newly created private directory and its processes; no existing DSN or production connection argument. JSON scenarios supply trusted SQL and explicitly opted-in external argv (no shell). Concurrent actors use separate connections; observation barriers have deadlines, not assumed sleep ordering. Raw SQL outcomes, SQLSTATE, transaction status, pg_locks, pg_stat_activity, index/constraint/ACL definitions and acknowledged business operations are retained before cleanup. A business ledger is independently replayed in Python and compared row by row. Reports separate invariant outcome from expected broken/fixed control and environment/framework failures.

CLI: list scenarios, run on a local PostgreSQL binary directory, verify evidence, render existing evidence. API returns the same structured result. Windows pure-core/CLI verification is distinct from native Linux PostgreSQL execution; native Windows PostgreSQL execution must not be implied by WSL execution.

## Trust and scope

Only disposable synthetic databases. SQL/commands are executable trusted inputs, not sandboxed data. No arbitrary remote DSNs. Selected controls have bounded rows/workers, SQL timeouts and barrier deadlines; external commands have a capture/timeout budget. The delivered prototype has no hard whole-scenario deadline for arbitrary trusted SQL, which can override database settings (a limitation of the initial outer-deadline design intent, documented before final claims). No arbitrary scheduler, distributed/replication/failover oracle or production accuracy claim. No credentials or host environment dumps in reports. Failure evidence is append-only per fresh run directory. No remote publishing.
