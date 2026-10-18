#!/bin/sh
# Only for a newly created disposable Alpine3.24 environment. Does not start services.
set -eu
if [ "${MW_DISPOSABLE_ENVIRONMENT:-}" != "yes" ]; then
  printf '%s\n' 'Set MW_DISPOSABLE_ENVIRONMENT=yes only inside your disposable Alpine environment.' >&2
  exit 1
fi
. /etc/os-release
test "$ID" = alpine
case "$VERSION_ID" in 3.24.*) ;; *) printf '%s\n' 'Requires pinned Alpine3.24 base' >&2; exit 1 ;; esac
apk add --no-cache postgresql16=16.15-r0 postgresql17=17.11-r0 python3=3.14.8-r0 py3-pip
printf '%s\n' 'Installed; run Python/package/experiments as an unprivileged user, never root.'
