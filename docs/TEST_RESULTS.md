# Historical baseline validation results

This is the original pre-supplement acceptance, preserved as historical documentation. Current results supersede its pg-osc NOT RUN and suite counts: [CROSS_VERSION_RESULTS.md](../CROSS_VERSION_RESULTS.md) and [PG_OSC_197_RESULTS.md](../PG_OSC_197_RESULTS.md). The72-case study was not rerun on the final candidate.

Exact command/output/exit status records are in the external evidence directory. See final delivery report for clean-install final results. Counts below describe executed scopes and do not turn skipped tests into PASS.

- Actual Linux PostgreSQL16.15 and17.11 selected controls:72/72 agreement (12×2×3 fresh clusters);48 positive/fixed runs PASS,24 deliberately broken runs FAIL,0 unexpected ERROR/INCONCLUSIVE. All72 evidence manifests verified. Within this fixed set:0 false alarms on48 safe controls,0 misses on24 injected broken controls. These are development controls, not independent production error-rate estimates.
- Independent reviewer PG16 run before the last encoding regression:37 passed,1 root-only skip; new startup-evidence-failure regression separately passed. Review raw records and defects were retained.
- Windows11 build26200/Python3.13.0 fresh venv:20 passed,19 skipped (no native PG binaries; POSIX-only descendant check). CLI list and Unicode evidence/verification actually run. Native Windows PostgreSQL lifecycle NOT RUN and explicitly unsupported in this candidate.
- Clean Git checkout/venv Linux rerun at implementation commit669062b: PG16.15 **38 passed,1 root-only skip**; PG17.11 **38 passed,1 root-only skip**. Additional installed-package API/CLI smoke runs execute outside the checkout and verify the imported path is site-packages.
- Hash-locked acceptance dependencies were additionally installed in fresh Windows3.13 and Alpine3.14 venvs. The Windows clean-checkout route repeated20 passed/19 skipped and verified a copied Linux evidence bundle. The Linux locked route ran the editable additive JSON case and verified its report. The opt-in official-psql JSON case also actually passed while60 controlled mutations ran.
- Initial Windows command-output Unicode test failed (GBK output decoded as UTF8); fixed Python subprocess UTF8 environment and added raw base64 capture/decode-error marker. Original failure preserved in `windows-acceptance.json`; successful rerun in `windows-acceptance-v2.json`.
- Real pgroll related #1013 controlled lock timeout/retry path on both majors; quiet retry success. Real pg-schema-diff #316 default-plan protection and explicitly unsafe partial apply on both majors. Atlas Community actual dry-run/apply on17. pg-osc actual migration NOT RUN due pinned native dependency build failure.

## Observer measurements

Six alternating-order PG17 concurrent-DML runs,100 seed rows/60 single-statement mutations each. Observer off/on each n=3. Median whole-run elapsed (includes initdb/start/stop) off0.918061s vs on0.889220s. Median sum of60 workload SQL durations off0.040009s vs on0.042591s. Each run PASS. Full six raw values and evidence byte counts are in `linux/acceptance/initial-72/summary.json`.

The whole-run difference is dominated by environment/scheduling noise; it is not evidence of a speedup. The SQL-time medians are a bounded measurement, not production overhead. Both modes retain baseline metadata/final ledger; “off” disables only two extra runtime lock/activity snapshots. No CPU/memory peak profiling or production latency distribution was measured.

## Known gaps

No native Windows PostgreSQL execution, Docker-daemon execution, PG18/19, replication/failover, true production workload, arbitrary transaction schedule, real pg-osc run, exhaustive metadata coverage or stable production accuracy estimate. No CI execution on GitHub (no remote repository authorized). Raw resource budgets apply to selected controls; custom trusted SQL has no hard whole-run or memory cap.
