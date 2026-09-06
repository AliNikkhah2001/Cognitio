# Third-party notices

This ledger must be completed with exact commit SHAs before upstream code is copied into Cognitio.

## Existing dependencies and bundled assets

| Component | Upstream | Use | License verification |
|---|---|---|---|
| Cytoscape.js | https://github.com/cytoscape/cytoscape.js | Legacy graph renderer bundle | [ ] verify bundled version and notice |
| NetworkX | https://github.com/networkx/networkx | Graph algorithms and Louvain communities | [ ] record installed version and license |
| markdown-it-py | https://github.com/executablebooks/markdown-it-py | Markdown parsing/rendering | [ ] record installed version and license |
| watchdog | https://github.com/gorakhargosh/watchdog | Filesystem events | [ ] record installed version and license |
| SQLite | https://www.sqlite.org/ | Rebuildable index/FTS | [ ] record distribution status |

## Planned adapted code

No Atomic or Nodum source is included by this planning commit.

### Atomic Editor

- Upstream: https://github.com/kenforthewin/atomic-editor
- Commit: **not pinned yet**
- Intended code: standalone CodeMirror editor and selected Markdown extensions
- License: [ ] verify at selected commit
- Modifications: remove Atomic application stores/transport; add Cognitio adapter and IMPERIUM theme contract

### Nodum graph

- Upstream: https://github.com/nodummd/nodum
- Commit: **not pinned yet**
- Intended code: Cosmos.gl renderer lifecycle, labels, LOD, forces, filters, camera persistence, ghost-node interactions
- License: [ ] verify at selected commit
- Modifications: remove Next.js/API/settings coupling; accept normalized graph props and callbacks

See `docs/UPSTREAM_CODE_POLICY.md` for the mandatory import and update procedure.
