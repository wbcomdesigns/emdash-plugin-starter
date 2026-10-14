#!/usr/bin/env bash
# Load the Fieldnote model site (realistic content, photos and settings) into a plugin's own lab.
# Usage: model-site/load-into-lab.sh <lab-folder> [--portable]
#
# Two sources, same site:
# - Full snapshot (model-site/snapshot/data.db, kept on the owner's machine only): content, photos
#   AND the plugins' own data (votes, reviews, poll answers, settings), handed to the lab's local
#   plugin build (registry id -> plugin slug).
# - Portable build (any machine, from git): fieldnote-seed.json (all content, settings, menus,
#   categories), media.json and images.json (the committed stock photos). Plugin activity then
#   comes from your plugin's own lab data script (see model-site/README.md).
# The lab must be a standard blog-template EmDash site (made by the plugin's scripts/setup-lab.sh).
# The Fieldnote showcase itself is never touched.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAB="$(cd "${1:?Usage: load-into-lab.sh <lab-folder> [--portable]}" && pwd)"
MODE="${2:-}"
SNAP="$HERE/snapshot"
[[ -f "$LAB/src/layouts/Base.astro" ]] && grep -q 'theme.css' "$LAB/src/layouts/Base.astro" || { echo "STOP: $LAB is not a blog-template site." >&2; exit 1; }
(cd "$LAB" && npx astro dev stop >/dev/null 2>&1 || true)
mkdir -p "$LAB/uploads" && cp -R "$SNAP/uploads/." "$LAB/uploads/"

if [[ -f "$SNAP/data.db" && "$MODE" != "--portable" ]]; then
	cp "$SNAP/data.db" "$LAB/data.db"
	rm -f "$LAB/data.db-wal" "$LAB/data.db-shm"
	sqlite3 "$LAB/data.db" <<SQL
DELETE FROM _plugin_state WHERE source = 'registry';
$(while IFS='=' read -r id slug; do
	[[ -z "$id" || "$id" == \#* ]] && continue
	echo "UPDATE _plugin_storage SET plugin_id='$slug' WHERE plugin_id='$id';"
	echo "UPDATE _plugin_indexes SET plugin_id='$slug' WHERE plugin_id='$id';"
	echo "UPDATE options SET name = replace(name, 'plugin:$id:', 'plugin:$slug:') WHERE name LIKE 'plugin:$id:%';"
done < "$HERE/plugin-ids.txt")
SQL
	echo "Loaded the full Fieldnote snapshot (content, photos and plugin data) into $LAB."
else
	# Portable build: a fresh lab database, then the authored content and the stock photos.
	rm -f "$LAB/data.db" "$LAB/data.db-wal" "$LAB/data.db-shm"
	(cd "$LAB" && npx emdash seed "$HERE/fieldnote-seed.json" --on-conflict update >/dev/null)
	python3 -I - "$LAB/data.db" "$HERE/media.json" "$HERE/images.json" <<'PY'
import json, sqlite3, sys
db = sqlite3.connect(sys.argv[1])
cols = {r[1] for r in db.execute("PRAGMA table_info(media)")}
for row in json.load(open(sys.argv[2])):
    row = {k: v for k, v in row.items() if k in cols}
    db.execute(f"INSERT OR REPLACE INTO media ({', '.join(row)}) VALUES ({', '.join('?' * len(row))})", list(row.values()))
for img in json.load(open(sys.argv[3])):
    db.execute(f'UPDATE "ec_{img["collection"]}" SET "{img["field"]}" = ? WHERE slug = ?', (json.dumps(img["value"]), img["slug"]))
db.commit()
PY
	echo "Built the Fieldnote model site from git (content, photos, settings) in $LAB."
	echo "Plugin activity (votes, reviews, poll answers) comes from your plugin's own lab data script."
fi
echo "Start the lab again (scripts/restart-lab.sh). Sign in on the lab only: /_emdash/api/setup/dev-bypass (admin Maya Lin on the full snapshot)."
