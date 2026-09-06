# Cognitio

> The local-first knowledge engine for IMPERIUM. Formerly developed as **Lythic**.

**Cognitio** is Latin for knowledge, recognition, and understanding. The name describes the module's job: turn a folder of durable Markdown files into a searchable, navigable, explainable knowledge graph.

This repository is the legacy Lythic codebase being converted into an independently testable submodule embedded at `modules/cognitio` in [IMPERIUM](https://github.com/AliNikkhah2001/IMPERIUM). It is not intended to remain a second desktop application. IMPERIUM owns the window, tabs, navigation, theming, and user experience; Cognitio owns vault parsing, indexing, links, graph queries, and knowledge services.

## Status

Planning and containment phase. The existing `lythic` Python namespace remains temporarily available so the migration can be incremental. Do not treat the current PySide6 presentation layer or Cytoscape prototype as the target UI.

| Area | Current state | Target state |
|---|---|---|
| Canonical storage | Markdown vault | Markdown vault |
| Search/index | SQLite + FTS5 | Rebuildable SQLite + FTS5 index |
| Knowledge graph | Wikilinks, backlinks, local BFS, Louvain | Typed nodes/edges, ghost nodes, local/global/semantic views |
| Editor | PySide6 `QTextEdit` prototype | Atomic-derived CodeMirror 6 React editor inside IMPERIUM |
| Graph UI | Cytoscape HTML prototype | Nodum-derived Cosmos.gl React component inside IMPERIUM |
| Desktop shell | Standalone PySide6 | IMPERIUM PyQt6 + QWebEngine |
| Package name | `lythic` | `cognitio`, with temporary compatibility imports |

## Architectural contract

1. Markdown files are authoritative in local mode.
2. `.cognitio/cache.db` is derived and may always be rebuilt.
3. Cognitio contains no IMPERIUM UI and imports no PyQt6 or PySide6 in its core.
4. UI communication crosses a versioned, JSON-serializable service boundary.
5. Nodum and Atomic code is adapted behind Cognitio-owned interfaces; upstream license notices remain intact.
6. One note has one authoritative writer. Local-vault and remote-Nodum modes are never silently dual-written.
7. Every milestone requires tests, measurements, documentation, and an explicit exit gate.

See:

- [Architecture](docs/ARCHITECTURE.md)
- [IMPERIUM integration contract](docs/INTEGRATION_WITH_IMPERIUM.md)
- [Build, test, and evaluation plan](docs/TEST_EVALUATION_BUILD.md)
- [Upstream code and attribution policy](docs/UPSTREAM_CODE_POLICY.md)
- [Full execution roadmap](ROADMAP.md)
- [Agent execution plan](docs/agents/IMPLEMENTATION_PLAN.md)
- [Historical research archive](RESEARCH-ARCHIVE.md)
- [Source references](REFERENCES.md)

## Target repository layout

```text
cognitio/
├── pyproject.toml
├── src/cognitio/
│   ├── domain/            # notes, links, graph types and invariants
│   ├── application/       # use cases and ports
│   ├── infrastructure/    # Markdown, SQLite, watcher and providers
│   └── api/               # JSON-safe facade used by IMPERIUM
├── web/
│   ├── editor/            # Atomic-derived editor adapter
│   └── graph/             # Nodum-derived graph component
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── performance/
│   └── e2e/
├── THIRD_PARTY_NOTICES.md
└── docs/
```

The present repository does not yet match this layout. The roadmap deliberately separates containment, namespace migration, backend hardening, frontend extraction, host integration, and release qualification.

## Development bootstrap

Current legacy setup:

```bash
git clone --recurse-submodules https://github.com/AliNikkhah2001/IMPERIUM.git
cd IMPERIUM/modules/cognitio
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy lythic
```

After the namespace migration, `mypy lythic` becomes `mypy src/cognitio`; the compatibility package remains only for a documented deprecation window.

## Immediate checklist

- [ ] Merge the Cognitio planning PR in this repository.
- [ ] Merge the IMPERIUM submodule scaffold PR.
- [ ] Rename the GitHub repository from `Lythic` to `Cognitio` when redirects and permissions are confirmed.
- [ ] Update `.gitmodules` to the renamed repository URL.
- [ ] Split PySide6 presentation dependencies from the core install.
- [ ] Establish current test, coverage, lint, type, startup, and graph-performance baselines.
- [ ] Fix path-stable note IDs and preserve unresolved links as ghost nodes.
- [ ] Create the versioned `KnowledgeService` API.
- [ ] Add a Vite + React + TypeScript build boundary for embedded web UI.
- [ ] Adapt Atomic Editor behind `EditorAdapter`.
- [ ] Adapt Nodum graph rendering behind `KnowledgeGraphProps`.
- [ ] Integrate the Knowledge tab and complete release gates.

## Non-goals for the first release

- Reimplementing all of Obsidian.
- Shipping two Qt desktop shells.
- Copying Nodum's complete Next.js/PostgreSQL stack.
- Importing Atomic's complete AI workflow before basic note integrity is proven.
- Bidirectional synchronization without conflict semantics and recovery tests.
- Claiming large-vault readiness without reproducible benchmarks.

## License

Cognitio is MIT-licensed. Adapted upstream files must also retain their applicable notices. See [LICENSE](LICENSE) and [upstream policy](docs/UPSTREAM_CODE_POLICY.md).
