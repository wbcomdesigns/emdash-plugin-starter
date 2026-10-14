# What EmDash supports: check this before building

**Read EmDash's own guides first.** Every fresh EmDash site ships them in `.agents/skills/`: `building-emdash-site` (what the CMS gives every site) and `creating-plugins` (what a plugin can do, with `references/sandbox-boundaries.md` for the limits). Source: https://github.com/emdash-cms/emdash, docs: https://docs.emdashcms.com. Those guides beat this file and beat anything remembered. This section was written from them on 2026-10-13 after the owner pointed out the plans were being scoped without looking at what the CMS already offers.

## What EmDash core gives every site (do not rebuild these)

| Built in | What it is | What that means for our plugins |
| --- | --- | --- |
| Site search | `LiveSearch` component (instant results), `search()`, a Ctrl or Cmd + K pattern | KnowX uses it. It does not build its own search box or index |
| Comments | `Comments` and `CommentForm` components, threaded, per collection, with moderation in admin | Roadmap discussion uses it. No comment system of our own, anywhere |
| Widget areas | Named areas (sidebar, footer) the owner fills in admin: search, categories, tags, recent posts, rich text | Check whether a plugin can offer a widget before building a "place it in the sidebar" feature |
| Menus, site settings | Title, tagline, logo, social links, **time zone**, date format | Use the site's time zone and date format. No plugin setting for either |
| Categories and tags | Hierarchical taxonomies with counts, `getEntriesByTerm`, filter in content queries | Listora, Roadmap and KnowX categories are EmDash taxonomies |
| SEO data | Title, description, canonical per entry; plugins add structured data through `page:metadata` | No SEO fields of our own |
| Bylines, redirects, revisions, drafts, scheduling, preview | Core content features | Roadmap merge uses redirects |
| Official plugins | Forms, Embeds, Color picker field, Field kit (lists, grids, tag inputs for json fields), Audit log, Webhook notifier, AI comment moderation, Resend email provider | Docs point owners to Resend for email. Field kit covers list-style fields such as opening hours or a gallery |

## What a registry plugin can add to the admin (from `creating-plugins`)

| Surface | Use it for |
| --- | --- |
| Admin pages (Block Kit: tables, forms, tabs, accordion, charts, meters, banners, conditional fields, button confirmations). **Not in an admin-page form: the repeater and the media picker.** EmDash's guide calls them authoring elements for field widgets | Queues, settings, reports |
| **Dashboard widgets** on the EmDash dashboard | "3 reviews waiting", "2 ideas waiting". The owner's alert, with no email needed |
| **Saved-entry panels and actions** on the post and page editing screen | Polls: attach a poll while editing. Documented for registry plugins |
| **Field widgets**: a custom field on any collection, storing a json value (text, number, toggle, select, media picker elements) | A "poll" or "rating" field the owner adds to a content type |
| **Raw routes that return a file** (`response: "raw"`, `pluginResponse()`, `Content-Disposition` allowed) | A real spreadsheet download from the plugin itself |
| Reading a media file's bytes (`media:bytes:read`, up to 16 MiB) | Import a spreadsheet the owner uploaded to the media library. The owner chooses the file from a dropdown of media names built with `ctx.media.list` (`media:read`), because the media picker cannot sit in an admin-page form |
| MCP tools on private routes | Let an AI agent manage polls or listings. Later |

Only a trusted (native) plugin can add a block inside post text, React admin screens, raw page fragments, or Astro render components.

Checked on 2026-10-13 against EmDash 1.2.0 (the version in the labs). Every locked plan depends on rows in this table. A row marked **Not proven** must be proven on a lab site as the first step of the task that needs it. If the proof fails, stop and tell the owner. Do not build around it and do not keep trying variations.

Live sites run EmDash 1.1. Anything here may be missing there, so each plugin states EmDash 1.2 as its minimum and a site is updated first.

## Proven (used by Listora, tested and walked in a browser)

