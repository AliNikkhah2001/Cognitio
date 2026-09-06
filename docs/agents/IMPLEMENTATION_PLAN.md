# Agent implementation plan

This file is the execution contract for coding agents. `ROADMAP.md` defines product order; this file defines how work is selected, proven, reviewed, and handed off.

## Before any change

- [ ] Read `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, and the relevant ADRs.
- [ ] Read IMPERIUM's `docs/COGNITIO_INTEGRATION.md` at the pinned host commit.
- [ ] Confirm the current Cognitio and IMPERIUM SHAs.
- [ ] Select exactly one unchecked roadmap slice with measurable acceptance criteria.
- [ ] Identify affected boundaries: storage, parser, index, bridge, editor, graph, host UI.
- [ ] Record data-loss, compatibility, licensing, and rollback risks.
- [ ] Add or update tests before implementation where practical.

## Work package template

```markdown
## COG-<number>: <outcome>

### Scope
- [ ] ...

### Non-goals
- ...

### Acceptance evidence
- [ ] Unit/property tests
- [ ] Integration/contract tests
- [ ] Manual or visual verification
- [ ] Performance measurement if relevant
- [ ] Documentation and attribution

### Rollback
- Previous Cognitio SHA:
- Previous IMPERIUM submodule SHA:
- User-data recovery step:
```

## Required execution sequence

- [ ] Baseline the relevant tests and measurements.
- [ ] Implement the smallest end-to-end vertical slice.
- [ ] Run focused tests.
- [ ] Run the complete repository quality gate.
- [ ] Verify from an IMPERIUM recursive checkout when the host contract changes.
- [ ] Inspect UI output when presentation changes; screenshots alone do not replace interaction tests.
- [ ] Review copied code against `UPSTREAM_CODE_POLICY.md`.
- [ ] Update roadmap checkboxes only for evidence-complete work.
- [ ] Write a handoff containing changed files, commands, results, risks, and next unchecked item.

## Review blockers

- Direct imports from Cognitio core into React or vice versa
- PySide6/PyQt6 imports in the core
- Filename-stem note identity
- SQLite treated as the only copy of prose
- Silent local/remote dual writes
- Unversioned bridge messages
- Network/CDN requirement for packaged desktop UI
- Copied upstream code without commit-level attribution
- Performance claims without datasets and commands
- Checkbox completion without linked evidence

## Handoff template

```markdown
### Outcome

### Commits
- Cognitio:
- IMPERIUM:

### Verification
- Command:
- Result:

### Manual evaluation

### Known risks

### Rollback

### Next unchecked roadmap item
```
