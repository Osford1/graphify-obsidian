# Obsidian: how the graph lands in the vault

The exporter writes a self-contained vault folder — a separate folder of notes that Obsidian opens
directly (mine is kept apart from my main notes vault). `.graphify_obsidian_manifest.json` at the
root lists exactly what was written, so you can tell a fresh export from a stale one.

    obsidian-vault/
    ├── .obsidian/graph.json                # tiny Obsidian config (graph-view settings)
    ├── .graphify_obsidian_manifest.json    # every file written (575 notes + config)
    ├── _COMMUNITY_Community 0.md           # one note per community
    ├── _COMMUNITY_Community 1.md
    ├── ...
    └── <Node Name>.md                      # one note per graph node

## Note format

Every graph node becomes a note named after its label. Frontmatter carries provenance and tags;
the body is the edges.

A **concept** note (`ACT (Action Chunking Transformer).md`):

    ---
    source_file: "pi0.pdf"
    type: "concept"
    community: "Community 13"
    location: "Sec. VI-C, Ref. [57]"
    tags:
      - graphify/concept
      - graphify/EXTRACTED
      - community/Community_13
    ---

    # ACT (Action Chunking Transformer)

    ## Connections
    - [[π₀ A Vision-Language-Action Flow Model for General Robot Control]] - `cites` [EXTRACTED]

    #graphify/concept #graphify/EXTRACTED #community/Community_13

A **paper** note is the same shape with `type: "paper"` and no `location`; its `## Connections`
list is the paper's place in the graph.

## Frontmatter fields

| Field | Meaning |
| --- | --- |
| `source_file` | the corpus file the node came from (e.g. `pi0.pdf`) |
| `type` | `concept`, `rationale`, `paper`, `document`, `code` |
| `community` | the community the node belongs to (its `community_name`) |
| `location` | where in the source it was found (`Sec. VI-C, Ref. [57]`); concepts only |
| `tags` | `graphify/<type>`, `graphify/EXTRACTED` or `graphify/INFERRED`, `community/Community_N` |

## Links

Edges are **wikilinks**, so Obsidian's graph view and backlink pane light up on their own:

    - [[Diffusion Policy]] - `references` [EXTRACTED]

Both the relation (`cites`, `implements`, `references`, `rationale_for`, `shares_data_with`,
`conceptually_related_to`, `semantically_similar_to`, `calls`) and the provenance tag are written
inline. `[INFERRED]` links are the model's guess — in this run the inferred edges averaged 0.71
confidence. Treat them as hypotheses.

## Community notes

One per community, named `_COMMUNITY_Community N.md`:

    ---
    type: community
    cohesion: 0.05
    members: 45
    ---

    # Community 1

    **Cohesion:** 0.05 - loosely connected
    **Members:** 45 nodes

    ## Members
    - [[BRICKCRAFT]] - paper - BrickCraft_2605.07605.pdf
    - [[Diffusion Policy]] - concept - BrickCraft_2605.07605.pdf
    ...

    ## Live Query (requires Dataview plugin)

    ```dataview
    TABLE source_file, type FROM #community/Community_1
    SORT file.name ASC
    ```

    ## Connections to other communities
    - 1 edge to [[_COMMUNITY_Community 5]]

    ## Top bridge nodes
    - [[Diffusion Policy]] - degree 8, connects to 1 community

The `## Live Query` block needs the **Dataview** plugin; without it, it just shows as a code
block. Cohesion below ~0.1 is loose (the note says "loosely connected"); higher cohesion means a
tighter cluster.

## How I open it

1. Obsidian → *Open folder as vault* → pick `obsidian-vault/`.
2. Graph view (`Ctrl/Cmd+G`) for the whole thing; the backlink pane on any note walks its edges.
3. Start from a `_COMMUNITY_` note to browse a topic, or from a paper note to see what it connects
   to.
4. The tags (`#graphify/concept`, `#community/Community_13`, …) make good saved searches.

## The `.obsidian/graph.json`

All the exporter writes is:

    { "colorGroups": [] }

i.e. it does **not** ship colour groups, so the graph starts uncoloured. Colour by the
`#community/...` tag or by `type` yourself if you want the communities visible at a glance.

## Caveat: the vault lags the graph

The manifest listed **575 notes**; the graph has **680 nodes**. The vault was exported
2026-09-22 and the graph rebuilt 2026-09-23 (two papers added). Re-run
`graphify export obsidian` after any rebuild, or the vault is stale.