| Need | How |
| --- | --- |
| Public, member and admin routes | `public: true`; `permission: "content:read"`; no permission means admin |
| Plugin storage with indexes, guarded writes | `ctx.storage.<name>`, `updateIf`, `compareAndSet` |
| Key-value store with compare-and-set | `ctx.kv` |
| Read, create, update, publish content | `content:read`, `content:write`, `content:publish` |
| Read and assign categories | `taxonomies:read`, `taxonomies:write` |
| Send email | `email:send`, `ctx.email.send`. Absent when the site has no mail provider |
| Admin pages: tables, forms, menus, toggles, select, text | Block Kit. Tables need `page_action_id` |
| Structured data on a page | `page:metadata` hook |
| A card on the EmDash dashboard | `admin.widgets` in the manifest. The admin route receives `{ type: "page_load", page: "widget:<id>" }`. Links use `{ type: "link", target: { kind: "plugin-page", path } }`. Proven in Listora #27 |
| A long admin table | `next_cursor` on the table draws Load more. The admin then sends `{ type: "block_action", action_id: <page_action_id>, value: { cursor, sort } }`. There is no Next and Previous. Proven in Listora #45 |
| A settings page in groups, number box with limits | `number_input` with `min` and `max`. A form cannot hold text between fields, so use one small form per group with `context` lines above it. Proven in Listora #27 |
| Kit pages inside the site's layout, colours and fonts | One layout file, site tokens |
| Categories and counts on a kit page | `getTermsForEntries`, `getTaxonomyTerms` from `emdash` |

## In EmDash's code, not proven by us

| Need | What the code says | Needed by |
| --- | --- | --- |
| Scheduled tasks running on their own | `ctx.cron.schedule` and the `cron` hook. Run by hand in tests only | Listora expiry and notices, Reviews and Roadmap notices |
| A panel on the post and page editing screen | `admin.editorPanels`, `admin.editorActions` are in the registry manifest rules | Polls #14 |
| A block inside post text | `admin.portableTextBlocks`, trusted install only. **Already working on our own live sites:** `packages/brndle-blocks` in `knowxtheme-com` and `woocustomdev-com` is a trusted plugin that adds blocks. Copy its shape. Not yet tried with one of these plugins | Polls #16, Reviews #19, Listora #50, Roadmap #18, KnowX #17 |
| List the site's content types | `schema:read`, `ctx.schema.listCollections()` | Reviews #14, KnowX #16 |
| Upload a file to the media library | `media:write`, `ctx.media.upload` or `getUploadUrl` | Listora #25 |
| Pick a media file in an admin form | **Not with `media_picker`** (field widgets only). A dropdown of names from `ctx.media.list` is the way | Listora #25 |
| Create a redirect | `redirects:write`, `ctx.redirects.create` | Roadmap #17 |
| Number box, multi-line text, tick-boxes, tabs, combobox in admin forms | Block Kit `number_input`, `text_input` with `multiline`, `checkbox`, `tab`, `combobox` | Every Settings page |
| Site search from a kit page | `search()` from `emdash` | KnowX search |
| EmDash comments on a kit page of a custom collection | Comment functions exist; collection comment settings exist | Roadmap #13 |
| A real file download from a plugin route | `response: "raw"` with `Content-Disposition`. Documented, not yet tried by us | Listora #46 |
| Import from a media-library file | A dropdown of file names from `ctx.media.list`, then `media:bytes:read`. Not yet tried by us | Listora #46 |
| The site's time zone | Proven in Listora #39. A kit page reads `getSiteSettings().timezone`. A plugin route cannot read it, so anything time-of-day (open now) is worked out by the page. EmDash refuses an unknown zone itself |

## Found while building (2026-10-14)

