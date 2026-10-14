#!/usr/bin/env bash
# Load the Fieldnote model site (realistic content and plugin data) into a plugin's own lab.
# Usage: model-site/load-into-lab.sh <lab-folder>
# The lab must be a standard blog-template EmDash site (made by the plugin's scripts/setup-lab.sh).
# It copies the snapshot's database and photos into the lab, drops the registry installs the
# snapshot came with, and hands each plugin's data and settings to the lab's local build
# (registry id -> plugin slug). The Fieldnote showcase itself is never touched.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAB="$(cd "${1:?Usage: load-into-lab.sh <lab-folder>}" && pwd)"
SNAP="$HERE/snapshot"
[[ -f "$SNAP/data.db" ]] || { echo "No snapshot. Ask the plugin owner agent to run model-site/snapshot.sh." >&2; exit 1; }
[[ -f "$LAB/src/layouts/Base.astro" ]] && grep -q 'theme.css' "$LAB/src/layouts/Base.astro" || { echo "STOP: $LAB is not a blog-template site." >&2; exit 1; }
(cd "$LAB" && npx astro dev stop >/dev/null 2>&1 || true)
cp "$SNAP/data.db" "$LAB/data.db"
rm -f "$LAB/data.db-wal" "$LAB/data.db-shm"
mkdir -p "$LAB/uploads" && cp -R "$SNAP/uploads/." "$LAB/uploads/"
sqlite3 "$LAB/data.db" <<SQL
DELETE FROM _plugin_state WHERE source = 'registry';
$(while IFS='=' read -r id slug; do
	[[ -z "$id" || "$id" == \#* ]] && continue
	echo "UPDATE _plugin_storage SET plugin_id='$slug' WHERE plugin_id='$id';"
	echo "UPDATE _plugin_indexes SET plugin_id='$slug' WHERE plugin_id='$id';"
	echo "UPDATE options SET name = replace(name, 'plugin:$id:', 'plugin:$slug:') WHERE name LIKE 'plugin:$id:%';"
done < "$HERE/plugin-ids.txt")
SQL
echo "Loaded the Fieldnote model site into $LAB. Start the lab again (scripts/restart-lab.sh)."
echo "Sign in on the lab only, never on the showcase: /_emdash/api/setup/dev-bypass (admin is Maya Lin)."
