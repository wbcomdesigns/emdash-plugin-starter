#!/usr/bin/env bash
# Owner agent only: take a fresh snapshot of the Fieldnote showcase for the labs.
# Reads the showcase; never writes to it. The new snapshot is built in a work folder and
# replaces the committed one only after model-site/scrub.py cleaned and verified it; any
# failure leaves the previous snapshot exactly as it was.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="${1:-$HOME/code/emdash-showcase}"
WORK="$(mktemp -d "$HERE/.snapshot-work.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
sqlite3 "$SITE/data.db" ".backup '$WORK/data.db'"
cp -R "$SITE/uploads" "$WORK/uploads"
python3 "$HERE/scrub.py" "$WORK/data.db"
rm -f "$WORK/data.db-wal" "$WORK/data.db-shm"
rm -rf "$HERE/.snapshot-old"
if [[ -d "$HERE/snapshot" ]]; then mv "$HERE/snapshot" "$HERE/.snapshot-old"; fi
mv "$WORK" "$HERE/snapshot"
rm -rf "$HERE/.snapshot-old"
trap - EXIT
echo "Snapshot taken: $(du -sh "$HERE/snapshot" | cut -f1)"
