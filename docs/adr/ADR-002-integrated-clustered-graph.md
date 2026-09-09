# ADR-002: Integrated clustered graph workspace

**Status:** accepted for the transitional IMPERIUM frontend  
**Date:** 2026-09-09

## Context

The first host integration rendered at most 120 nodes in a circular SVG and opened the existing editor in a separate mode. That hid the graph while editing, made every note appear equally important, and could not express communities or tag hubs.

Atomic and Nodum are useful upstream references, but their current components depend on bundled React/TypeScript application boundaries that IMPERIUM's transitional script loader does not yet provide. Copying their application components now would couple storage, routing, and renderer lifecycle to the wrong layer.

## Decision

- Keep one Knowledge workspace: explorer, graph canvas, and Markdown node editor remain visible together.
- Make all three vertical panes collapsible, make both dividers draggable, and persist layout locally.
- Return every graph node from the service. Rendering uses canvas, viewport culling, selective labels, pan, and zoom; there is no fixed 120-node data slice.
- Represent hashtags as typed `tag` nodes and note-to-tag edges.
- Give nodes a stable community key. The transitional renderer places communities as separate golden-angle clusters, places the highest-degree member at each cluster center, sizes nodes by degree, then relaxes explicit and tag edges.
- Include existing IMPERIUM SQLite notes as typed note nodes through a host adapter. Their Markdown wikilinks and tags participate in the same graph without silently copying prose into the filesystem vault.
- Add a dependency-free `local-keyword-v1` suggestion provider. It proposes related notes and tags from shared keywords/tags and exposes its evidence. Suggested relationships remain suggestions until the user inserts a wikilink or hashtag.
- Add atomic Markdown create/save operations with path containment and optimistic revision checks.

## Upstream evaluation

No Atomic or Nodum source is copied by this decision.

- Atomic evaluated at `825e223a0e5a272a483b8ec36b7a640d95afba63` (MIT). Its CodeMirror adapter remains the preferred editor source after the Vite/TypeScript boundary exists.
- Nodum evaluated at `e6a50c21c7bdbc63937a23bd606574a64c6681e7` (MIT). Its GPU graph lifecycle remains a candidate for the measured WebGL phase.
- Sigma.js/Graphology remain the smaller WebGL/ForceAtlas2 alternative.
- Leiden is preferred over Louvain for a future analytical community provider because it guarantees connected communities. The transitional stable tag/category grouping is intentionally simpler and inspectable.

## Consequences

The immediate UI behaves like a clustered knowledge map and supports safe editing without adding a CDN or new build dependency. The renderer is suitable for the acceptance fixture and is not a claim of 10k/50k-node readiness. The component boundary remains replaceable by a benchmarked Sigma/Cosmos adapter later.

## Verification

- Service tests cover more than 120 nodes, tag hubs, safe create/save, stale revisions, traversal rejection, and explainable suggestions.
- Host source tests reject the old slice and separate Notes workspace.
- Host visual evaluation must exercise pan, zoom, node selection, editing, all collapse controls, and both resize handles.
