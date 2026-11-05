# What is in `sample/`

One honest slice of the real graph output, published so the shape of the output is visible
without shipping anyone's papers. Read this before reusing it.

| File | What it is |
| --- | --- |
| `graph-slice.json` | One whole community from the real graph (Community 10, "Morphological Design of Soft Robots": 16 nodes, 21 edges), with fields trimmed. |
| `community-labels.json` | The 61 curated community names applied to the graph — the one part of the output that is a human judgement call, not a machine result. |
| `GRAPH_REPORT.excerpt.md` | The header + summary + hub list of the real `GRAPH_REPORT.md` (the generated report, not the papers). |

## What was removed from `graph-slice.json`, and why

graphify stores, per node, not just a label but a `rationale` / `evidence` field holding prose it
pulled from the paper, plus an `author` field with third-party names. Both are other people's
content, so they are **not** here — that is also why the full `graph.json` is not published.

Kept (all structural or bibliographic):

- on nodes: `id`, `label`, `file_type`, `community`, `community_name`, `source_file`
- on edges: `source`, `target`, `relation`, `confidence`

The longest retained string is 129 characters — a node `id` / `source_file` slug (a slugified paper
title). The longest human-readable *label* is 94 characters. No sentence of paper prose survives in
this file.

## Why a whole community and not the "top" nodes

My first attempt sampled the highest-degree nodes; they shared almost no edges (12 nodes, 2 links
— useless as a sample). A single community is internally dense (16 nodes, 21 edges here), so the
slice actually shows what a cluster looks like.

## Provenance

Graph built 2026-09-23 with `graphifyy` 0.9.65 from a 15-document corpus (12 PDF + 3 Markdown).
Full graph: 680 nodes, 913 edges, 27 hyperedges, 61 communities.
