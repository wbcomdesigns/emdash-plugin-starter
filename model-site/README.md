# Fieldnote model site

The same realistic content and plugin data as the Fieldnote showcase (port 4350), for any plugin lab. Agents build features and take screenshots against this data, so every plugin is judged on one believable site: a notes app company with 8 posts, an About page with a poll, 10 partner listings with photos and 2 waiting, 10 roadmap items with 231 votes, 3 releases, 8 help articles, 4 FAQs, reviews with an owner reply, and the site named Fieldnote with admin Maya Lin.

## Use it (agents)

1. Build your plugin's standard lab: `scripts/setup-lab.sh` in the plugin repo (blog template).
2. Load the model data into it:

   ```bash
   bash ~/code/emdash-plugin-starter/model-site/load-into-lab.sh <your-lab-folder>
   ```

3. Start the lab again: `scripts/restart-lab.sh` (with `PLUGIN_LAB=<your-lab-folder>` if you used a custom folder).
4. Sign in on your lab only: `http://localhost:<lab-port>/_emdash/api/setup/dev-bypass?redirect=/_emdash/admin/`.

Your plugin's data and settings from the showcase are handed to your lab's local build. The site menu links to every plugin's pages; pages of plugins your lab does not have will 404, which is expected.

To start over, run the loader again: it replaces the lab's database with the snapshot.

## Never

- Never sign in to, change, or reset the showcase itself (`~/code/emdash-showcase`, port 4350). Its sign-in shortcut resets the menu and footer.
- Never commit lab data back here. Only the owner agent refreshes the snapshot.

## Refresh the snapshot (owner agent only)

After the showcase gains new content or a plugin release: `bash model-site/snapshot.sh` (reads the showcase, never writes to it). It cleans a copy with `scrub.py` and replaces the committed snapshot only if the check passes. If it stops on a new table, review that table and add it to `ALLOWED_TABLES` only when it holds nothing personal. After changing `scrub.py`, run `python3 -I model-site/test_scrub.py`. Check `plugin-ids.txt` still matches the showcase's registry install ids, then commit.
