#!/usr/bin/env bash
# Owner agent only: take a fresh snapshot of the Fieldnote showcase for the labs.
# Reads the showcase; never writes to it.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-$HOME/code/emdash-showcase}"
rm -rf "$HERE/snapshot" && mkdir -p "$HERE/snapshot"
sqlite3 "$SITE/data.db" ".backup '$HERE/snapshot/data.db'"
cp -R "$SITE/uploads" "$HERE/snapshot/uploads"
# Scrub: no sign-in material, no secrets, no visitor traces.
DB="$HERE/snapshot/data.db"
for t in $(sqlite3 "$DB" ".tables" | tr ' ' '\n' | grep -iE 'sess|auth|cred|token|oauth|challenge|secret|device_code|audit|rate_limit|404_log|transfer_|upload_attempt'); do
	sqlite3 "$DB" "DELETE FROM $t;"
done
sqlite3 "$DB" "DELETE FROM options WHERE lower(name) GLOB '*secret*' OR lower(name) GLOB '*salt*' OR lower(name) GLOB '*token*' OR lower(name) GLOB '*password*' OR lower(name) GLOB '*key*' OR lower(name) GLOB '*smtp*' OR lower(name) GLOB '*api*';"

# Check, fail closed: anything that still looks secret, or any email outside the fake domains,
# deletes the snapshot and stops. Add a domain here only for made-up model-site addresses.
fail() { echo "STOP: $1. Snapshot deleted; nothing to commit." >&2; rm -rf "$HERE/snapshot"; exit 1; }
left="$(sqlite3 "$DB" "SELECT name FROM options WHERE name GLOB '*[Ss]ecret*' OR name GLOB '*[Ss]alt*' OR name GLOB '*[Tt]oken*' OR name GLOB '*[Kk]ey*';")"
[[ -z "$left" ]] || fail "secret-like settings remain: $left"
for t in $(sqlite3 "$DB" ".tables" | tr ' ' '\n' | grep -iE 'sess|auth|cred|token|oauth|secret|audit'); do
	[[ "$(sqlite3 "$DB" "SELECT count(*) FROM $t;")" == 0 ]] || fail "table $t still has rows"
done
stray="$(sqlite3 "$DB" .dump | grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' | grep -vE '@([A-Za-z0-9-]+\.)*example(\.com)?$|^dev@emdash\.local$' | sort -u)"
[[ -z "$stray" ]] || fail "email addresses outside the fake domains: $stray"

# One self-contained file: fold the write-ahead log in and switch it off, so data.db alone is complete.
sqlite3 "$HERE/snapshot/data.db" "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode=DELETE; VACUUM;" >/dev/null
rm -f "$HERE/snapshot/data.db-wal" "$HERE/snapshot/data.db-shm"
echo "Snapshot taken: $(du -sh "$HERE/snapshot" | cut -f1)"
