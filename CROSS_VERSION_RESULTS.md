# Supplemental cross-version acceptance

Baseline `c9edadf53dcfa83c760ee2055adb1c659db34125` preserved in a verified Git Bundle. Current runtime fix commit `445e7ff18c529d51e73aa6962138f3f10a838b5f` was installed from a fresh local clone into a new hash-locked Linux venv. Tests were copied outside the checkout and imports asserted to resolve to site-packages, avoiding source-shadowed installation success.

| Executed scope | Python / PostgreSQL | Actual result |
| --- | --- | --- |
| Full installed-package suite, non-root Linux |3.14.8 /16.15 |40 passed,1 root-only skip,17.00s |
| Full installed-package suite, non-root Linux |3.14.8 /17.11 |40 passed,1 root-only skip,16.87s |
| Root initdb refusal, separate fresh install check |3.14.8 /17.11 |1 passed |
| Independent reviewer full suite |3.14.8 /17.11 |40 passed,1 root-only skip |
| Fresh Windows hash-locked install and prepared workflow steps |3.13.0 /no native PG |21 passed,20 skipped; installed offline CLI passed |
| Real pg-osc#197 and native ALTER |Ruby3.3.0 /16.15,17.11 |6 reproduced permission-contract FAIL,6 native-control PASS |

Windows skips are19 database-dependent tests and1 POSIX-only process-group test. Native Windows PostgreSQL is NOT RUN/unsupported; WSL results are Linux results. The workflow's GitHub-hosted Windows/Linux/Docker execution is **NOT RUN**, not local PASS. Dependencies/action SHAs and local preparation checks are described in [CI_PREPARATION.md](docs/CI_PREPARATION.md).

## Covered contracts

Both full database suites execute all twelve native controls: concurrent acknowledged INSERT/UPDATE/DELETE ledger; additive migration/old-new clients; deliberately incompatible old-client projection; long-transaction blocking and55P03 timeout;57014 concurrent-index cancel/invalid residual catalog; explicit index recovery; stale and corrected backfill interleaving; actual FK/unique rejection; bad/good role grant preservation; partial commit/aborted transaction/resume. They also exercise API/CLI0/2/1, Unicode evidence, HTML/Markdown escaping, hash tamper rejection and owned cluster shutdown/removal, including an evidence-write failure during startup.

The previous72-case stability experiment remains a historical baseline result, not a new run on this candidate. Current full regressions cover both majors after the fixes; no extra unrelated coverage tests were added.

## Preserved failures and fixes

- Independent baseline review reproduced a false PASS for assertion `SELECT TRUE; SELECT FALSE`; only the first result was read. A real-PG red test confirmed PASS. The minimal fix retains all result sets/column/status evidence and requires exactly one result set for boolean assertions, otherwise INCONCLUSIVE. Existing first-result `rows` stays compatible.
- A crafted unsealed report outcome injected raw HTML into the Markdown heading. A red regression reproduced it; only known enum labels are now emitted in the heading, otherwise UNKNOWN. Detailed values remain escaped.
- The prior100ms child-cleanup regression could kill the interpreter before spawning a child. Independent probes proved that precondition failure. A5s startup budget plus `not timed_out` retains the no-late-file and descendants-cleaned assertions. The dedicated timeout test still tests real timeout separately.

Original baseline failure XML/logs, new red/green tests, core hashes and independent re-review are external `review/` and `linux/logs/`. They were not replaced with final successes.

In-process installed-package statement coverage is85% overall in this run, including CLI modules measured as0 because pytest CLI tests launch subprocesses without coverage instrumentation. That limitation does not mean CLI was not run; CLI behavior has actual subprocess assertions and separate installed-CLI checks. No coverage number establishes system correctness.

Resource limits are finite built-in workloads/timeouts; the product has no hard CPU/memory/disk quota or universal whole-script deadline. Production false-positive/false-negative rates, replication/failover, arbitrary schedules and versions beyond the tested matrix remain UNKNOWN/NOT RUN.
