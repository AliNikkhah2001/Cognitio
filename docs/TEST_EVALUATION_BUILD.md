# Build, test, and evaluation plan

## Required local gates

Legacy baseline:

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy lythic
pytest --cov=lythic --cov-report=term-missing
```

Target core:

```bash
python -m pip install -e ".[dev]"
ruff check src tests
ruff format --check src tests
mypy src/cognitio
pytest -m "not e2e" --cov=cognitio --cov-report=term-missing
```

Target web packages:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm test:e2e
```

## Test pyramid

| Level | Required evidence |
|---|---|
| Unit | parser cases, IDs, link resolution, graph transforms, filters, reducers |
| Property | arbitrary paths/frontmatter/wikilinks never crash or escape vault |
| Integration | Markdown ↔ index ↔ service, watcher updates, migration and rebuild |
| Contract | identical provider behavior for local/fake/Nodum implementations |
| UI component | editor commands, graph events, labels, filters, empty/error states |
| End-to-end | create, edit, link, rename, search, graph-open, ghost-create, recovery |
| Visual | IMPERIUM themes, glass modes, high DPI, narrow/wide layouts |
| Performance | indexing, query latency, graph build, frame time, memory, bundle size |
| Security | traversal, unsafe links/HTML, secrets, dependency and license audit |

## Fixture vault matrix

- [ ] Empty vault
- [ ] One note
- [ ] Duplicate filenames in separate directories
- [ ] Circular links and self-links
- [ ] Unresolved links and aliases
- [ ] Unicode, RTL, spaces, emoji, and normalization variants
- [ ] Frontmatter arrays, dates, malformed YAML, and very large properties
- [ ] Attachments and unsupported binaries
- [ ] Concurrent external file modification
- [ ] Corrupt or stale index
- [ ] 1k, 10k, and 50k synthetic graphs

## Performance budgets to ratify

Initial budgets are hypotheses, not claims:

| Scenario | Provisional budget |
|---|---:|
| Open an already-indexed 10k-note vault | p95 < 2 s |
| Search indexed 10k-note vault | p95 < 100 ms backend time |
| Incremental single-file update | p95 < 250 ms |
| Local graph depth 2 | p95 < 150 ms backend time |
| Graph interaction at 10k visible nodes | median >= 45 FPS on reference hardware |
| Editor input latency | p95 < 50 ms |

Record the reference machine and dataset with every benchmark. Adjust budgets only in an ADR or roadmap change, never to make a failing PR appear green.

## Manual evaluation journeys

- [ ] Clone IMPERIUM recursively and launch from documented commands.
- [ ] Select an existing Markdown vault without modifying its content.
- [ ] Create two same-named notes in different folders and link both correctly.
- [ ] Create an unresolved link, see its ghost node, then create the destination.
- [ ] Rename a linked note and verify backlinks plus recovery behavior.
- [ ] Search, open from results, open from graph, and return without losing camera state.
- [ ] Change IMPERIUM theme/glass mode while editor and graph are open.
- [ ] Edit a file externally and observe safe refresh/conflict behavior.
- [ ] Delete the derived index and successfully rebuild it.
- [ ] Simulate process termination during autosave and verify recovery.

## CI stages

1. License and dependency policy
2. Python lint/format/type
3. Python unit/property/integration/contract tests
4. Web lint/type/unit/build
5. Desktop bridge and packaging smoke tests
6. UI end-to-end and visual regression
7. Scheduled large-vault performance suite

No performance or UI claim belongs in the README unless its measurement is reproducible from this plan.
