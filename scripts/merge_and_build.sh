#!/usr/bin/env bash
# graphify merge + build runbook for a papers corpus.
#
# Cheap to re-run: it merges whatever chunk files exist, then builds the graph.
# It overwrites graph.json / GRAPH_REPORT.md, but the build refuses to shrink the
# graph, so it will not silently replace a bigger graph with a smaller one.
#
# Usage:
#   GRAPHIFY_CORPUS=/path/to/papers bash merge_and_build.sh
#
# The interpreter is the one graphify recorded in graphify-out/.graphify_python.
set -euo pipefail

cd "$(dirname "$0")/.."                       # project root (holds graphify-out/)

PY="$(cat graphify-out/.graphify_python)"     # the exact venv python graphify ran under

# The corpus directory graphify scanned. This MUST be the scan root: build_from_json
# derives each node id's prefix from it, so passing the project dir instead silently
# re-keys every node (e.g. 'raw_papers_brickcraft_...') and breaks community lookups.
export GRAPHIFY_CORPUS="${GRAPHIFY_CORPUS:-$PWD/raw-papers}"

GRAPHIFY_BIN="${GRAPHIFY_BIN:-graphify}"      # only used for the integrity check at the end

echo "=== corpus: $GRAPHIFY_CORPUS ==="
echo "=== chunk files present ==="
ls -la graphify-out/.graphify_chunk_*.json 2>/dev/null | awk '{print $5, $9}' || true

# ---------------------------------------------------------------------------
# Step B3: merge chunks -> .graphify_semantic_new.json
#   Concatenate every chunk that parses. A chunk that fails to parse is named
#   and skipped, never fatal - one bad chunk costs only that chunk.
# ---------------------------------------------------------------------------
echo "=== Step B3: merge chunks -> .graphify_semantic_new.json ==="
"$PY" -c '
import json, glob
from pathlib import Path
chunks = sorted(glob.glob("graphify-out/.graphify_chunk_*.json"))
all_nodes, all_edges, all_hyperedges = [], [], []
bad = []
for c in chunks:
    try:
        d = json.loads(Path(c).read_text(encoding="utf-8"))
    except Exception as e:
        bad.append((c, str(e)[:80])); continue
    all_nodes += d.get("nodes", []); all_edges += d.get("edges", []); all_hyperedges += d.get("hyperedges", [])
Path("graphify-out/.graphify_semantic_new.json").write_text(json.dumps({
    "nodes": all_nodes, "edges": all_edges, "hyperedges": all_hyperedges,
    "input_tokens": 0, "output_tokens": 0}, indent=2, ensure_ascii=False), encoding="utf-8")
print("Merged %d chunks: %d nodes, %d edges, %d hyperedges"
      % (len(chunks) - len(bad), len(all_nodes), len(all_edges), len(all_hyperedges)))
for c, e in bad: print("SKIPPED (invalid JSON):", c, e)
'

# ---------------------------------------------------------------------------
# Dedupe the merged nodes by id -> .graphify_semantic.json
# ---------------------------------------------------------------------------
echo "=== dedupe nodes -> .graphify_semantic.json ==="
"$PY" -c '
import json
from pathlib import Path
new = json.loads(Path("graphify-out/.graphify_semantic_new.json").read_text(encoding="utf-8"))
seen = set(); dedup = []
for n in new["nodes"]:
    if n["id"] not in seen:
        seen.add(n["id"]); dedup.append(n)
Path("graphify-out/.graphify_semantic.json").write_text(json.dumps({
    "nodes": dedup, "edges": new["edges"], "hyperedges": new["hyperedges"],
    "input_tokens": 0, "output_tokens": 0}, indent=2, ensure_ascii=False), encoding="utf-8")
print("deduped nodes: %d (from %d)" % (len(dedup), len(new["nodes"])))
'

# ---------------------------------------------------------------------------
# Part C: merge AST (structure) + semantic (LLM) -> .graphify_extract.json
#   AST ids win where they collide: structural nodes are the ground truth.
# ---------------------------------------------------------------------------
echo "=== Part C: merge AST + semantic -> .graphify_extract.json ==="
"$PY" -c '
import json
from pathlib import Path
ast = json.loads(Path("graphify-out/.graphify_ast.json").read_text(encoding="utf-8"))
sem = json.loads(Path("graphify-out/.graphify_semantic.json").read_text(encoding="utf-8"))
seen = {n["id"] for n in ast["nodes"]}
merged_nodes = list(ast["nodes"])
for n in sem["nodes"]:
    if n["id"] not in seen:
        merged_nodes.append(n); seen.add(n["id"])
merged = {"nodes": merged_nodes, "edges": ast["edges"] + sem["edges"],
          "hyperedges": sem.get("hyperedges", []), "input_tokens": 0, "output_tokens": 0}
Path("graphify-out/.graphify_extract.json").write_text(
    json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
print("Merged: %d nodes, %d edges" % (len(merged_nodes), len(merged["edges"])))
'

# ---------------------------------------------------------------------------
# Step 4: build graph, cluster, analyze, report
#   to_json() will REFUSE to write a graph with fewer nodes than the file on
#   disk. If you really mean to shrink it, move graph.json aside first.
# ---------------------------------------------------------------------------
echo "=== Step 4: build graph, cluster, analyze, report ==="
"$PY" -c '
import json, os
from pathlib import Path
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json

CORPUS = os.environ["GRAPHIFY_CORPUS"]
extraction = json.loads(Path("graphify-out/.graphify_extract.json").read_text(encoding="utf-8"))
detection  = json.loads(Path("graphify-out/.graphify_detect.json").read_text(encoding="utf-8"))

G = build_from_json(extraction, root=CORPUS, directed=False)
if G.number_of_nodes() == 0:
    print("ERROR: Graph is empty - extraction produced no nodes."); raise SystemExit(1)

communities = cluster(G)
cohesion = score_all(G, communities)
tokens = {"input": 0, "output": 0}          # real usage is not exposed; see cost.json note
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {cid: "Community " + str(cid) for cid in communities}
questions = suggest_questions(G, communities, labels)

wrote = to_json(G, communities, "graphify-out/graph.json")
if not wrote:
    print("REFUSED to shrink graph.json (existing graph has more nodes). Move it aside if intended.")
    raise SystemExit(1)

report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens,
                  CORPUS, suggested_questions=questions)
Path("graphify-out/GRAPH_REPORT.md").write_text(report, encoding="utf-8")
Path("graphify-out/.graphify_analysis.json").write_text(json.dumps({
    "communities": {str(k): v for k, v in communities.items()},
    "cohesion": {str(k): v for k, v in cohesion.items()},
    "gods": gods, "surprises": surprises, "questions": questions},
    indent=2, ensure_ascii=False), encoding="utf-8")
print("Graph: %d nodes, %d edges, %d communities"
      % (G.number_of_nodes(), G.number_of_edges(), len(communities)))
'

# ---------------------------------------------------------------------------
# Integrity check + outputs
# ---------------------------------------------------------------------------
echo "=== integrity check (CLI) ==="
"$GRAPHIFY_BIN" diagnose multigraph --graph graphify-out/graph.json 2>&1 | tail -15 || true

echo "=== outputs ==="
ls -la graphify-out/graph.json graphify-out/GRAPH_REPORT.md graphify-out/graph.html 2>/dev/null || true
