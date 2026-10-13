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
| A block inside post text | `admin.portableTextBlocks` plus a `componentsEntry` exporting `blockComponents`. Trusted install only: EmDash warns they are ignored for registry installs | Polls #16, Reviews #19, Listora #50, Roadmap #18, KnowX #17 |
| List the site's content types | `schema:read`, `ctx.schema.listCollections()` | Reviews #14, KnowX #16 |
| Upload a file to the media library | `media:write`, `ctx.media.upload` or `getUploadUrl` | Listora #25 |
| Pick a media file in an admin form | Block Kit `media_picker` | Listora #38 |
| Create a redirect | `redirects:write`, `ctx.redirects.create` | Roadmap #17 |
| Number box, multi-line text, tick-boxes, tabs, combobox in admin forms | Block Kit `number_input`, `text_input` with `multiline`, `checkbox`, `tab`, `combobox` | Every Settings page |
| Site search from a kit page | `search()` from `emdash` | KnowX search |
| EmDash comments on a kit page of a custom collection | Comment functions exist; collection comment settings exist | Roadmap #13 |
| A kit address that tells an admin from a member and a guest | Kit pages read `Astro.locals.user`. The role field has not been checked | Listora #46 |
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
