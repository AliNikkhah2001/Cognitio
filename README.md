# Cognitio

> The local-first knowledge engine for IMPERIUM. Formerly developed as **Lythic**.

**Cognitio** is Latin for knowledge, recognition, and understanding. The name describes the module's job: turn a folder of durable Markdown files into a searchable, navigable, explainable knowledge graph.

This repository is the legacy Lythic codebase being converted into an independently testable submodule embedded at `modules/cognitio` in [IMPERIUM](https://github.com/AliNikkhah2001/IMPERIUM). It is not intended to remain a second desktop application. IMPERIUM owns the window, tabs, navigation, theming, and user experience; Cognitio owns vault parsing, indexing, links, graph queries, and knowledge services.

## Status

The minimum Qt-free knowledge service is integrated into IMPERIUM. The existing `lythic` Python namespace remains temporarily available so the migration can be incremental. Do not treat the historical PySide6 presentation layer or Cytoscape prototype as the target UI.

| Area | Current state | Target state |
|---|---|---|
| Canonical storage | Markdown vault | Markdown vault |
| Search/index | SQLite + FTS5 | Rebuildable SQLite + FTS5 index |
| Knowledge graph | Wikilinks, backlinks, local BFS, Louvain | Typed nodes/edges, ghost nodes, local/global/semantic views |
| Editor | Integrated IMPERIUM Markdown node editor with atomic vault save | Atomic-derived CodeMirror 6 adapter inside IMPERIUM |
| Graph UI | Clustered canvas with tag hubs, degree sizing, pan/zoom | Benchmarked Nodum/Cosmos or Sigma/Graphology WebGL adapter |
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

## IMPERIUM workspace integration

IMPERIUM exposes Cognitio as one unified **Knowledge Workspace**. Its explorer, clustered graph, and Markdown node editor are simultaneous collapsible/resizable panes rather than separate graph/editor tabs. Vault Markdown can be safely created and edited with revision conflicts; existing synchronized IMPERIUM notes also appear as graph nodes and keep their SQLite authority.

Hashtags are rendered as hub nodes, community colors are stable, highly connected nodes are larger and central within a cluster, and the graph payload has no 120-node preview cap. A local, explainable keyword/tag provider suggests related notes and hashtags; it never presents a suggested edge as an authored fact.

The former standalone Notes navigation item is removed. Existing saved `notes` routes migrate to `cognitio` automatically, so upgrades do not open an empty module. The host owns this composition; Cognitio does not import IMPERIUM UI or either Qt binding.

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

- [x] Merge the Cognitio planning and minimum-service work.
- [x] Merge the IMPERIUM submodule integration.
- [x] Rename the GitHub repository to `Cognitio` and update `.gitmodules`.
- [x] Split the Qt-free knowledge service from the historical PySide6 shell.
- [ ] Establish current test, coverage, lint, type, startup, and graph-performance baselines.
- [x] Fix path-stable note IDs and preserve unresolved links as ghost nodes.
- [x] Create the minimum JSON-safe `KnowledgeService` API.
- [ ] Add a Vite + React + TypeScript build boundary for embedded web UI.
- [ ] Adapt Atomic Editor behind `EditorAdapter` after the host TypeScript build boundary.
- [ ] Benchmark and adapt Nodum/Cosmos or Sigma/Graphology behind `KnowledgeGraphProps`.
- [x] Integrate vault Markdown and existing IMPERIUM notes in one graph-editor workspace.
- [ ] Complete the remaining release gates.

## Non-goals for the first release

- Reimplementing all of Obsidian.
- Shipping two Qt desktop shells.
- Copying Nodum's complete Next.js/PostgreSQL stack.
- Importing Atomic's complete AI workflow before basic note integrity is proven.
- Bidirectional synchronization without conflict semantics and recovery tests.
- Claiming large-vault readiness without reproducible benchmarks.

## License

Cognitio is MIT-licensed. Adapted upstream files must also retain their applicable notices. See [LICENSE](LICENSE) and [upstream policy](docs/UPSTREAM_CODE_POLICY.md).
