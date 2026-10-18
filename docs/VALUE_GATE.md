# Preimplementation value gate: proceed with bounded engineering prototype

Actual pilots, 2026-10-18, before reusable production code:

- PostgreSQL 16.15 and 17.11 each retained an invalid index after a catalog-observed concurrent-index wait was canceled (57014); explicit drop/recreate restored validity. Separate table-replacement controls preserved rows but lost a SELECT grant (42501). These are expected native behaviors, not newly discovered bugs.
- pg-schema-diff v1.0.9 / 9ada4710c28718312557c84cca1be4b2557eed54 actually rejected #316's bad dependency ordering during its default temporary-database validation on BOTH majors. It protected the live schema. With explicitly disabled validation and allowed hazards, apply failed after dropping the column/index. Credit the default protection; do not advertise this as missed by its safety checker.
- A deliberately faulty caller-supplied UPDATE backfill was first refused with IS_USER_GENERATED hazard. After explicitly allowing that documented hazard, the schema-validated application exited 0 while changing a synthetic identifier from 00001234567890123456 to 00001. An independent original-value contract detected that loss. This is faulty caller SQL outside a schema validator's business correctness promise, not a defect in pg-schema-diff.

Raw evidence: dedicated WSL /opt/migrationwitness/pilot/{native-16,native-17,baseline-16,baseline-17,business17,business17-allowed}. Each includes command argv/output/exit status, result JSON and PostgreSQL server log. The first refused business run and initial build failure are preserved.

Decision: enough practical scope separation to implement an engine-independent, disposable runtime contract witness. Incremental value is reproducible concurrent histories, fault barriers, independent business/client/ACL checks and combined evidence across tools, not ACL or invalid-index detection in isolation. Mature tools already supply many of those checks individually, and an expert can script them. No research novelty, superiority, production accuracy or unique-feature claim. Final release decision remains contingent on actual cross-version controls, tool runs and independent review.
