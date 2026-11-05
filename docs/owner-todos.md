# Owner todos

Open items before this is finished:

- [ ] **PNG export.** There is no PNG in the working copy. Either screenshot the inlined
      `graph.html` and drop one in the README, or switch to `graphify <corpus> --svg`. Do not add
      an image link until the file is actually committed.
- [ ] **Vault re-export.** The exported vault (575 notes) predates the final graph (680 nodes).
      Re-run `graphify export obsidian` and re-count the notes.
- [ ] **Build wall-clock time.** Unknown today. Add timestamps to `scripts/merge_and_build.sh` if a
      real number is ever wanted.
- [ ] **graphify version drift.** The scripts call graphify's Python modules directly and are tied
      to `graphifyy` 0.9.65. Re-check the module signatures on upgrade.
- [ ] **Colour groups.** The exported `.obsidian/graph.json` is empty (`{"colorGroups": []}`), so
      the graph opens uncoloured. Add colour groups by `#community/...` if wanted.
