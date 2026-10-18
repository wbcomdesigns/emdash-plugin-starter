# Before you install (shared text)

Every Wbcom EmDash plugin starts its registry Installation tab and its `docs/website/getting-started/install.md` with this block, word for word, so a developer meets the same first steps on every plugin. Change it here first, then copy it into each plugin at its next release.

Fill in `<Plugin>`, `<slug>`, `<repo>` and `<tag>` for each plugin. `<tag>` is the version being released (`v0.2.1`), never `main`.

---

## Before you install

**1. Your site needs a sandbox runner.** Registry plugins run in a sandbox. Until the site has one, Admin, Plugins shows "No plugins configured" and there is no Registry in the menu.

- **Node:** in your site, run `npm install @emdash-cms/sandbox-workerd workerd`, then add `sandboxRunner: "@emdash-cms/sandbox-workerd/sandbox",` inside `emdash({ ... })` in `astro.config.mjs`.
- **Cloudflare:** add `import { sandbox } from "@emdash-cms/cloudflare";` and `sandboxRunner: sandbox(),`. It needs the Workers Paid plan and a `worker_loaders` binding named `LOADER` in your Wrangler config. The EmDash Cloudflare templates ship that binding commented out. EmDash's guide: https://docs.emdashcms.com/deployment/plugin-sandbox/#cloudflare-workers

Stop the dev server and start it again. **Registry** now shows in the admin menu.

**2. The plugin is the engine. Visitor pages come from its site kit.** A registry plugin cannot add pages to your site. Until you copy the kit, its addresses (for example `/<slug>/`) show your site's 404 page. That is expected. The kit copy below takes one command.

**3. You need Node 22.16 or later** for the `npx emdash seed` step.

Checked on EmDash 1.3.1 with the `blog` template on Node. The Cloudflare lines follow EmDash's own guide; we have not run them on a Cloudflare site yet.

## Install

1. Admin, Registry, search **<Plugin>**, Install, then accept the permissions.
2. From your site's root folder, get the kit for the version you just installed and copy it in:

   ```bash
   kit="$(mktemp -d)" &&
     git clone --depth 1 \
       --branch <tag> \
       https://github.com/wbcomdesigns/<repo> \
       "$kit/<repo>" &&
     "$kit/<repo>/scripts/add-to-site.sh" .
   ```

   (`mktemp -d` makes a fresh folder only you can write to, and `&&` runs the script only when the clone worked. Never clone into a fixed `/tmp/<name>`: on a shared machine someone else can create it first.)

   The script copies the kit, never replaces a newer shared file another Wbcom plugin already copied, keeps a backup of the wording file only when you changed it yourself, creates the content types the plugin needs (if any), and prints the exact lines to paste into your templates, with the file names.
3. Paste the lines it printed. Restart the dev server.
4. Add the menu links it printed in Admin, Menus.
5. Open the plugin in the admin and follow its first screen.

After every plugin update, run step 2 again with the new tag.

## Rules for the command and the script (for plugin builders)

- **Show the command exactly as above, on six lines, every line 52 characters or fewer,** everywhere: the admin card, both install pages, the kit README and the script's own output. An admin `code` block does not wrap or scroll, so a longer line is cut off. 52 characters fit the code box at 768 and wider. At 390 the box is about 40 characters wide and the address line is still cut, so the card also links the install guide right under the command ("Copy it from the install guide on a phone"), where it wraps.
- **Wording backup only when the owner edited it.** The kit ships `site-kit/lib/<plugin>-strings.sums`: one SHA-256 per line, of the strings file of every released version, newest last (add the new one at each release). The script backs up the site's strings file only when its hash is not in that list. An untouched file from any older release is replaced without a word.
- **Say when a shared file was upgraded.** When the script replaces an older `wbcom-kit.ts` or `wbcom-base.css` that another Wbcom plugin copied, it prints one line saying so (old and new `wbcom-shared` numbers), as it does when it keeps a newer one.
- **Engine and kit can be one version apart.** A site updates the plugin in the admin and copies the kit later, or the other way round. The kit must handle every error code the previous engine release returns and the new one returns, and must treat a missing field from an older engine (for example `guestWrites`) the safe way. A guest never sees "Something went wrong" for a known refusal: a "guest cannot write here" code from either version shows the sign-in wording. The registry changelog of every release says "Copy the kit again after you update", with the command.

- **Every kit file the owner may edit is protected the same way.** Ship `site-kit/kit.sums`: `<sha256>  <path>` for every file the script copies, at every released tag plus the new one. Before replacing a site file, the script backs it up (`.bak-YYYYMMDD`, a time suffix on a second run the same day) when its hash is not a released hash for that path, and says which files it backed up. Untouched files from any release are replaced without a word. This covers components, styles and pages, not only the wording file.
- **A new kit keeps sending what the previous engine needs.** If the previous engine keyed guests by a browser token or field, the new kit still sends it (the new engine ignores it), so an older engine never falls back to one shared or one random identity per request.

## Guests and hosting (shared text for every plugin with guest writes)

Copy this into the plugin's guest section, filled in.

EmDash gives a plugin the visitor's address only on Cloudflare, or when the site sets `trustedProxyHeaders` in `astro.config.mjs`. Without an address, guests are asked to sign in before they can vote or post, so one person cannot vote many times.

Set `trustedProxyHeaders` only to a header that **your proxy writes itself and replaces** on every request. EmDash reads the first address in that header. Many proxies **add** to `X-Forwarded-For` instead of replacing it (nginx `$proxy_add_x_forwarded_for`, most load balancers), so the first address is whatever the visitor typed, and a guest could vote again and again. Behind nginx, set `proxy_set_header X-Real-IP $remote_addr;` and use `trustedProxyHeaders: ["x-real-ip"]`. Behind another proxy, use the header it overwrites with the connecting address. If you are not sure, leave it unset: members can still take part.
