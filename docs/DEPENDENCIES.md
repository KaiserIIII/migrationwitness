# Dependency provenance

Installed only in a new dedicated `MigrationWitness-20261018` WSL distro and project-owned fresh venvs. No third-party Skill installation. Rootfs official Alpine3.24.2 SHA256 c5ca053cfe1d85c5b96dff8b9bc57045f7f184a30ffb6b65776409ca90388677; signed Alpine APK packages retain distribution signatures. Raw `/lib/apk/db/installed` is archived externally, including every transitive package version, origin, license and aports source commit. The authoritative installation timestamps and package records are in the delivery evidence manifest.

| Component | Pinned version / source | License / provenance |
| --- | --- | --- |
| PostgreSQL16 | 16.15-r0, upstream REL_16_15 / 7d3e000c5961a544302072058a1184e9a588837b | PostgreSQL License, Alpine signed package |
| PostgreSQL17 | 17.11-r0, upstream REL_17_11 / 083ac033419f690758508e08c1736089384bbee8 | PostgreSQL License, Alpine signed package |
| Python Linux | 3.14.8-r0 | PSF, Alpine signed package |
| Python Windows | 3.13.0 existing installed interpreter | PSF, read-only runtime; fresh project venv |
| psycopg | 3.3.4 /83f110367cdd249cc0a352e2246ecea9e878e5a0 | LGPL-3.0; official PyPI wheels/APK, not copied into source |
| pytest | 9.0.3 /a7d58d7a21b78581e636bbbdea13c66ad1657c1e | MIT, test-only |
| setuptools | 80.9.0 | MIT, build-only |
| pg-schema-diff | v1.0.9 / 9ada4710c28718312557c84cca1be4b2557eed54 | MIT, source Go build |
| pgroll | v0.16.3 / 777a5350e09012b29d26b9611122046d8a96fc1c | Apache-2.0, source Go build |
| Atlas Community | v1.3.0 / 9a6bc601212130aaaefcbc8dd36c710baf9716ff | Apache-2.0, source build community flavor, no commercial binary/login |
| pg-osc | inspected current042c6eefd7e5eb59044fd99cf1c42d26ddf022cf, release0.9.10 /0a439a873f9df1bf474cfe13060a115278b94658 | MIT, installation attempt and compatibility limits documented |

Go's default proxy timed out. Public goproxy.cn fallback retained checksum database verification (not disabled), exact source module versions and upstream go.sum. Transitive build module records are external `go version -m`/module-cache evidence, not redistributed product dependencies. Ruby attempts honor pinned Gemfile.lock and are lab-only; failed builds are not represented as executed migrations.

No upstream source text or binary is vendored into this MIT package. Public documentation links and original synthetic examples are included. Full fetched third-party source/API responses remain in the external evidence directory and are excluded from the source ZIP.
