# Cognitio execution roadmap

This is the controlling roadmap for converting the legacy Lythic application into IMPERIUM's contained knowledge submodule. Check an item only when its evidence is linked in the pull request.

## Definition of done for every phase

- [ ] Scope and non-goals are written before implementation.
- [ ] Risks and rollback are recorded.
- [ ] Tests fail before the implementation when practical.
- [ ] Lint, formatting, type checking, unit tests, integration tests, and security checks pass.
- [ ] Performance is measured when the phase changes indexing, rendering, or startup.
- [ ] User-facing behavior is manually evaluated in IMPERIUM.
- [ ] Documentation and attribution are updated.
- [ ] The submodule commit is pinned explicitly in IMPERIUM.
- [ ] The phase PR has a reproducible verification log.

## Phase 0 — Baseline and legal containment

Goal: make the starting point reproducible before refactoring.

- [ ] Add the root MIT license and `THIRD_PARTY_NOTICES.md`.
- [ ] Record Lythic, Atomic, Nodum, Cytoscape, Cosmos.gl, CodeMirror, Graphology, Sigma.js, NetworkX, and SQLite licenses.
- [ ] Tag the untouched legacy baseline as `lythic-legacy-v0.1.0`.
- [ ] Capture supported operating systems and Python/Node versions.
- [ ] Run and record current unit/integration coverage.
- [ ] Add a smoke test that indexes a fixture vault and opens the current application.
- [ ] Create fixture vaults: tiny, duplicate-title, unresolved-link, Unicode, attachment, and 10k-note synthetic.
- [ ] Measure clean index time, incremental update time, query latency, graph build time, peak memory, and startup.
- [ ] Document known defects rather than silently treating README claims as evidence.

Exit gate:

- [ ] A clean machine can reproduce the baseline.
- [ ] Every borrowed-code license is classified as compatible, incompatible, or pending review.
- [ ] The baseline tag and measurements are linked from the PR.

## Phase 1 — Rename and extract the Python core

Goal: establish `cognitio` as a UI-independent package.

- [ ] Move domain, application, parser, repository, watcher, and graph-clustering code under `src/cognitio`.
- [ ] Keep a small deprecated `lythic` compatibility namespace that re-exports supported APIs.
- [ ] Move PySide6, preview, editor, media, and standalone window dependencies to a `legacy-ui` optional extra.
- [ ] Ensure importing `cognitio` does not import either Qt binding.
- [ ] Rename `.lythic/cache.db` to `.cognitio/cache.db` with a safe one-time migration.
- [ ] Use vault-relative normalized paths or stable UUIDs as note IDs; never use filename stems alone.
- [ ] Represent unresolved wikilinks as ghost nodes.
- [ ] Add explicit models for note, block, tag, attachment, link, relation, and graph snapshot.
- [ ] Add schema versioning and index migrations.
- [ ] Preserve compatibility for existing vaults and configuration.

Exit gate:

- [ ] Core unit tests pass without Qt installed.
- [ ] Duplicate filenames in different folders remain distinct.
- [ ] Index deletion and rebuild produces equivalent results.
- [ ] A legacy import test proves the compatibility window.

## Phase 2 — Stable service and provider contracts

Goal: prevent IMPERIUM, Nodum, and the local vault from coupling to implementations.

- [ ] Define `KnowledgeService` and `KnowledgeProvider` protocols.
- [ ] Version every JSON message crossing QWebChannel.
- [ ] Implement `LocalVaultProvider` using Cognitio core.
- [ ] Specify `NodumProvider`, but keep it disabled until local mode passes release gates.
- [ ] Add optimistic save revisions and conflict responses.
- [ ] Add cancellation and request IDs for expensive search/graph work.
- [ ] Emit `noteChanged`, `graphChanged`, `vaultChanged`, and `conflictDetected` events.
- [ ] Validate and limit filesystem paths at the bridge boundary.
- [ ] Define pagination and graph truncation behavior.

Required API operations:

- [ ] `openVault`
- [ ] `listNotes`
- [ ] `readNote`
- [ ] `saveNote`
- [ ] `createNote`
- [ ] `renameNote`
- [ ] `deleteNoteToTrash`
- [ ] `search`
- [ ] `getGraph`
- [ ] `getBacklinks`
- [ ] `resolveLink`

Exit gate:

- [ ] Contract tests run against an in-memory/fake provider and the local provider.
- [ ] Malformed messages fail safely with structured errors.
- [ ] Save conflicts never overwrite newer content.

## Phase 3 — IMPERIUM frontend build boundary

Goal: make TypeScript-based editor and graph code maintainable inside QWebEngine.

- [ ] Choose full Vite migration or a transitional `knowledge.bundle.js` library build.
- [ ] Pin Node, package-manager, TypeScript, React, and Vite versions.
- [ ] Enable TypeScript strict mode and source maps for development.
- [ ] Create shared visual tokens mapped to IMPERIUM glass modes.
- [ ] Create a single `Knowledge` route and feature flag.
- [ ] Add an error boundary, loading states, empty states, and degraded rendering mode.
- [ ] Make packaged assets work from `file://` and Qt resource URLs.
- [ ] Add bundle-size and missing-asset checks.

Exit gate:

- [ ] The bundle builds offline from the lockfile.
- [ ] QWebEngine loads the component without CDN dependencies.
- [ ] Light/dark and native/frosted/faked glass modes pass screenshots.

## Phase 4 — Atomic-derived editor adapter

