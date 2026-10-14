#!/usr/bin/env bash
# Owner agent only: take a fresh snapshot of the Fieldnote showcase for the labs.
# Reads the showcase; never writes to it.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-$HOME/code/emdash-showcase}"
rm -rf "$HERE/snapshot" && mkdir -p "$HERE/snapshot"
sqlite3 "$SITE/data.db" ".backup '$HERE/snapshot/data.db'"
cp -R "$SITE/uploads" "$HERE/snapshot/uploads"
echo "Snapshot taken: $(du -sh "$HERE/snapshot" | cut -f1)"
