# Executed supplemental acceptance commands

These are the actual command shapes used in the dedicated local lab, not a hosted CI run. Full shell scripts, timestamps, raw stdout/stderr, package reports, failures and exit statuses remain in `E:/final/migrationwitness-final-evidence-20261018`. Source paths are project-owned; no existing database is connected. Substitute a new directory when reproducing; original evidence must not be overwritten.

## Clean installation and full Linux regression

An independent local clone of runtime commit445e7ff was copied into the disposable WSL lab. A new venv installed the hash-locked accepted Alpine wheels and package; tests were copied outside source. Root ran only the root-refusal branch; the remaining commands ran as the unprivileged postgres account:

```sh
base=/opt/migrationwitness-final-20261018
python3 -m venv "$base/clean-venv"
"$base/clean-venv/bin/python" -m pip install --only-binary=:all: --require-hashes -r "$base/clean-source/requirements-py314-alpine.lock" --report "$base/logs/fresh-linux-dependencies.json"
"$base/clean-venv/bin/python" -m pip install --no-index --no-build-isolation --no-deps "$base/clean-source" --report "$base/logs/fresh-linux-package.json"
MW_PG_BIN=/usr/libexec/postgresql17 "$base/clean-venv/bin/python" -m pytest -q "$base/validation/tests/test_cluster.py::test_root_cannot_initialize"
# Below runs as postgres, not root:
cd "$base/validation"
unset PYTHONPATH
export PYTHONUTF8=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
"$base/clean-venv/bin/python" -c 'import migrationwitness; print(migrationwitness.__file__); assert "site-packages" in migrationwitness.__file__'
for major in 16 17; do
  export MW_PG_BIN=/usr/libexec/postgresql$major
  "$base/clean-venv/bin/python" -m coverage run --source=migrationwitness --data-file="$base/logs/coverage-final-pg$major" -m pytest -q tests --basetemp=/tmp/mw-final-clean-pg$major --junitxml="$base/logs/final-pg$major-tests.xml"
done
```

Both full suites exited0 with40 passed/1 root-only skip. The separate root test exited0/1 passed. Actual coverage reports and the initial red tests are retained; no failed log was rewritten. Coverage tooling was an existing separately installed lab dependency, not a product dependency. Exact installer and interpreter records are in `linux/logs/fresh-linux-*` and `fresh-installed-path.log`.

## Real pg-osc and native permission experiments

For each major16/17 and repetition0/1/2, a new output directory and fresh private cluster were used:

```sh
python pgosc_probe.py --pg-bin /usr/libexec/postgresql16 --mode pgosc --tool-launcher /opt/migrationwitness-final-20261018/pgosc-launcher.sh --output /opt/migrationwitness-final-20261018/runs/pg16-pgosc-r0
python pgosc_probe.py --pg-bin /usr/libexec/postgresql16 --mode native --tool-launcher /opt/migrationwitness-final-20261018/pgosc-launcher.sh --output /opt/migrationwitness-final-20261018/runs/pg16-native-r0
```

The public `scripts/pgosc_197_probe.py` is byte-identical to that actual experiment script. All12 completed with probe exit0; all6 real pg-osc outcomes are contract FAIL and all6 native outcomes PASS. Each tool's real argv/stdout/base64, return code, SQLSTATE, actual role probes, activity/lock samples, catalog/data and sealing are retained. [Build/run procedure](../env/PG_OSC_REPRODUCTION.md) describes the pinned launcher. [Results](../PG_OSC_197_RESULTS.md) records the result and its narrow scope.

## Windows and CI preparation

The Windows job's PowerShell install/full pytest/installed CLI blocks in [ci.yml](../.github/workflows/ci.yml) were executed with a new local Python3.13.0 venv. Raw `ci-preparation/local-windows-final/install.log`, `validation.log`, `cli.log`, `ci-evidence/pytest.log`, JUnit and `test-summary.json` record21 passed/20 explicit skips and CLI success. Native Windows DB operations were NOT RUN. Consult [CI_PREPARATION.md](CI_PREPARATION.md) for exact workflow and static-check scope. Hosted setup-python, Docker lifecycle and GitHub Actions were NOT RUN.

The existing baseline bundle was reverified, and final source inventory/ZIP/bundle/restore checks run separately after documentation freeze; the external DELIVERY.json and SHA256SUMS are authoritative for those identities.
