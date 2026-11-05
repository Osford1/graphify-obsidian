# Credits

This repo is my pipeline and notes. It stands on three pieces of other people's work, none of
which is redistributed here.

| Component | Author / upstream | Version | Licence | How it is used |
| --- | --- | --- | --- | --- |
| **graphify** (`graphifyy` on PyPI) | Graphify Labs — <https://github.com/Graphify-Labs/graphify> | 0.9.65 | Apache-2.0 (the wheel also ships a `LICENSE-MIT` file, i.e. dual-licensed) | The entire pipeline: detection, extraction, build, clustering, report, Obsidian export. Used as an installed tool. |
| **vis-network** | vis.js contributors — <https://github.com/visjs/vis-network> | 9.1.6 | Apache-2.0 / MIT (dual) | Renders the interactive graph. `scripts/inline_vis.py` inlines a copy **you supply**; the ~700 KB bundle is not committed. |
| **Obsidian** | Dynalist Inc. — <https://obsidian.md> | (desktop app) | Proprietary, free for personal use | The app the exported vault is opened in. |

## Provenance notes

- **graphify version is pinned.** The installed skill records it in `.graphify_version` =
  `0.9.65`. The scripts here call graphify's Python modules (`graphify.build`, `graphify.cluster`,
  `graphify.analyze`, `graphify.report`, `graphify.export`) directly, so they are tied to that
  version's API surface. Re-check the module signatures on upgrade.
- **No licence on the skill itself.** The installed `graphify` skill folder carries a version
  marker but **no licence file**. With no licence to copy under, no part of the skill's `SKILL.md`
  or `references/` is reproduced in this repo — it is credited and linked only.
- **vis-network version string.** `inline_vis.py` writes the banner
  `/* vis-network 9.1.6 UMD, inlined for offline use */`. If you inline a different bundle,
  update that string so the file still says what it contains.
- **Corpus is not included.** The papers the graph was built from are other people's work and are
  deliberately absent; so is any graph output that embeds paper-derived text. See
  `docs/scope-and-limits.md` and `sample/README.md`.
