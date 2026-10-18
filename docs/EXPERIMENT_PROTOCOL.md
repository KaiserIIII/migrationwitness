# Preregistered acceptance protocol

Written before running database experiments. PG16 and PG17, private ephemeral clusters, <= 2 concurrent workload writers plus two compatibility readers, <= 1,000 initial business rows, <= 100 acknowledged mutation transactions per scenario, statement_timeout <= 10s, lock_timeout <= 2s, observation barrier <= 8s, each scenario <= 60s. Index interruption uses a catalog-visible wait barrier, not a large data download. No metric claims beyond these selected controls. A changed protocol gets a new revision and preserves the failed run.

| ID | Perturbation / control | Contract and independent oracle |
| --- | --- | --- |
| lock_timeout | Open reader transaction blocks ALTER; short lock timeout | Observe ungranted relation lock + blocker PID while active; SQLSTATE 55P03, no column afterward, transaction rollback recoverable. Native expected behavior. |
| concurrent_dml | INSERT/UPDATE/DELETE while additive DDL | Every acknowledged txn reflected in independent Python final-row model; missing/extra/value differences fail. All client errors reported. |
| old_new_clients_safe | Add new column while old/new explicit projections run | Both query contracts succeed; ledger exact. |
| old_new_clients_break | Rename old column while old client still uses it | Old contract must fail with 42703; correctly report contract violation even if DDL succeeds. |
| index_cancel | Hold writer, begin CREATE INDEX CONCURRENTLY, observe catalog/wait, cancel owned connection | SQLSTATE 57014; retain invalid index; declared all-indexes-valid contract FAIL. Record native partial-success state, not upstream bug. |
| index_recover | Repeat cancellation then explicitly drop/recreate | Same intermediate evidence; final valid index and ledger PASS. |
| backfill_bad | Copy old values, commit intervening writes, apply stale backfill | New representation must equal current old value; deterministic stale overwrite must FAIL. No claim about an actual tool unless run through it. |
| backfill_safe | Same intervening writes; UPDATE target from current source in DB | New representation equals current value; ledger PASS. |
| constraints_safe | Add FK NOT VALID then VALIDATE; unique index | Catalog validated FK/valid unique index; real violating inserts rejected 23503 / 23505 and transaction rolled back; existing data intact. |
| privileges_bad | Recreate object without restoring SELECT grant | Non-owner SET ROLE query fails 42501 despite identical columns/data and successful migration; catalog ACL evidence. |
| privileges_safe | Same recreation, restore explicit grant | Non-owner query succeeds; object definition and data checked. |
| partial_recovery | Commit additive change then cancel second statement; resume idempotently | Capture partial columns/aborted transaction; after explicit resume target definition exact, no invalid indexes, data intact. |

For native scenarios expected FAIL controls are index_cancel, old_new_clients_break, backfill_bad, privileges_bad. All other controls expect PASS. INCONCLUSIVE is never counted as a successful control. Harness errors are ERROR. Actual tool issue reproductions are separately labeled REPRODUCED / NOT REPRODUCED under stated conditions / NOT RUN / BLOCKED, never inferred from these constructed controls.

Evaluation: run all controls on both majors, then repeat in newly initialized clusters at least twice; record exact numerator/denominator of selected-control agreement, per-run elapsed time and workload/observer SQL timing. Compare observer-on/off under the same bounded workload in alternating order; report variation and scheduling limitations, not production overhead. Safety baseline: run at least one tool's actual plan validation and contrast its declared hazards with runtime oracles.
