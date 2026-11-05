# The pipeline, stage by stage

This walks the real path one papers corpus took: papers → extraction → graph → inlined
visualisation → Obsidian vault → PNG. Every command and file name below is the one that actually
ran; where a stage was manual, it says so.

All paths are relative to the project root — the directory that holds `graphify-out/` and the
corpus folder. The corpus folder is `GRAPHIFY_CORPUS`.

---

## 0. Pick the interpreter

graphify records the Python it ran under:

    graphify-out/.graphify_python      # one line: absolute path to the venv python

The runbook reads it into `PY` so every stage uses the same interpreter:

    PY="$(cat graphify-out/.graphify_python)"

Why it matters: graphify is usually installed with `uv`/`pipx` into its own venv. Calling the
system `python` instead will import-fail on `graphify.*`.

---

## 1. Detect — what is in the corpus

graphify scans the corpus and writes the file manifest it will process:

    graphify-out/.graphify_detect.json

For this corpus that found **15 documents** — 12 PDFs and 3 Markdown files. Detection is also
where the "Corpus Check" line in the report comes from (~38,358 words → "fits in a single
context window").

---

## 2. Extract — structure pass, then LLM pass

Two extractions run:

- **Structure / AST pass** → `graphify-out/.graphify_ast.json`. Near-empty for a folder of PDFs;
  it earns its keep on code.
- **LLM pass** over chunks → `graphify-out/.graphify_chunk_NN.json`. One JSON per chunk; this is
  where nodes and edges are actually proposed, each tagged `EXTRACTED` or `INFERRED`.

Chunks are produced by graphify's subagents. There is **no per-child token accounting**, which is
why `cost.json` is marked `estimated: true` (see stage 7).

If you add papers and re-run, only new/changed files are re-extracted; the hashes live in
`graphify-out/manifest.json`.

---

## 3. Merge — chunks → one extraction file

`scripts/merge_and_build.sh` does this in three cheap Python passes:

1. **Concatenate** every `.graphify_chunk_*.json` that parses →
   `graphify-out/.graphify_semantic_new.json`. A chunk that fails to parse is named and skipped,
   never fatal.
2. **Dedupe nodes by `id`** → `graphify-out/.graphify_semantic.json`.
3. **Merge structure + semantic nodes** (AST ids win) →
   `graphify-out/.graphify_extract.json`.

Run it:

    GRAPHIFY_CORPUS=/path/to/papers bash scripts/merge_and_build.sh

Why the split files: a chunk that fails to parse costs you only that chunk, and the merge is
cheap to re-run.

---

## 4. Build — graph, communities, report

Still inside the runbook, one Python block calls graphify's modules directly:

    from graphify.build   import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions
    from graphify.report  import generate
    from graphify.export  import to_json

    G = build_from_json(extraction, root=CORPUS, directed=False)

Two things that bite:

- **`root=` must be the corpus directory**, not the project directory. `build_from_json` derives
  a prefix for node ids from it; pass the wrong root and every id is silently re-keyed, which
  breaks community lookups later. (Called out in `apply_labels.py` too.)
- **`to_json` refuses to shrink.** If the existing `graph.json` has more nodes than the new build,
  it returns false and the runbook aborts rather than overwrite a bigger graph with a smaller one.
  Move `graph.json` aside if shrinking is intended.

Outputs:

| File | What |
| --- | --- |
| `graphify-out/graph.json` | the graph (node-link JSON: `nodes`, `links`, `hyperedges`) |
| `graphify-out/GRAPH_REPORT.md` | human report: counts, community hubs, god nodes |
| `graphify-out/.graphify_analysis.json` | communities, cohesion, god nodes, surprises, questions |

Then an integrity check:

    graphify diagnose multigraph --graph graphify-out/graph.json

---

## 5. Inline the visualisation (make `graph.html` offline)

graphify's HTML export loads vis-network from a CDN:

    <script src="https://unpkg.com/vis-network@..."></script>

That dies without a network. `scripts/inline_vis.py` replaces the tag with the contents of a
local `vis-network.min.js` you supply:

    VIS_NETWORK_JS=/path/to/vis-network.min.js python scripts/inline_vis.py

It is idempotent (re-running prints "already inlined") and backs the original up to
`graph.html.orig` the first time. On this corpus:

    graph.html.orig      555,228 bytes   (CDN tag)
    graph.html         1,401,501 bytes   (inlined)
    inlined JS           702,611 bytes

Verify with a grep — there should be **no** `https://` left in `src=`/`href=`:

    grep -oE '(src|href)="https?://[^"]*"' graphify-out/graph.html    # → nothing

---

## 6. Export to the Obsidian vault

graphify's Obsidian exporter turns the graph into notes:

    graphify export obsidian        # writes obsidian-vault/

Full detail in `docs/obsidian-setup.md`. In short: one note per node, one note per community,
wikilinks for edges, a manifest of what it wrote, and a plain `.obsidian/` config so it opens as
a vault.

Exports are not incremental-aware the way the graph is — the vault exported here (575 notes,
2026-09-22) is older than the graph (2026-09-23). Re-export after a rebuild.

---

## 7. PNG export — manual

There is no PNG in the working copy and no script for it. The final visual is a **manual
screenshot** of the inlined `graph.html` open in a browser; that image is what gets pasted into a
note as a static preview. If you would rather have a file export than a screenshot, graphify can
also write an SVG:

    graphify /path/to/papers --svg      # graph.svg, embeds in Notion/GitHub

Marked manual because that is what it is — I did not automate it.

---

## 8. Re-curating community names

Clustering gives you `Community 0 .. Community N`. Naming them is a human pass — write a
`{"0": "Name", ...}` JSON and apply it:

    GRAPHIFY_CORPUS=/path/to/papers python scripts/apply_labels.py labels.json

That rebuilds `GRAPH_REPORT.md`, rewrites `graph.json` with `community_name` on every node, and
saves `.graphify_labels.json`. See `sample/community-labels.json` for the 61 labels this run used.

## 9. Asking "how does A relate to B"

    python scripts/relate.py <id_prefix_a> <id_prefix_b>

Reads `graph.json` directly: prints the direct cross-paper edges, the shortest path between the
two paper nodes, both ego-neighbourhoods, and the community each node sits in.

---

## Measured intermediate sizes (this run)

| Artifact | Bytes |
| --- | --- |
| `.graphify_extract.json` | 847,052 |
| `.graphify_semantic.json` | 847,052 |
| `.graphify_semantic_new.json` | 851,255 |
| `graph.json` | 880,765 |
| `GRAPH_REPORT.md` | 36,595 |
| `graph.html` | 1,401,501 |

Chunk files (`.graphify_chunk_01..13.json`) ranged 35 KB–146 KB. **Build wall-clock time is not
reported** — there is no timestamped log, so it is left as unknown rather than guessed.
