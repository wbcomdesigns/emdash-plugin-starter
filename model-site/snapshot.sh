#!/usr/bin/env bash
# Owner agent only: take a fresh snapshot of the Fieldnote showcase for the labs.
# Reads the showcase; never writes to it.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-$HOME/code/emdash-showcase}"
rm -rf "$HERE/snapshot" && mkdir -p "$HERE/snapshot"
sqlite3 "$SITE/data.db" ".backup '$HERE/snapshot/data.db'"
cp -R "$SITE/uploads" "$HERE/snapshot/uploads"
# No sign-in material in the snapshot: empty every session, token, credential and challenge table.
for t in $(sqlite3 "$HERE/snapshot/data.db" ".tables" | tr ' ' '\n' | grep -iE 'sess|auth_|_auth|cred|token|oauth|challenge|secret|authorization'); do
	sqlite3 "$HERE/snapshot/data.db" "DELETE FROM $t;"
done
# One self-contained file: fold the write-ahead log in and switch it off, so data.db alone is complete.
sqlite3 "$HERE/snapshot/data.db" "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode=DELETE; VACUUM;" >/dev/null
rm -f "$HERE/snapshot/data.db-wal" "$HERE/snapshot/data.db-shm"
echo "Snapshot taken: $(du -sh "$HERE/snapshot" | cut -f1)"
