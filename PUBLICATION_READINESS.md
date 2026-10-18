# Source-experiment publication readiness

**PUBLICATION_READY — source experimental edition only.** Prepared target: `KaiserIIII/migrationwitness`. The repository has not been created, no remote configured, no code pushed, and no Release/PyPI/deployment performed. Publishing remains a separate human authorization step.

## Evidence supporting the decision

- Frozen baseline preserved and bundle-verified; only two reproduced behavior defects were fixed (ambiguous SQL assertion false PASS and Markdown outcome heading injection), plus a reproduced test startup flake. Independent re-review found no unresolved reproduced P1/P2 in the reviewed core; current41-test full PG17 run passed40 with one root-only skip.
- New clean Git clone, new hash-locked Linux venv, installed-package imports outside source, complete PG16.15/17.11 regressions:40 passed/1 root-only skip each. Separate root refusal passed. Fresh Windows3.13 preparation:21 passed/20 explicitly skipped, installed offline CLI/Unicode/tamper checks passed.
- Real untouched pg-osc0.9.10 completed on both majors, reproducing role grant loss in all6 controlled runs; native ALTER preserved grants in all6 controls. Source files/lock verified unchanged. Earlier failed builds and framework red tests are retained.
- Reviewed public file inventory, relative links, MIT project license, exact Python wheel locks, source/license provenance and immutable CI action references. External runtimes/binaries/private raw logs are excluded from source. Author/committer identity uses KaiserIIII's GitHub noreply address.
- Source ZIP, Git Bundle, file/hash inventory, restore instructions and final SHA/tree are generated together and checked in external DELIVERY.json; the commit cannot contain its own hash.

## CI readiness is distinct from execution

[Workflow](.github/workflows/ci.yml) prepared: Windows Python3.13 offline/tests/CLI; bounded Alpine Python3.14 PostgreSQL16/17 full small suite. Action SHAs, official rootfs checksum and accepted platform wheel hashes are pinned; direct APK versions are exact and signed transitive package records retained. Linux CI containers specify2CPU/1GiB RAM/256PIDs/512MiB tmpfs, a5-minute suite deadline and15-minute job budget. These are CI container limits, not product-enforced quotas.

Fresh local Windows workflow commands and static YAML/PowerShell/shell/Python checks passed. **GitHub-hosted Actions and Docker container lifecycle are NOT RUN** because publication is not authorized and the local daemon is unavailable. No green badge or hosted-CI success is claimed. Hosted labels/setup-Python artifacts and signed transitive APK resolution remain operational dependencies; missing pinned versions must fail closed. See [CI preparation](docs/CI_PREPARATION.md).

## Public boundary and known limits

Source ZIP contains only tracked original source, tests, docs, CI configuration, exact metadata and an explicitly derived real-run summary of synthetic data. Original pg-osc stdout contains hostnames and local paths and remains private. Raw GitHub comments, unreviewed snapshots, caches, venvs, legacy Ruby/gems and PostgreSQL data directories are excluded. No private calendar, production database, personal document or token was used.

Dependencies retain their own licenses and are installed separately; no native/third-party binary is redistributed. Release-tag resolution and artifact hashes are not complete source-to-binary attestations. Bundled native libraries in upstream wheels and a comprehensive CVE advisory scan are NOT fully audited; no “CVE-free” or security-sandbox claim. Legacy Ruby3.3.0 is isolated optional reproduction tooling, not a recommended service runtime.

Native Windows PostgreSQL remains unsupported/NOT RUN; use Linux/WSL. Arbitrary trusted SQL/commands can ignore connection environment/timeouts and consume resources; no hard product memory/CPU/disk quota, arbitrary-schedule control or universal descendant isolation. Production accuracy, arbitrary ACL/metadata/workload preservation, replication/failover and untested PG/Python versions remain UNKNOWN/NOT RUN. Hash manifests are unsigned. These limitations are compatible with a clearly labeled local source experiment, not a production safety certificate.

## Frozen release procedure

[PUBLISHING.md](PUBLISHING.md) records the pending repository/push/CI procedure. Do not execute it without fresh publication authorization. No feature expansion or new project follows this acceptance. Final candidate/ZIP/bundle identity is external `E:/final/migrationwitness-final-evidence-20261018/DELIVERY.json`; retain the previous baseline artifacts separately.
