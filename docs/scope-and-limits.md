# Scope and limits

Read this before filing an issue. This is one person's pipeline, published so the shape of it is
visible and reusable. It is not a product, not a package, and not a fork of graphify.

## What it is not

- **Not general.** The scripts assume a corpus folder and an existing `graphify-out/`; they do not
  create one from scratch. The vault layout is *my* layout.
- **Not one command.** The stages are separate on purpose — there is no orchestrator.
- **Not tested.** No test suite, no CI, no fixtures, no config file.
- **Not a graphify fork.** graphify is credited, not vendored. None of its code is copied here.
- **Not reproducible from this repo alone.** The corpus is other people's papers and is not
  included, so you cannot rebuild *this exact* graph from what is here.

## Honest failure modes (all hit in the real run)

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Graph is empty - extraction produced no nodes` | extraction wrote nothing usable | check the `.graphify_chunk_*.json` files parse; re-extract |
| `REFUSED to shrink graph.json` | the new build has fewer nodes than the file on disk | move the old `graph.json` aside if shrinking is intended |
| community lookups fail / ids change | `root=` was not the corpus dir | pass the corpus path as `root=` (see `apply_labels.py`) |
| `graph.html` blank, network errors | vis-network still loaded from the CDN | run `scripts/inline_vis.py` with a local bundle |
| vault notes out of date | exported before the last rebuild | re-run `graphify export obsidian` |
| `INFERRED` edges look wrong | they are model guesses (avg confidence 0.71 here) | check the `[INFERRED]` tags; do not cite them as facts |
| a chunk is silently missing | it failed to parse | the merge step prints `SKIPPED (invalid JSON):` for it |

## Not measured

- **Build wall-clock time** — there is no timestamped log, so it is reported nowhere.
- **Real token cost** — `cost.json` is an *estimate* (`estimated: true`): the harness exposes no
  per-subagent usage, so input is `chars/4` of the text handed to subagents and output is
  `chunk JSON bytes / 3.6`.

## Third-party content deliberately absent

The corpus is other people's papers, and graphify's node objects carry paper-derived prose
(`rationale` / `evidence`, measured up to **725 characters** in this graph) plus third-party author
names. None of that, no PDFs, and no raw `graph.json` / chunk payloads are committed here.
`sample/` holds one field-trimmed slice instead — see `sample/README.md` for exactly what was
removed.