- A stored image field holds a media reference, not an address. To draw it use EmDash's `Image` component. For a share image or structured data, `Astro.locals.emdash.getPublicMediaUrl(storageKey)` gives the address; make it absolute.
- A plugin route does not get an image address for a listing. Anything that must show a real photo is drawn by the site page, not from plugin JSON.
- EmDash core has a gallery converter (`content/converters/gallery`). Look for a built-in gallery before building one.

## Not possible, so do not plan for it

| Need | Why | What to do |
| --- | --- | --- |
| A block inside post text from a registry install | Sandboxed plugins cannot | Editing-screen panel and slots; block with a trusted install |
| A plugin adding its own pages or styles | Sandboxed plugins cannot | The site kit |
| A plugin intercepting requests | No hook for it | Site middleware from the kit. Decides Maintenance Mode |
| A file input on a plugin admin page | Block Kit has none | Download: a raw plugin route returns the file. Upload: the owner adds the file to the media library and picks it with the media picker. **Earlier text here said a download was not possible. That was wrong** |
| A custom field on a category, such as an icon | A category has a label, a slug and a description only | Keep the extra value in plugin storage keyed by the category |
| The visitor's location ("near me") | EmDash core sends `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()` on every page, so the browser refuses. Found in Listora #51 | Search by typed city. Dropped |
| A member id from the request, or a user on a public route | By design | Member routes are private |
| Atomic rate limits without care | Plain read-then-write races | `compareAndSet` |

## Second check, 2026-10-13: will it work where it runs

Read from the EmDash source and from the live sites' own config files (`knowxtheme-com`, `woocustomdev-com`, `attowp-com`).

### On the live sites today

| Question | Finding | Consequence |
| --- | --- | --- |
| Can a registry (sandboxed) plugin run? | **Not as configured.** The Worker Loader line is commented out in every site's `wrangler.jsonc`, with the note that it needs a Workers paid plan. Without it EmDash's stand-in runner refuses to load a sandboxed plugin | On our own sites, install these plugins the trusted way (`plugins: []`), or turn the loader on. Owner decision |
| Do scheduled tasks fire? | Yes. Every site has a cron trigger each minute | Hourly notices and daily expiry will run |
| Can the site send email? | **No mail provider is configured** on the sites checked. `ctx.email` is then absent | Every "one email an hour" feature stays silent until a provider is set up. The plugins already handle that: nothing breaks, the admin count still shows |
| Is a visitor's address available? | Yes on Cloudflare (`CF-Connecting-IP`, trusted) | Guest voting, guest reviews and guest ideas work |
| EmDash version | 1.1 on live sites, 1.2 in the labs | Update one site first. The editing-screen panel in particular is only confirmed in 1.2 |

### On the lab sites (Node)

| Question | Finding | Consequence |
| --- | --- | --- |
| Visitor's address | **Absent.** On Node EmDash trusts no header unless the site config lists one in `trustedProxyHeaders` | Guest features refuse every guest on a lab as built. Each lab adds `trustedProxyHeaders: ["x-forwarded-for"]` to its EmDash config and the walk sends that header, or guest cases can only be run in automated tests |
| Email | The dev mailer prints the mail to the server log | Read it there |
| Scheduled tasks | The Node scheduler exists. Not yet seen firing on its own | Prove once on any lab |

### Each plugin against EmDash

