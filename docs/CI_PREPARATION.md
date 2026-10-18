# Historical local CI preparation, 2026-10-18

> Prepublication snapshot: the NOT RUN statements below describe the original local preparation. Subsequent [actual hosted acceptance](https://github.com/KaiserIIII/migrationwitness/actions/runs/39122362491) passed all3 jobs on472b98d: LinuxPG16/17 each40 passed/1 root-only skip, Windows21/20, plus actual supported CLI and Linux root-refusal checks. Hosted Docker passed; local Docker daemon remains unavailable. See [current cross-version results](../CROSS_VERSION_RESULTS.md).

Workflow `.github/workflows/ci.yml` is prepared. No public repository, remote, push, Release or hosted workflow run was created; local source commits are recorded separately in the delivery. All evidence paths below are relative to the private `ci-preparation/` acceptance dossier, not public files.

The Windows job uses Python 3.13.0 x64 and `requirements-py313-windows.lock` with `--require-hashes --only-binary=:all:`. It runs the full suite while explicitly recording database and POSIX-only skips, then exercises an installed CLI outside the checkout: list 12 scenarios, render Unicode/HTML-escaped evidence, seal and verify it, and reject a deliberately modified copy with exit code 2.

The Linux matrix runs PostgreSQL 16.15-r0 and 17.11-r0 on Python 3.14.8-r0 inside the accepted Alpine 3.24.2 rootfs. This preserves compatibility with the existing CPython 3.14 musllinux wheel lock; that lock cannot be used directly on hosted Ubuntu/glibc. The official rootfs SHA-256 endpoint was fetched again and matches the pinned value. CI downloads and checks the actual rootfs bytes before importing a local Docker image. No pre-existing database or remote service is used.

Each Linux container has 2 CPUs, 1 GiB RAM with no extra swap, 256 PIDs, a 512 MiB `/tmp` tmpfs, and a 64 MiB per-file limit. There are no host bind mounts, published ports, Docker socket mounts, or privileged containers. The full suite runs as the unprivileged PostgreSQL user with a 300-second deadline and a 15-second kill grace. Installation plus execution has a 450-second outer deadline; the complete Linux job has a 15-minute budget. The root-refusal test executes separately as root, then only that branch may be skipped in the unprivileged full suite. Windows has a 10-minute job budget and 3-minute test-step budget; no independent Windows process memory quota is claimed. These are external CI limits, not product-enforced quotas. The container writable layer has no aggregate disk quota.

Local evidence:

- `local-windows-final/install.log` and its `ci-evidence/dependency-install.json`: fresh Python 3.13.0 environment, hash-locked dependency installation and offline build succeeded after the final core changes.
- `local-windows-final/ci-evidence/pytest.log`, `pytest.xml`, and `test-summary.json`: **41 collected, 21 passed, 20 skipped**. Nineteen skips require unavailable native PostgreSQL execution; one requires POSIX process groups. Native Windows PostgreSQL: **NOT RUN**.
- `local-windows-final/cli.log` and `ci-evidence/cli-summary.json`: installed offline CLI passed list/render/verify/tamper-rejection checks. The intentionally tampered evidence directory is a negative control.
- `static-validation.json`: YAML parsed with already-installed PyYAML 6.0.3, read-only permissions/full action SHAs/job timeouts checked. Extracted PowerShell scripts parsed successfully. All five extracted Linux shell scripts passed `sh -n` in the existing accepted Alpine environment; embedded Python snippets also compile. No actionlint or complete GitHub workflow-schema validation is claimed.
- `actions-provenance.json`: immutable release/ref SHAs, source URLs, MIT license links, and review scope. Fetched action metadata, README and license files are external evidence, not product source. Review covered those materials; no exhaustive bundled JavaScript audit or source-to-runtime attestation is claimed.
- `alpine-direct-provenance.json`: accepted signed-APK versions, licenses, and aports source commits for direct system dependencies. `observed-alpine-apk-installed.txt` is the prior accepted environment's package record, not a newly executed CI installation.

An early guard fixed to the original 39-test baseline correctly rejected a concurrently expanded 40-test suite. It was replaced by a minimum-baseline guard plus actual-count recording and allowed-skip checks. A local Windows-to-WSL extraction initially used CRLF; extracted shell evidence was rewritten with LF before successful syntax checks. These were preparation issues, not successful hosted CI runs.

Hosted GitHub Actions and the Docker container lifecycle are **NOT RUN**. The local Docker daemon is unavailable, and it was not started, reset or repaired. The final Windows verification used the local 3.13.0 interpreter rather than executing `actions/setup-python` on a hosted runner. Hosted labels remain mutable; exact Python setup artifacts are resolved by the pinned action. Direct APK packages are exact-version pinned, but their full transitive closure is resolved from signed repositories and recorded at runtime rather than locked here. Exact old APK versions disappearing will fail closed. None of these limitations is evidence of hosted CI success.

Official documentation consulted:

- [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Docker container run and resource flags](https://docs.docker.com/reference/cli/docker/container/run/)
- [Docker rootfs import](https://docs.docker.com/reference/cli/docker/image/import/)
- [Docker container file copy](https://docs.docker.com/reference/cli/docker/container/cp/)
- [pytest JUnit XML output](https://docs.pytest.org/en/stable/how-to/output.html#creating-junitxml-format-files)
- [Official Alpine rootfs SHA-256](https://dl-cdn.alpinelinux.org/alpine/v3.24/releases/x86_64/alpine-minirootfs-3.24.2-x86_64.tar.gz.sha256)
