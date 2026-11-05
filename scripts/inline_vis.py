#!/usr/bin/env python3
"""Stage 5 - inline the vis-network bundle into graphify's graph.html.

graphify's HTML export loads vis-network from a CDN (unpkg.com), so the file is
dead the moment you open it without a network. This script rewrites that
<script src=...> tag into an inline <script> holding a local copy of the bundle,
so graph.html becomes a single self-contained file you can open offline (and
screenshot for the vault's PNG preview).

Idempotent: re-running it does nothing once inlined. The first run keeps a
backup of the CDN version as graph.html.orig so you can diff or revert.

You supply the bundle yourself - no third-party code is shipped in this repo.
Download vis-network (9.1.6 is what the original run used) and point at it:

    VIS_NETWORK_JS=/path/to/vis-network.min.js python inline_vis.py
"""
from pathlib import Path
import os, re, sys

HTML = Path("graphify-out/graph.html")                              # rewritten in place
JS = Path(os.environ.get("VIS_NETWORK_JS", "vis-network.min.js"))   # your local bundle

html = HTML.read_text(encoding="utf-8")

# Find the CDN tag the exporter wrote.
m = re.search(r'<script[^>]*src="https://unpkg\.com/[^"]*"[^>]*></script>', html)
if not m:
    print("no unpkg <script src> tag found - already inlined or format changed")
    print("external refs remaining:", len(re.findall(r'(?:src|href)="https?://', html)))
    sys.exit(0)

tag = m.group(0)
js = JS.read_text(encoding="utf-8")

# Keep the CDN version once, so you can diff or revert.
# (index by name + ".orig" rather than Path.with_suffix - a multi-dot suffix is
# not accepted by with_suffix on every Python version.)
backup = HTML.parent / (HTML.name + ".orig")
if not backup.exists():
    backup.write_text(html, encoding="utf-8")

inline = "<script>\n/* vis-network 9.1.6 UMD, inlined for offline use */\n" + js + "\n</script>"
out = html.replace(tag, inline)
HTML.write_text(out, encoding="utf-8")

# Prove it worked: nothing should load over the network any more.
remaining = re.findall(r'(?:src|href)="https?://[^"]*"', out)
print(f"tag was: {tag}")
print(f"inlined {len(js):,} chars of JS")
print(f"graph.html: {len(html):,} -> {len(out):,} chars")
print(f"external refs remaining: {len(remaining)} {remaining[:3]}")
