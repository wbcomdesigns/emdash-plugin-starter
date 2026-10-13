# Wbcom EmDash plugins: plan and starter

This repository is two things:

1. **The plan** for the Wbcom utility plugins on EmDash: which plugins, in what order, who can work on what.
2. **The starter** every plugin repo is made from, and the home of the two files all plugin kits share.

## The plugins

| Plugin | Repo | Lab port | Brand | State on 2026-10-13 |
| --- | --- | --- | --- | --- |
| Listora (directory) | `emdash-listora` | 4321 | Listora | Shipped. 0.3.1 on the registry |
| WB Reviews | `emdash-reviews` | 4331 | WB Reviews | Engine, admin and 13 tests written. Kit written, never rendered |
| Polls | `emdash-polls` | 4332 | WB Polls | Starter only |
| KnowX Knowledge Base | `emdash-knowx` | 4333 | KnowX | Starter only |
| WB Maintenance Mode | `emdash-maintenance` | 4334 | WB Maintenance Mode | Starter only. First card is an investigation |
| Roadmap and Feature Voting | `emdash-roadmap` | 4335 | Product Roadmap | Starter only |

Each plugin repo carries everything an agent needs, with no shared conversation:

| File | Answers |
| --- | --- |
| `ops/handoff.md` | Where does it stand, what do I do next |
| `SCOPE.md` | How every kind of site owner uses it, decisions made with the owner, what is in and out, the data schema, routes, settings, screens and their states |
| `PLAN.md` | The order of the 0.1.0 cards, what is parked for 0.2.0, what must be proven before a live site |
| `AGENTS.md` | The hard rules |
| `CONTRIBUTING.md` | Build rules, the gate before a release, the publish steps |
| `docs/qa/QA_CHECKLIST.md` | The cases by role that a release must pass |
| GitHub issues, milestone `0.1.0` | The cards: build, UX ready when, function ready when, QA cases |

## How to assign the work

- **One agent per plugin.** The repos, lab sites and ports are separate, so the five can run at the same time on one machine.
- Tell the agent one thing: "Read `ops/handoff.md` in `~/code/emdash-<slug>` and work the cards in order."
- An agent stops at a passing gate. It never publishes. A registry release cannot be changed.
- An agent does not edit `site-kit/lib/wbcom-kit.ts` or `site-kit/styles/wbcom-base.css` in its own repo. A change to either is made here first and then copied to every plugin, by whoever owns this repo.

## Suggested order if you cannot run all five at once

1. **Reviews**: closest to done, and it proves the shared kit and the lab scripts for everyone else.
2. **Polls**: small, no site content involved.
3. **Roadmap**: the same member pattern, plus the one case where a member action creates a draft.
4. **KnowX**: the largest kit (four pages) and public writes from guests.
5. **Maintenance Mode**: start its investigation card early, because the answer decides the design.

## Rules every plugin follows

- Free scope only. `SCOPE.md` is the contract.
- Guests do only what `SCOPE.md` marks public. Member actions use the signed-in EmDash account, never an id from the request.
- Derived numbers (ratings, vote counts) live in plugin storage, so keeping them right never touches site content.
- Kit markup is the same for every visitor, because site pages are cached without regard to cookies.
- Nothing from an outside host in the kit. Sites only allow scripts and styles from themselves.
- Every screen has loading, empty and error states, works at 390, and reads in dark mode.
- Everyone installing an EmDash plugin today is a developer, so setup may need one. What the owner and visitors use after setup must still be plain and complete.
- A registry (sandboxed) install cannot add a block inside article text; a trusted install can (`admin.portableTextBlocks` plus a `componentsEntry`). Each plugin has a "prove the in-text block" task. A registry install can add a panel and actions to the post and page editing screen (`admin.editorPanels`, `admin.editorActions`). First use is `emdash-polls` issue #14.
- No half-cooked features: if a site owner with no technical help cannot use a thing from start to finish, it is not built or shipped in that form. No typed internal ids, no copy-and-paste boxes.
- Every release passes the gate in `CONTRIBUTING.md`, including a browser walk as a subscriber-role member.

## Brand kits

Logos are never drawn in a plugin repo. They come from the brand pipeline in `~/Documents/brand logos/_render-src/`, which builds the whole set from one mark definition: `build_kit.py` for the WB plugin family (separate gradient shapes, no tile), `build_web_kit.py` for site brands (tile marks), `build_social.py` / `build_web_social.py` for banners, `preview_sheet.py` for the contact sheet, `update_brand_md.py` for the brand sheet. A plugin repo carries only `icon.png` (256, from the kit's mark) and `images/banner.png` (the no-tagline lockup on white).

Kits built on 2026-10-13: KnowX, WB Polls, Product Roadmap, WB Reviews, WB Maintenance Mode.

## Open decisions for the owner

- **Publisher name.** Everything publishes as `@vapvarun.bsky.social/<slug>`. Moving to a Wbcom handle later means new package identities. Decide before the second plugin is published.
- **Decided 2026-10-13:** the site owner chooses who can take part (members only, or anyone) in Reviews, Polls and Roadmap.
- **Not ready for existing live sites yet.** The findings from Listora apply to all of these: prove each kit on a preview deploy of one site, never on production first. See `emdash-listora` issue #23.
- **Shared account page.** Each plugin ships a `My ...` component and no account page of its own, so they never collide. A site's account page mounts whichever it has installed. Listora still ships its own `/account/` page and should move to this pattern.

## Making a new plugin from this starter

1. Copy this folder to `~/code/emdash-<slug>`, without `node_modules` and `.git`.
2. Set `name` and `lab.port` in `package.json`, and `slug`, `name`, `description`, `keywords`, `repo` in `emdash-plugin.jsonc`.
3. Write `SCOPE.md` before any code, and settle its open questions with the owner one at a time: how each kind of site owner uses it, purpose, in scope, out of scope, schema, routes, settings, admin screens, kit files, screens and their states, risks. Record each answer in its decisions table.
4. Write `PLAN.md`: the cards in order, what is parked, what must be proven before a live site.
5. Write `docs/qa/QA_CHECKLIST.md` from the scope: guest, member, admin and presentation cases.
6. File the cards as GitHub issues, each with Build, UX ready when, Function ready when and QA cases.
7. `npm install --legacy-peer-deps && npm test`, then `./scripts/setup-lab.sh`.

The full process, including what went wrong on the first release, is in the `vapvarun-emdash` skill: `references/plugin-publishing.md`.
