#!/usr/bin/env python
"""Answer "how does A relate to B" straight out of graph.json.

Usage: python relate.py <id_prefix_a> <id_prefix_b>
  (defaults: genception / robot_learning_a_tutorial)

graphify builds node ids as <paper_slug>_<concept>, so an id *prefix* selects a
whole paper. Reads graph.json, then prints:
  - the direct cross-paper edges (with relation + EXTRACTED/INFERRED),
  - the shortest path between the two paper nodes,
  - each paper's ego-neighbourhood and the community every node sits in.

This is the "so what" step: it is how I check whether two papers are actually
connected, or just co-cited by the clustering.
"""
import json, sys
from pathlib import Path
import networkx as nx
from networkx.readwrite import json_graph

A = sys.argv[1] if len(sys.argv) > 1 else "genception"
B = sys.argv[2] if len(sys.argv) > 2 else "robot_learning_a_tutorial"

data = json.loads(Path("graphify-out/graph.json").read_text(encoding="utf-8"))
# graph.py writes node-link JSON with the edge list under "links" (not "edges").
G = json_graph.node_link_graph(data, edges="links")


def eattr(u, v):
    raw = G[u][v]
    d = next(iter(raw.values()), {}) if isinstance(G, nx.MultiGraph) else raw
    return d.get("relation", "?"), d.get("confidence", "?"), d.get("confidence_score", "?")


def label(n):
    return G.nodes[n].get("label", n)


def src(n):
    return Path(G.nodes[n].get("source_file") or "?").name


ap = [n for n in G if n.startswith(A)]
bp = [n for n in G if n.startswith(B)]
print(f"A-nodes: {len(ap)}  B-nodes: {len(bp)}  (total {G.number_of_nodes()} nodes / {G.number_of_edges()} edges)")

print("\n== DIRECT CROSS-PAPER EDGES ==")
found = 0
for u, v in G.edges():
    if (u in ap and v in bp) or (u in bp and v in ap):
        rel, conf, score = eattr(u, v)
        found += 1
        print(f"  {label(u)} [{src(u)}]\n    --{rel}--> ({conf} {score}) {label(v)} [{src(v)}]")
print(f"  ({found} direct edges)")

print("\n== SHORTEST PATH between the two paper nodes ==")
pa = f"{A}_paper" if f"{A}_paper" in G else (ap[0] if ap else None)
pb = f"{B}_paper" if f"{B}_paper" in G else (bp[0] if bp else None)
if pa and pb:
    try:
        path = nx.shortest_path(G, pa, pb)
        print(f"  {len(path)-1} hops:")
        for i, n in enumerate(path):
            if i < len(path) - 1:
                rel, conf, score = eattr(n, path[i + 1])
                print(f"   {label(n)}  --{rel}--> ({conf} {score})")
            else:
                print(f"   {label(n)}")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        print("  no path:", e)

for tag, nodes in (("A", ap), ("B", bp)):
    print(f"\n== {tag} NODES (community) ==")
    for n in sorted(nodes):
        print(f'  [{G.nodes[n].get("community_name", G.nodes[n].get("community"))}] '
              f"{label(n)} | deg={G.degree(n)} | {src(n)}")