Goal: embed a polished Markdown editor without importing Atomic's whole application.

- [ ] Record the exact upstream Atomic Editor commit.
- [ ] Copy or vendor only the standalone editor package and required extensions.
- [ ] Preserve MIT attribution in copied files and notices.
- [ ] Create an `EditorAdapter` interface independent of Atomic stores and transport.
- [ ] Implement wikilinks, aliases, headings, callouts, tasks, tables, code, and frontmatter.
- [ ] Connect open/save/rename events to `KnowledgeService`.
- [ ] Add autosave debounce, dirty state, crash recovery, and conflict UI.
- [ ] Add keyboard navigation and accessibility testing.

Exit gate:

- [ ] Round-trip fixtures preserve Markdown bytes except for an explicitly requested formatting command.
- [ ] A crash/restart test recovers unsaved content.
- [ ] Link rename updates are atomic or safely recoverable.

## Phase 5 — Nodum-derived graph package

Goal: reuse Nodum's hard-won WebGL interaction code behind a host-neutral component.

- [ ] Record the exact upstream Nodum commit and source files.
- [ ] Preserve MIT headers and document meaningful modifications.
- [ ] Extract renderer lifecycle, camera, force settings, labels, LOD, filters, hover, search, ghost nodes, time controls, and incremental placement.
- [ ] Remove Next.js routing, TanStack Query fetching, Nodum settings mutations, and Nodum-specific UI components.
- [ ] Split the large component into canvas, controls, labels, engine hook, types, and store.
- [ ] Accept normalized `GraphPayload` input only.
- [ ] Expose `onOpenNode`, `onCreateGhost`, `onSettingsChange`, and focus callbacks.
- [ ] Add WebGL-loss recovery and a small-vault accessible list fallback.
- [ ] Keep renderer state across tab changes and incremental graph updates.

Exit gate:

- [ ] Unit tests cover transformations, filters, labels, and event mapping.
- [ ] Interaction tests cover open, hover, focus, ghost creation, zoom, and filters.
- [ ] Benchmarks meet agreed frame-time and memory budgets at 1k, 10k, and 50k nodes.

## Phase 6 — Unified Knowledge experience

Goal: make Cognitio feel native to IMPERIUM.

- [ ] Merge the existing Notes and Markdown workflows behind a migration-safe Knowledge tab.
- [ ] Add explorer, editor/reader, graph, backlinks, properties, outline, and related-notes panels.
- [ ] Add Edit, Read, Split, Local Graph, Global Graph, and Editor + Graph modes.
- [ ] Clicking a graph node opens the note; hovering a wikilink highlights its graph node.
- [ ] Clicking a ghost node offers note creation.
- [ ] Map IMPERIUM goals, habits, courses, flashcards, quizzes, and files to optional typed graph nodes.
- [ ] Persist pane layout, graph camera, filters, and last-open note.
- [ ] Add first-run vault selection and safe import guidance.

Exit gate:

- [ ] Critical user journeys pass end-to-end on all supported platforms.
- [ ] Existing IMPERIUM data and tabs remain recoverable through the migration period.
- [ ] Visual regression baselines are approved.

## Phase 7 — Optional Nodum remote provider

Goal: connect collaborative server workspaces without making them mandatory.

- [ ] Verify Nodum's current public API and pin its version.
- [ ] Implement authentication/token storage through IMPERIUM's secret boundary.
- [ ] Map Nodum graph/note payloads to Cognitio contracts.
- [ ] Define offline behavior, retries, pagination, rate limits, and conflict UX.
- [ ] Keep local and remote vault identities explicit in the UI.
- [ ] Prohibit silent dual writes.

Exit gate:

- [ ] Provider contract suite passes for local and Nodum providers.
- [ ] Network failure cannot corrupt or mislabel local content.
- [ ] The user can export remote notes to portable Markdown.

## Phase 8 — Semantic and analytical graph

Goal: add Atomic-inspired intelligence only after explicit links are dependable.

- [ ] Define separate edge layers: explicit, inferred, semantic, structural, and activity.
- [ ] Add local embeddings behind an optional provider.
- [ ] Make model, dimensions, normalization, and index version inspectable.
- [ ] Add PageRank, betweenness, connected components, communities, paths, and orphan diagnostics.
- [ ] Display why every inferred or semantic edge exists.
- [ ] Permit disabling and rebuilding all AI-derived data.
- [ ] Measure retrieval quality with a labeled fixture set.

Exit gate:

- [ ] Semantic results are reproducible for a pinned model.
- [ ] No generated relationship is presented as an authored fact.
- [ ] The feature works without sending vault content to a remote service by default.

## Phase 9 — Release qualification

- [ ] Complete threat model and dependency/license scan.
- [ ] Verify backup, restore, corrupt-index recovery, and interrupted-write recovery.
- [ ] Verify clean install, upgrade, uninstall, and submodule checkout instructions.
- [ ] Run Windows, Linux, and macOS test matrix where supported.
- [ ] Run accessibility, keyboard-only, high-DPI, and reduced-motion checks.
- [ ] Publish reproducible performance report and known limits.
- [ ] Remove legacy PySide6 UI from the default package.
- [ ] Decide and document the `lythic` compatibility removal date.
- [ ] Tag Cognitio v0.1 and pin it in an IMPERIUM release candidate.

Release gate:

- [ ] No critical/high security findings.
- [ ] No known data-loss defect.
- [ ] All required CI checks pass from a clean checkout with submodules.
- [ ] Manual acceptance checklist is signed off.
