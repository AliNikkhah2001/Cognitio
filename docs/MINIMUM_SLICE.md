# Minimum working slice

This slice proves that IMPERIUM can load Cognitio from its pinned submodule and use a stable, Qt-free service boundary.

## Implemented

- [x] Importable `cognitio.KnowledgeService`
- [x] Importable `modules.cognitio.KnowledgeService` from an IMPERIUM checkout
- [x] Existing-directory vault validation
- [x] Recursive UTF-8 Markdown discovery
- [x] Path-based IDs that keep duplicate filenames distinct
- [x] Title, tag and wikilink extraction
- [x] Search across title, path and content
- [x] Raw note reading
- [x] Explicit graph edges
- [x] Unresolved wikilinks represented as ghost nodes
- [x] JSON-safe bootstrap payload
- [x] Unit tests with no Qt dependency
- [x] Minimal GitHub Actions gate
- [x] Atomic Markdown create/save with optimistic revision checks
- [x] Hashtags represented as graph hub nodes
- [x] Explainable local keyword/tag connection suggestions
- [x] Graph payload verified above 120 nodes without truncation

## Intentionally deferred

- [ ] SQLite/FTS provider migration from legacy Lythic
- [ ] Incremental filesystem watcher
- [ ] Rename, trash and full conflict-recovery UI
- [ ] Atomic-derived editor
- [ ] Nodum-derived WebGL graph
- [ ] Semantic edges and analytics

The service rescans Markdown in memory. Create and save use path containment, same-directory temporary files, atomic replacement, and optimistic revisions; rename and trash remain deferred. Its public response format is designed so the scanner can later be replaced by the derived SQLite index.

## Verify

```bash
python -m unittest discover -s tests/unit -p "test_cognitio_service.py" -v
```

From an IMPERIUM recursive checkout:

```bash
python -c "from modules.cognitio import KnowledgeService; print(KnowledgeService)"
```
