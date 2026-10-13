# What EmDash supports: check this before building

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
| Pick a media file in an admin form | Block Kit `media_picker` | Listora #38 |
| Create a redirect | `redirects:write`, `ctx.redirects.create` | Roadmap #17 |
| Number box, multi-line text, tick-boxes, tabs, combobox in admin forms | Block Kit `number_input`, `text_input` with `multiline`, `checkbox`, `tab`, `combobox` | Every Settings page |
| Site search from a kit page | `search()` from `emdash` | KnowX search |
| EmDash comments on a kit page of a custom collection | Comment functions exist; collection comment settings exist | Roadmap #13 |
| A kit address that tells an admin from a member and a guest | `Astro.locals.user` carries `role` as a number (50 is admin). Read in the EmDash source; not yet tried on a kit address | Listora #46 |
| The site's time zone | Site settings have `timezone`. So no plugin setting is needed | Listora #39 |

## Not possible, so do not plan for it

| Need | Why | What to do |
| --- | --- | --- |
| A block inside post text from a registry install | Sandboxed plugins cannot | Editing-screen panel and slots; block with a trusted install |
| A plugin adding its own pages or styles | Sandboxed plugins cannot | The site kit |
| A plugin intercepting requests | No hook for it | Site middleware from the kit. Decides Maintenance Mode |
| A file download or file upload on a plugin admin page | Block Kit has neither | A kit address for admins |
| A custom field on a category, such as an icon | A category has a label, a slug and a description only | Keep the extra value in plugin storage keyed by the category |
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

### What must be decided or done outside the plugins

1. How our own sites install these: trusted install, or turn on the Worker Loader (needs the paid Workers plan).
2. A mail provider on any site that should send the notices.
3. Update one live site to EmDash 1.2 before the preview check.
