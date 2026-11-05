#!/usr/bin/env python
"""Re-apply curated community labels and regenerate the derived outputs.

Clustering hands you `Community 0 .. Community N`; naming them is a human pass.
Write a labels file (`{"0": "Name", ...}`) and run this to:
  - rewrite graphify-out/GRAPH_REPORT.md using the names,
  - rewrite graphify-out/graph.json so every node carries `community_name`,
  - save graphify-out/.graphify_labels.json.

It rebuilds the graph from the *saved* extraction + analysis, so it does NOT
re-cluster. That keeps it cheap and deterministic: same graph, better names.

Usage:
    GRAPHIFY_CORPUS=/path/to/papers python apply_labels.py labels.json
"""
import json, os, sys
from pathlib import Path

from graphify.build import build_from_json
from graphify.cluster import score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json

if len(sys.argv) < 2:
    sys.exit("usage: GRAPHIFY_CORPUS=/path/to/papers python apply_labels.py <labels.json>")

# root= MUST be the scan root (the corpus dir), not the project dir: build_from_json
# rewrites node ids with a directory-derived prefix from root=, so a wrong root silently
# re-keys every node (e.g. 'raw_papers_brickcraft_...') and community lookups then fail.
SCAN = os.environ.get("GRAPHIFY_CORPUS", "raw-papers")

extraction = json.loads(Path("graphify-out/.graphify_extract.json").read_text(encoding="utf-8"))
detection  = json.loads(Path("graphify-out/.graphify_detect.json").read_text(encoding="utf-8"))
analysis   = json.loads(Path("graphify-out/.graphify_analysis.json").read_text(encoding="utf-8"))

labels = {int(k): v for k, v in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")).items()}

G = build_from_json(extraction, root=SCAN, directed=False)
communities = {int(k): v for k, v in analysis["communities"].items()}
cohesion    = {int(k): v for k, v in analysis["cohesion"].items()}

# Reuse the run's token ESTIMATE so the regenerated report header matches the build.
# (cost.json is explicitly `estimated: true` - the harness exposes no per-subagent usage.)
_cost = (json.loads(Path("graphify-out/cost.json").read_text(encoding="utf-8"))
         if Path("graphify-out/cost.json").exists() else {"runs": []})
_last = (_cost.get("runs") or [{}])[-1]
tokens = {"input": _last.get("input_tokens", 0), "output": _last.get("output_tokens", 0)}

questions = suggest_questions(G, communities, labels)
report = generate(G, communities, cohesion, labels, analysis["gods"], analysis["surprises"],
                  detection, tokens, SCAN, suggested_questions=questions)
Path("graphify-out/GRAPH_REPORT.md").write_text(report, encoding="utf-8")
Path("graphify-out/.graphify_labels.json").write_text(
    json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False), encoding="utf-8")

wrote = to_json(G, communities, "graphify-out/graph.json", community_labels=labels)
print("graph.json written:", wrote)
print("nodes", G.number_of_nodes(), "edges", G.number_of_edges(), "communities", len(communities))
