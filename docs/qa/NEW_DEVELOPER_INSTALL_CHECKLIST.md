# New developer install checklist

A fresh-eye QA pass for every Wbcom EmDash plugin: Listora, WB Reviews, WB Polls, Product Roadmap, KnowX, and every plugin that follows.

The question it answers: **can a developer who has never seen our repos install a plugin, wire it into their site, and reach a working visitor page, using only what we give them?**

Started 2026-10-18, after a report that on a fresh EmDash setup "all the plugins give 404".

## Rules for the tester

1. **Read only what a new developer gets.** That is the registry listing (its Description, Installation and FAQ tabs) and the GitHub pages it links to, at the release tag that is live. Nothing else: no lab scripts (`setup-lab.sh`, `apply-kit.sh`, `prove-lab.sh`), no `ops/`, no memory, no team chat.
2. **Do each step exactly as written.** Copy-paste commands and snippets as they are. If a step needs knowledge the guide does not give, that is a finding, even when you know the answer.
3. **Note each place you stopped to think.** Did you guess a file name, look up a path, or read the source? Each one is a finding.
4. **Never fix the site to keep going without writing it down.** Write the finding, then apply the smallest fix and carry on, so one gap does not hide the next.
5. **One GitHub issue per finding** on that plugin's repo, labelled `install-path`, under the next version milestone. A gap shared by every plugin goes on `emdash-plugin-starter`.
6. **Screenshots** go to `~/work-artifacts/screenshots/YYYY-MM/`. Open each one and judge it as the owner or visitor would.

## Starting points

Run the checklist from each starting point. The same plugin can pass one and fail another.

| ID | Site | How to get it | What it catches |
| --- | --- | --- | --- |
| F1 | Fresh site, Node | `npm create emdash@latest <dir> -- --template blog --platform node --pm npm --yes` | The default local setup |
| F2 | Fresh site, Cloudflare | `npm create emdash@latest <dir>` with the defaults (Cloudflare, blog) | The default `create-emdash` platform, which has a different sandbox runner |
| E1 | Existing blog site, current EmDash | An F1 site with a few posts and pages already added | The usual "I already have a blog" developer |
| E2 | Existing site, other template | `--template portfolio` or `--template starter`, or a site whose layout is not `Base.astro` | Layout names, entry ids and template paths that differ from the blog template |
| E3 | Existing site, older EmDash | A site still on 1.2, updated during the walk | Update order and version notes |
| E4 | Existing site with another Wbcom plugin | Any site above with one Wbcom plugin already wired | Shared kit files (`wbcom-kit.ts`, `wbcom-base.css`), `/account/` pages, menu links |

Write down the EmDash version shown at the foot of the admin sidebar for every run. On 2026-10-18 a fresh site got **EmDash 1.3.0**; from 2026-10-18 19:19 UTC it gets **1.3.1**, and every guide still says "tested on 1.2".

## Part 0. Is the site ready for a registry plugin?

Do this once per site, before any plugin.

| # | Check | Pass when | Where developers get lost |
| --- | --- | --- | --- |
| 0.1 | Open Admin, Plugins on the untouched site | You can see where plugins come from | On a fresh site the screen says "No plugins configured" and shows **no Registry link**. Nothing says why. |
| 0.2 | Find out from our guide what the site needs | The guide names the package to install and the exact `astro.config.mjs` lines, for Node and for Cloudflare | Our guides say "needs a sandbox runner" in one line at the bottom. Only the WB Reviews kit README shows the lines, and only for Node. Nothing covers Cloudflare (`@emdash-cms/cloudflare` `sandbox()` and the Worker Loader binding). |
| 0.3 | Install the runner and restart the dev server | Admin, Plugins shows **Registry** | Nothing says a restart is needed after changing `astro.config.mjs` |
| 0.4 | Open Admin, Registry and search "Wbcom" or the plugin name | All five plugins are listed, published by Wbcom Designs, with a verified badge | |

## Part 1. The same steps for every plugin

Walk these for each plugin. Part 2 lists what is particular to each.

