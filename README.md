# graphify-obsidian

**Turning a folder of research papers into a knowledge graph, then into a browsable Obsidian
vault.** This is the pipeline and the notes I use to do that — the scripts, the runbook, the docs
— not a product and not a fork of [graphify](https://github.com/Graphify-Labs/graphify).

It works on my machine and my vault layout. There is no installer, no config file and no test
suite; the scripts assume the `graphify` skill is already installed and that a corpus folder and a
`graphify-out/` directory already exist. If you want the tool itself, use graphify — this repo is
only *how I drive it*.

## The path it takes

    papers/*.pdf ─▶ detection ─▶ LLM extraction ─▶ merge + build ─▶ graph.json
                                                          │
                                                          ├─▶ graph.html   (vis-network inlined, opens offline)
                                                          └─▶ Obsidian vault (one note per node, wikilinks)
                                                                  │
                                                                  └─▶ PNG   (manual: screenshot the HTML graph)

| # | Stage | What runs | Output |
| --- | --- | --- | --- |
| 1 | Detect | graphify scans the corpus | `graphify-out/.graphify_detect.json` |
| 2 | Extract | structure pass, then LLM subagents over chunks | `.graphify_ast.json`, `.graphify_chunk_NN.json` |
| 3 | Merge | `scripts/merge_and_build.sh` folds chunks → dedup → merge | `.graphify_extract.json` |
| 4 | Build | graph + clustering + analysis + report | `graph.json`, `GRAPH_REPORT.md` |
| 5 | Inline | `scripts/inline_vis.py` bakes vis-network into the HTML | `graph.html` (0 external refs) |
| 6 | Export | graphify's Obsidian exporter | `obsidian-vault/*.md` |

`docs/pipeline.md` walks all of it with the real commands and intermediate file names.
`scripts/apply_labels.py` re-applies my curated community names; `scripts/relate.py` answers
"how does paper A relate to paper B" straight off `graph.json`.

## State of the real run

Numbers below are measured from the files in the working copy, not estimated. Run dated
**2026-09-23**, corpus **15 documents** (12 PDF + 3 Markdown, ~38,358 words).

| Metric | Value |
| --- | --- |
| Nodes | 680 |
| Edges | 913 (834 EXTRACTED · 78 INFERRED · 1 AMBIGUOUS) |
| Hyperedges | 27 |
| Communities | 61 (51 shown, 10 thin omitted) |
| Node types | concept 470 · rationale 142 · paper 52 · code 10 · document 6 |
| Est. tokens | 80,906 in / 49,435 out — **estimate** (`cost.json` says `estimated: true`) |
| Vault notes | 575 `.md`, exported 2026-09-22 |
| `graph.html` | 1,401,501 bytes, inlined, 0 external refs |

**Unknown / not measured:** wall-clock build time (no timestamped log), and there is no PNG in
the working copy — the PNG stage is a manual screenshot.

**Caveat worth knowing:** the vault export (575 notes, 2026-09-22) is *older* than the final graph
(680 nodes, 2026-09-23) because two papers were added after the first export. Re-run
`graphify export obsidian` after a rebuild or the vault silently lags the graph.

## What is in here

| Path | What it is |
| --- | --- |
| `docs/pipeline.md` | Stage-by-stage walk with the real commands and intermediate file names. |
| `docs/obsidian-setup.md` | How the graph lands in the vault: note format, frontmatter, links, how I open it. |
| `docs/scope-and-limits.md` | What this is *not*, and the failure modes I actually hit. |
| `docs/owner-todos.md` | Open items (PNG, vault re-export, build timing). |
| `scripts/merge_and_build.sh` | The runbook: merge chunks → build → cluster → report. |
| `scripts/inline_vis.py` | Inline the vis-network bundle into `graph.html` so it opens with no network. |
| `scripts/apply_labels.py` | Apply curated community labels; regenerate the report and JSON. |
| `scripts/relate.py` | "How does A relate to B" — cross-paper edges, shortest path, communities. |
| `sample/` | One honest slice of the real output — read `sample/README.md` first. |

## Running it

You need the `graphify` skill installed, a corpus folder, and (for the vault) an Obsidian vault.

    # build graph + vault in one go (graphify CLI)
    graphify /path/to/papers --obsidian

    # or drive merge/build yourself when extraction was done in chunks
    GRAPHIFY_CORPUS=/path/to/papers bash scripts/merge_and_build.sh

    # make the HTML self-contained (needs your own vis-network.min.js)
    VIS_NETWORK_JS=/path/to/vis-network.min.js python scripts/inline_vis.py

    # re-apply curated community names (optional)
    GRAPHIFY_CORPUS=/path/to/papers python scripts/apply_labels.py labels.json

    # ask how two papers relate
    python scripts/relate.py genception robot_learning_a_tutorial

Nothing is wired into a single command; that is deliberate — the stages fail independently and I
want to see which one broke.

## Credits

Built on **graphify** (`graphifyy`, <https://github.com/Graphify-Labs/graphify>), rendered with
**vis-network**, opened in **Obsidian**. Full list and licences in `CREDITS.md`. The first-party
scripts and docs here are MIT (`LICENSE`); third-party components keep their own licences and
none of their code is redistributed in this repo.