| Plugin | Fully supported | Supported, prove first | Dropped or changed |
| --- | --- | --- | --- |
| Listora 0.5.0 | Directory, submit, reviews, claims, messages, categories, expiry logic, settings | Scheduled tasks on their own; media upload and media picker (#25, #38); admin-only kit address (#46); in-text block (#50) | Time zone is EmDash's own setting. Import and export are parked if the kit address fails |
| WB Reviews | Reviews, approval, replies, rating data, guest reviews (on Cloudflare) | Listing content types (#14); hourly email task (#16); in-text block (#19) | Member account list moved to 0.2.0 |
| WB Polls | Polls, voting, results, guest voting (on Cloudflare), slots | Editing-screen panel (#14, EmDash 1.2); in-text block (#16) | Member polls, list and poll pages: not built, by owner decision |
| Product Roadmap | Items as content, voting, suggestions with approval, stages kept in plugin settings, categories | EmDash comments on the item page (#13); redirect on merge (#17); hourly email task (#16); in-text block (#18) | Emails to voters: not built |
| KnowX | Articles and categories as content, helpful votes, search log, report, FAQ, version badge | Site search from the kit page (needs the collection to have search turned on); listing content types (#16); in-text block (#17) | Product icon lives in plugin storage, since a category has no custom fields |
| WB Maintenance Mode | Nothing | Nothing | Dropped: a plugin cannot intercept requests |

### How to read all of this (owner, 2026-10-13)

These are general plugins for any EmDash site owner, not for our own sites. Our sites' config above is one example, nothing more.

- **Build on EmDash's own core.** Every EmDash site runs the same core, so plan around what the core provides. No per-site "what works here" checker.
- **Visitors first.** About nine in ten EmDash sites have visitors only, no members, and EmDash is very new. The visitor path is the main product: voting, reviewing, suggesting and rating must work for a visitor on any hosting. Member-only extras come later.
- **A visitor must never be locked out by hosting.** Where EmDash supplies a trusted visitor address, use it (salted hash). Where it does not, fall back to a browser cookie: one entry per browser, written content still waits for approval, and the admin page says the protection is weaker. (The cookie fallback is the build team's reading of "visitors first"; the owner can reverse it.)
- **Registry install first.** Everything in a plan works from the registry install. A trusted install is an optional extra for blocks inside text, documented as a short second section.
- **Email is a bonus.** A feature is complete without it. The notice goes out only where the site has mail.

## Proven on 2026-10-14 (Listora 0.5.0)

- **A block inside post text, with a trusted install: works.** A site-local native plugin whose descriptor is `{ id, version, format: "native", entrypoint: "/src/<folder>/plugin.ts", componentsEntry: "/src/<folder>/components.ts" }`, listed under `plugins: []`, puts the block in the editor's `/` menu and draws it on the page. No package needed. Give a `select` field an `initial_value`, or Insert stays off until a field is filled. An article styles its own `img`, `a` and headings, so the block must set those again with enough weight; headings inside the block land in the theme's contents list.
- **Admin-only (private) plugin routes refuse a plain browser link.** A cookie session must send `X-EmDash-Request: 1`, on GET too, or the answer is 403 `CSRF_REJECTED`. So a file download from a private route needs page script (`fetch` with the header, then a blob link). An admin Block Kit page cannot start one.
- **A top-level `link` block is invalid.** Put links inside `{ type: "actions", elements: [...] }` or a table cell.
- **`emdash seed <file> --no-content`** adds a collection, fields and taxonomies to a site that already has content (default `--on-conflict skip`). Local SQLite only as far as we have proven.

## Proven on 2026-10-14 (standard blog site, all five Wbcom plugins installed from the registry)

- **Registry installs get a generated id.** Routes live at `/_emdash/api/plugins/r_<16 base32>/`, the id being SHA-256(`<publisher DID>\n<slug>`) truncated (`emdash/src/registry/plugin-id.ts`). The slug address answers 404 "Plugin route not found". EmDash's own api-routes guide still says `<slug>`. Use `pluginFetch()` from `site-kit/lib/wbcom-kit.ts` (version 3) for every kit request. Our ids: listora `r_2oeji6rfeg7ovdex`, reviews `r_nt2pnhev44oaara3`, polls `r_4dk64cimgjxrz74v`, roadmap `r_76xywti6l5cbxzos`, knowx `r_2bzw2y6sgiq5c455`.
- **Admin pages and dashboard cards work** on a registry install (EmDash links them under the generated id itself).
- **The admin's registry screen** shows a generic plug icon in the list; the plugin's own icon, banner and screenshots show on its detail page once it loads.
- **The default template is blog** (`npm create emdash@latest` with no template = cloudflare + blog). Test on it.
