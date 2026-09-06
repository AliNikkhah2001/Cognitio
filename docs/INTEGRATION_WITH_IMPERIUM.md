# Integration with IMPERIUM

## Repository containment

IMPERIUM includes this repository as a pinned Git submodule:

```text
IMPERIUM/
└── modules/
    └── cognitio/  -> AliNikkhah2001/Lythic during legacy migration
```

The folder is named `cognitio` immediately. The remote repository may remain `Lythic` until the GitHub rename is performed; GitHub redirects normally preserve old clone URLs, but `.gitmodules` must still be updated deliberately and tested.

Clone and update:

```bash
git clone --recurse-submodules https://github.com/AliNikkhah2001/IMPERIUM.git
git submodule update --init --recursive
git -C modules/cognitio status
```

## Integration strategy

Do not import the legacy PySide6 application into IMPERIUM. PySide6 and PyQt6 must not own competing application objects in one process.

Instead:

1. Extract the Python knowledge core so it has no Qt import.
2. Instantiate `KnowledgeService` from IMPERIUM's Python process.
3. Expose a narrow `KnowledgeBridge` through the existing QWebChannel.
4. Build the editor and graph packages into IMPERIUM's web assets.
5. Mount a Knowledge route in the existing React application.

## Proposed bridge

Requests:

- `knowledgeOpenVault(path)`
- `knowledgeListNotes(cursor, filters)`
- `knowledgeReadNote(noteId)`
- `knowledgeSaveNote(noteId, content, expectedRevision)`
- `knowledgeCreateNote(title, parentPath)`
- `knowledgeRenameNote(noteId, newPath)`
- `knowledgeTrashNote(noteId)`
- `knowledgeSearch(query, cursor)`
- `knowledgeGraph(centerId, depth, filters)`
- `knowledgeBacklinks(noteId)`

Signals:

- `knowledgeNoteChanged(event)`
- `knowledgeGraphChanged(event)`
- `knowledgeVaultChanged(event)`
- `knowledgeConflictDetected(event)`

Every envelope includes `schemaVersion`, `requestId`, `vaultId`, and structured error data.

## UI layout

| Region | Content |
|---|---|
| Left | vault, folders, notes, tags, saved views |
| Center | edit, read, split, local graph, global graph, editor + graph |
| Right | properties, outline, backlinks, related notes, graph selection |

The Knowledge tab is introduced behind a feature flag. Existing Notes and Markdown tabs remain available until migration and recovery paths are verified.

## Integration checklist

- [ ] Submodule initializes from a clean IMPERIUM clone.
- [ ] IMPERIUM records the exact Cognitio commit in every integration PR.
- [ ] Python import paths do not depend on the current working directory.
- [ ] Cognitio core imports without PySide6 installed.
- [ ] QWebChannel exposes no arbitrary filesystem operation.
- [ ] Frontend assets are bundled locally and load without a CDN.
- [ ] Feature flag can disable Cognitio without breaking startup.
- [ ] Removing/rebuilding the local index does not remove Markdown.
- [ ] Existing notes are migrated or explicitly left untouched; never silently duplicated.
- [ ] Update/rollback instructions include the previous submodule SHA.

## Updating the pin

```bash
git -C modules/cognitio fetch origin
git -C modules/cognitio checkout <reviewed-cognitio-sha>
git add modules/cognitio
git commit -m "chore(cognitio): update submodule pin"
```

Never point IMPERIUM at an unreviewed floating branch in a release.