| # | Step | Pass when | Fresh-eye questions |
| --- | --- | --- | --- |
| 1.1 | Find the install steps | The registry Installation tab tells you every step, or links to one page that does | Is there one place to start, or several pages that disagree? |
| 1.2 | Install from the registry and accept the permissions | Admin, Plugins shows the plugin active at the live version. Its menu items appear in the sidebar. | Are the permissions explained in plain words? |
| 1.3 | Open each admin screen of the plugin | Each screen loads with an empty state that says what to do next. No error and no blank screen. | Does the first admin screen say the visitor pages still need the site kit? (Today: no.) |
| 1.4 | Open the visitor address the guide promises (for example `/roadmap/`) **before** copying the kit | You get a clear sign of what is missing | Today every kit address is a plain 404. **This is the reported bug.** |
| 1.5 | Get the kit files | The guide says where to get them **and which version**, and the files match the installed version | Guides say `path/to/emdash-x/site-kit`. Clone what? Which branch or tag? `main` can be ahead of the registry. |
| 1.6 | Copy the kit exactly as written | Every command works as pasted from the site root | Undefined `$K`, folders missing from the copy list, a script that must run from one folder |
| 1.7 | Create the content types the plugin needs, if any | One command, given in the guide, makes them | Does the guide give a command or only "create a collection with these fields"? |
| 1.8 | Wire the components into templates | The guide names **the file** to edit (for example `src/pages/posts/[slug].astro`) and the snippet works as pasted | Import paths in snippets assume a file one folder up from where the blog template keeps it |
| 1.9 | Add the menu links | The guide lists every link and where menus are edited (Admin, Menus) | |
| 1.10 | Start the site and open every visitor page | Every page renders, styled like the site, at 1440 and 390, light and dark | Unstyled page, layout not found, 404, build error |
| 1.11 | Do the main job as a guest, a member and an admin | Each role gets the result the guide promises, with clear failure messages | Member features need member sign-up turned on in EmDash. Is that said up front? |
| 1.12 | Check the browser console and the server log | No errors except ones the guide calls expected (for example a guest 401 on a member-only route) | |
| 1.13 | Update path | The guide says what to do after a plugin update (copy the kit again) and which files are never overwritten | Do my own edits to the strings file survive? |

## Part 2. Each plugin

The release tags walked on 2026-10-18 are noted. Recheck against the live tag each time.

### Listora (v0.6.1)

| # | Check | Notes from the 2026-10-18 read |
| --- | --- | --- |
| L1 | `git clone` plus `scripts/add-to-site.sh /path/to/site` | The only plugin with a one-command kit install. It clones `main`, not the live tag. |
| L2 | `npx emdash seed .emdash/listora-seed.json --no-content` | The CLI exists in a fresh site. Run it from the site root. |
| L3 | `src/layouts/ListoraLayout.astro` hands off to `Base.astro` | E2 sites: does the guide say how to point it at another layout? |
| L4 | Menu links `/listings/`, `/listings/submit/`, `/listings/calendar/`, `/account/` | `/account/` is shared with other plugins' `/account/*` pages. Check on E4. |
| L5 | Admin, Get started, **Load sample directory** | 12 listings with reviews appear on `/listings/` |
| L6 | Guest browses, searches, messages a listing. Member submits, reviews, saves, claims. Admin approves. | |
| L7 | Map tiles load from `tile.openstreetmap.org` | |

### WB Reviews (v0.2.0)

| # | Check | Notes from the 2026-10-18 read |
| --- | --- | --- |
| R1 | Kit copy commands | `K=path/to/emdash-reviews/site-kit`: the developer has to work out to clone the repo first |
| R2 | `<Reviews collection="posts" id={post.data.id} />` on the post template | The README snippet imports `../components/Reviews.astro`. From `src/pages/posts/[slug].astro` the right path is `../../components/`, so the snippet as pasted fails. The guide never names the file. |
| R3 | `<RatingBadge>` "on cards" | Which file is a card? On the blog template it is `src/components/PostCard.astro`, and the entry id there needs checking. |
| R4 | Admin, Reviews, Settings: tick content types, Save | Without this step no form shows. Is that clear? |
| R5 | Guest review waits, admin approves, page and badge update | |
| R6 | `/account/reviews/` My reviews, delete with a second click | |
| R7 | Email notice with no mail provider | It says plainly that email is off, with no silent failure |

### WB Polls (v0.3.0)

| # | Check | Notes from the 2026-10-18 walk (F1, passed after fixes by hand) |
| --- | --- | --- |
| P1 | Kit copy commands | Worked as pasted once `$K` pointed at a checkout of the tag |
| P2 | `<PollSlot collection="posts" id={post.data.id} />` | The snippet imports `../components/PollSlot.astro`. From `src/pages/posts/[slug].astro` the right path is `../../components/`. The guide never names the file. |
| P3 | Two slots, `position="above"` and `"below"` | Worked |
| P4 | `/account/votes` page | Worked |
| P5 | Create a poll, attach it to the whole site, open it, vote as a guest | Worked: the results bar and "You voted." showed |
| P6 | Guest console | One 401 from the member ballot check before the guest fallback. Expected, but is it documented? |

