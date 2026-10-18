# Upstream validation (2026-10-18)

Statuses are fresh authenticated public GitHub API observations, not inferred from issue age. Raw issues/comments/timelines, licenses, immutable source and hashes are external `upstream-issues/` and `competitors/` dossiers. All three issues remain open. No upstream Issue/PR was created.

## pgroll #1013 — actual related timeout path reproduced

[Issue](https://github.com/xataio/pgroll/issues/1013), current/latest v0.16.3 commit777a5350e09012b29d26b9611122046d8a96fc1c. Reporter says PG17 and “PGROLL14.3” (interpreting0.14.3 is an inference), load triggers repeated “index already exists”. Original workload is not supplied.

Actual run on PG16.15 AND17.11 used the supplied client/email schema (100 synthetic clients), explicit200ms pgroll lock timeout and an open updating transaction. `pgroll init`, baseline and genuine `pgroll start --complete` were run from the pinned source binary. The observer saw the concurrent-index lock wait and an index with indisvalid=false/indisready=false. Holding the writer for another0.8s triggered lock-timeout/retry and `relation client_api_key_idx already exists`; pgroll rolled back and removed the index. After releasing the writer, a quiet retry exited0 and created a valid/ready index. The100-row/count/id-sum/api-key-distinct check remained100/5050/100.

Classification: **independently reproduced related controlled timeout/retry path**, not identical reproduction of the original unspecified production schedule, and not a claim of data loss. Earlier invalid JSON recipes failed before migration; those attempts remain preserved and are not bug evidence. The actual tool evidence is `linux/tool-runs/pgroll-{16,17}-v5/`.

## pg-schema-diff #316 — reproduced; default safety check catches it

[Issue](https://github.com/stripe/pg-schema-diff/issues/316), v1.0.9/current9ada4710c28718312557c84cca1be4b2557eed54. `t(id primary key,u,c)` has an index on u with `WHERE c IS NULL`; target drops c. Pinned source builds dependency columns from indkey, omitting predicate-only references. [PR317](https://github.com/stripe/pg-schema-diff/pull/317) is open/unmerged; its code was inspected, not installed or represented as verified fix.

Actual PG16.15/17.11 native CLI plan validation failed with42704 because DROP COLUMN removed the dependent index before generated DROP INDEX CONCURRENTLY. This happened in the scratch validation database and left all live columns intact. With **explicit** `--disable-plan-validation` plus required allowed hazards, plan exited0 but unsafe apply exited1 after c and the index had already been removed. Rows remaining were independently inspected.

Classification: **independently reproduced**, with default protection working. This is not a migration defect missed by default validation. Expression-index variant and proposed PR fix runtime: **NOT RUN**. Actual raw evidence: `linux/pilot/baseline-{16,17}/`.

## pg-osc #197 — source-supported concern, actual migration NOT RUN

[Issue](https://github.com/shayonj/pg-osc/issues/197) reports post-swap user access loss without specifying release, PostgreSQL version, roles or exact schema. Current042c6eefd7e5eb59044fd99cf1c42d26ddf022cf and release0.9.10/0a439a873f9df1bf474cfe13060a115278b94658 clone/swap paths are byte-identical in inspected files: LIKE INCLUDING ALL does not by itself replay table ACLs, and no explicit grant replay was found in those paths. This source observation is not execution proof.

Pinned source and official0.9.10 gem were obtained and checked. Installation in dedicated Alpine/Ruby3.4.9 failed in upstream pinned google-protobuf3.25.5 native extension (format-security error; retry encountered upstream Rake build argument/dependency issues). Logs retained. No attempt was made to patch upstream dependency source or claim a successful pg-osc migration. **Full pg-osc migration/#197 reproduction: NOT RUN, environment/build limitation.**

Separate native table-replacement controls reproduce loss of an explicit reader grant and the fixed restore-grant behavior. Those are labeled constructed PostgreSQL controls, never pg-osc validation. A compatible separately pinned upstream Ruby environment is the main unresolved tool-coverage item.

## Atlas Community and business-value baseline

Apache Community1.3.0 source9a6bc601212130aaaefcbc8dd36c710baf9716ff was built with community flavor. Actual hash, dry-run and apply on PG17.11 exited0 for a deliberately lossy caller UPDATE; independent business-value check failed. The same test with pg-schema-diff first refused IS_USER_GENERATED, then executed when that explicit hazard was allowed. These demonstrate scope boundaries, not defects: schema correctness does not prove arbitrary business transformation correctness. No commercial/protected Atlas feature or MSA binary was used. Raw `linux/tool-runs/atlas-17-v4/` and `linux/pilot/business17{,-allowed}/`.
