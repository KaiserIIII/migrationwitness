# Reproduce pg-osc #197 with untouched upstream source

This optional legacy reproduction environment is separate from MigrationWitness installation and CI. It is for an isolated, disposable Linux lab only. Ruby3.3.0 is intentionally matched to upstream `.ruby-version`, not recommended as a general network-facing runtime. No production database or private data is used. Docker was checked first but its daemon was unavailable; the official upstream Dockerfile is `FROM ruby:3.0` plus a versioned gem install. That Docker recipe was read, not executed.

## Exact inputs

- pg-osc0.9.10: [commit0a439a873f9df1bf474cfe13060a115278b94658](https://github.com/shayonj/pg-osc/tree/0a439a873f9df1bf474cfe13060a115278b94658), MIT. Official codeload tar.gz SHA256 `8ce5709e5041bb7bb6bd19e643c6faada42ff2987a12edfab140ab219dc4b1de`.
- Ruby3.3.0: [official tar.xz](https://cache.ruby-lang.org/pub/ruby/3.3/ruby-3.3.0.tar.xz), SHA256 `676b65a36e637e90f982b57b059189b3276b9045034dcd186a7e9078847b975b`, release commit `5124f9ac7513eb590c37717337c430cb93caa151`; Ruby/BSD license.
- Bundler2.3.24: release commit `b835c7ea15261a5911eb3c000fe22d8b970c382e`, MIT.
- Upstream `Gemfile.lock` unchanged; `BUNDLE_FROZEN=true`, omit development/test groups. Actual runtime: bigdecimal3.1.8, google-protobuf3.25.5(x86_64-linux), oj3.16.6, ostruct0.6.0, ougai2.0.0, pg1.5.8, pg_query4.2.3, thor1.3.2. Artifact hashes are in [PG_OSC_PROVENANCE.json](../PG_OSC_PROVENANCE.json).
- Accepted Alpine3.24.2 x86_64; PostgreSQL16.15-r0 and17.11-r0, official signed APK builds, private Unix sockets. GCC15.2.0; build-base, zlib-dev, yaml-dev, libffi-dev, gdbm-dev, openssl-dev, libpq-dev. Full installed package/source-commit record remains in local raw evidence.

## Build procedure actually used

Choose a new lab prefix (here `/opt/mw-pgosc-lab`) in the disposable environment. Verify both archive hashes before extraction. Configure Ruby in its extracted source directory:

```sh
./configure --prefix=/opt/mw-pgosc-lab/ruby330 --disable-install-doc --disable-yjit --disable-rjit
make -j4
make install
export PATH=/opt/mw-pgosc-lab/ruby330/bin:/usr/libexec/postgresql17:/usr/bin:/bin
export GEM_HOME=/opt/mw-pgosc-lab/bootstrap-gems
export GEM_PATH=$GEM_HOME:/opt/mw-pgosc-lab/ruby330/lib/ruby/gems/3.3.0
gem install bundler -v 2.3.24 --no-document
cd /opt/mw-pgosc-lab/pg-osc-0a439a873f9df1bf474cfe13060a115278b94658
export BUNDLE_PATH=/opt/mw-pgosc-lab/pgosc-gems
export BUNDLE_WITHOUT=development:test
export BUNDLE_FROZEN=true
export BUNDLE_BUILD__PG_QUERY=--with-cflags=-std=gnu11
bundle _2.3.24_ install
bundle _2.3.24_ exec ruby -Ilib bin/pg-online-schema-change --version
```

The initial source build failed because GCC15 defaults to C23 while pg_query4.2.3 uses older unspecified-argument function declarations. Its supported build option selects GNU C11; no source patch, dependency upgrade or warning/contract suppression was used. The original failed log is retained. All52 upstream archive files, including Gemfile.lock, were byte-verified after installation. The archive lacks `.git`, so upstream gemspec `git ls-files` emits a warning during local source execution; version and actual migration still completed. The tool was not repackaged or published.

Create a small executable launcher exporting the same Ruby/GEM/BUNDLE settings, changing into that unchanged pg-osc source directory and executing:

```sh
exec bundle _2.3.24_ exec ruby -Ilib bin/pg-online-schema-change "$@"
```

Keep that launcher and its legacy runtime outside this repository. The probe takes an explicit trusted launcher path and never downloads or patches software.

## Run the real tool and native control

Install MigrationWitness in a clean Python venv. Run as an unprivileged Linux user with read/execute access to the legacy Ruby environment and write access to a NEW output parent:

```sh
python scripts/pgosc_197_probe.py --pg-bin /usr/libexec/postgresql16 --mode pgosc --tool-launcher /opt/mw-pgosc-lab/pgosc-launcher.sh --output runs/pg16-pgosc
python scripts/pgosc_197_probe.py --pg-bin /usr/libexec/postgresql16 --mode native --tool-launcher /opt/mw-pgosc-lab/pgosc-launcher.sh --output runs/pg16-native
python -m migrationwitness verify runs/pg16-pgosc
```

Repeat with PostgreSQL17 and fresh output paths. Each probe creates100 synthetic rows, separate migration/business LOGIN roles, records OWNER/OID/ACL/GRANT and performs actual SELECT/INSERT/UPDATE/forbidden DELETE as the restricted user. Probes rollback their writes. The migration is integer->bigint; pg-osc must exit cleanly, reach bigint and change OID before permission loss is labeled REPRODUCED. It uses no `--kill-backends` or modified copy query. Native ALTER must preserve OID and grants. The explicit GRANT mitigation is applied only after original tool evidence has been captured; it is not an upstream fix.

Probe exit0 means a completed investigation (including a reproduced failure); the report's **outcome FAIL** remains the business contract verdict. This differs from the main CLI's0/2/1 contract exits and is stated explicitly to avoid mistaking a successful reproducer for a correct migration. Inspect `result.json`, SQL event references, raw tool output and PostgreSQL log. Existing output directories are refused, evidence hashes are verified separately, and all owned clusters are stopped/removed after capture.