### Product Roadmap (v0.2.1)

| # | Check | Notes from the 2026-10-18 read |
| --- | --- | --- |
| M1 | Install steps | The registry Installation tab still warns about the 0.1.0 kit. That is stale for a new developer. |
| M2 | Create the `roadmap` and `changelog` collections | The Installation tab says "the kit ships the field list in `collection.mjs`". The kit README gives a seed command instead. The two disagree. |
| M3 | Copy `lib`, `styles`, `components`, `pages` | **`layouts/` is missing from the list**, but every page imports `../../layouts/RoadmapLayout.astro`. Followed as written, the site fails to build. |
| M4 | `$K` in the seed command | Never defined in that README |
| M5 | "Open Admin, then Settings" | Ambiguous: EmDash's own Settings or the plugin's Settings page |
| M6 | Menu links `/roadmap/`, `/changelog/`, `/account/roadmap-votes/` | |
| M7 | Guest votes, guest suggests, admin approves and moves stages, changelog entry shows | |

### KnowX (v0.1.4)

| # | Check | Notes from the 2026-10-18 read |
| --- | --- | --- |
| K1 | Create the `docs` and `faq` collections | The Installation tab says "field list in `site-kit/seed/`". The kit README gives `npx emdash seed $K/seed/knowx-seed.json --no-content`. They disagree. |
| K2 | Kit copy commands | Long but complete. `K=path/to/knowx/site-kit` uses a different folder name from the repo (`emdash-knowx`). |
| K3 | Search turned on for both collections | The seed does it. Check in Admin, Content Types. |
| K4 | Menu links `/docs/`, `/docs/faq/` | |
| K5 | Admin, KnowX, Settings: contact link, content types for search | |
| K6 | Guest searches, reads, votes helpful. Insights shows the search and the vote. | |

## Part 3. All five on one site

Run on E4 with all five wired, at the live versions.

| # | Check | Pass when |
| --- | --- | --- |
| 3.1 | Shared files | `src/lib/wbcom-kit.ts` and `src/styles/wbcom-base.css` hold the highest `wbcom-shared` number of the five, and every plugin works with it |
| 3.2 | `/account/` area | `/account/`, `/account/votes`, `/account/reviews/`, `/account/roadmap-votes/` all render, and the menu makes sense to a member |
| 3.3 | Post template | Poll slots, Reviews and any other component sit together without broken spacing at 390 |
| 3.4 | Admin sidebar | Each plugin's menu items have plain names. A first-time owner can tell which belongs to which plugin. |
| 3.5 | Dashboard widgets | All plugins' cards load |

## Part 4. Reporting

- One GitHub issue per finding, labelled `install-path`, on the plugin's repo (or on `emdash-plugin-starter` when every plugin shares the gap).
- Each issue names: the starting point (F1 to E4), the EmDash version, the plugin version and kit tag, the exact step, what the guide said, what happened, and what a new developer would need instead.
- When the pass is done, add a dated row below.

## Runs

| Date | Starting point | EmDash | Plugins and tags | Result |
| --- | --- | --- | --- | --- |
| 2026-10-18 | F1 | 1.3.0 | All five installed from the registry. WB Polls v0.3.0 kit walked. | Engines and admin screens fine. Part 0 fails (no Registry without a runner, no steps for it). Step 1.4 fails for all five (plain 404 before the kit is copied). P2, R2, M3 and the other findings above are open. Other kits not yet walked. |
| 2026-10-18 | F1 | 1.3.0 (d10d7ae1b) | Listora v0.6.1, WB Reviews v0.2.0, WB Polls v0.3.0, Product Roadmap v0.2.1, KnowX v0.1.4. Site: `~/code/nd-f1` on port 4371. | Part 0 fails until `@emdash-cms/sandbox-workerd` is installed and the dev process is started again (a config reload is not enough). Step 1.4 is a plain 404 for every kit URL. Listora's setup command works and `/listings/` renders. Pasted `$K=path/to/...` commands fail. Roadmap without `layouts/` returns 500. Reviews `../components` import returns 500 on the blog post. KnowX `/docs/` renders after the tag is checked out by hand. Guest 401 on Reviews `/mine` and Roadmap `/votes`. Issues filed. F2, E1, E2, E3, E4 and the guest/member/admin jobs are not walked yet. |
