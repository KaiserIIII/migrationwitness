# Disposable Linux environment

The actual acceptance environment is a new WSL2 distro, not a reused application distro or production database. Docker client existed, daemon unavailable; no daemon reset/socket deletion was attempted.

Official base:

- `https://dl-cdn.alpinelinux.org/alpine/v3.24/releases/x86_64/alpine-minirootfs-3.24.2-x86_64.tar.gz`
- SHA256 `c5ca053cfe1d85c5b96dff8b9bc57045f7f184a30ffb6b65776409ca90388677`

Verify that checksum before importing a NEW uniquely named WSL distro (`wsl --import NAME NEW_DIRECTORY ROOTFS --version 2`). Do not export/copy an existing personal distro. Run `MW_DISPOSABLE_ENVIRONMENT=yes sh env/setup-alpine.sh` inside the disposable distro only. Signed APK repository retention can change; exact versions must exist or installation fails rather than silently upgrade. Full accepted package/version/aports-commit records are in the external delivery evidence.

Create/use a non-root user (Alpine PG package provides `postgres`). Install the package into a clean venv; run under that non-root user. PostgreSQL binaries are `/usr/libexec/postgresql16` and `/usr/libexec/postgresql17`. The harness initializes/stops/removes its own clusters; it does not start an OS database service. Acceptance scripts below need write access to the chosen fresh output parent:

```sh
python -m pip install . pytest==9.0.3
MW_PG_BIN=/usr/libexec/postgresql16 python -m pytest -q
MW_PG_BIN=/usr/libexec/postgresql17 python -m pytest -q
python scripts/acceptance.py --pg-bin /usr/libexec/postgresql17 --output runs/pg17 --repeat 3
```

The project also accepts ordinary official Debian/Ubuntu PostgreSQL binary directories under an unprivileged Linux account; those packaging environments are not part of this acceptance. No VM/Docker image is redistributed.

## Optional pinned migration tools

Inspect upstream licenses/source before running them, only inside the disposable environment. Exact versions/commits and tested commands are in [DEPENDENCIES.md](../docs/DEPENDENCIES.md) and [UPSTREAM_VALIDATION.md](../docs/UPSTREAM_VALIDATION.md). pg-schema-diff and pgroll can be built with exact Go module commits and Go's checksum verification enabled. Default proxy timed out in this lab; a public mirror was used without disabling checksum verification.

```sh
GOBIN="$PWD/tools" go install github.com/stripe/pg-schema-diff/cmd/pg-schema-diff@9ada4710c28718312557c84cca1be4b2557eed54
GOBIN="$PWD/tools" go install github.com/xataio/pgroll@777a5350e09012b29d26b9611122046d8a96fc1c
python scripts/schema_diff_probe.py --pg-bin /usr/libexec/postgresql16 --tool-path "$PWD/tools/pg-schema-diff" --output runs/schema-probe
python scripts/upstream_probe.py pgroll --pg-bin /usr/libexec/postgresql17 --tool-path "$PWD/tools/pgroll" --output runs/pgroll-probe
```

Atlas was built from Apache Community1.3.0 source (nested `cmd/atlas`, Go1.26.4+): `go build -mod=readonly -ldflags='-X ariga.io/atlas/cmd/atlas/internal/cmdapi.flavor=community' -o /chosen/path/atlas .`. Then use `scripts/upstream_probe.py atlas` with its explicit tool path. Do not substitute the standard commercial distribution under its competitive-benchmarking restriction.

Initial Alpine/Ruby3.4 dependency builds failed and remain preserved. Supplemental untouched pg-osc0.9.10 actually completed with Ruby3.3.0/Bundler2.3.24 and the original frozen lockfile, using a supported GNU C11 build option for pg_query. See [PG_OSC_REPRODUCTION.md](PG_OSC_REPRODUCTION.md) for exact sources, versions and commands and [actual results](../PG_OSC_197_RESULTS.md). No source/dependency version was changed. Docker execution remains NOT RUN.
