# Upstream code and attribution policy

Cognitio may adapt code from Atomic and Nodum, but it must not blur ownership or make future updates impossible.

## Rules

- [ ] Verify the license at the exact commit before copying.
- [ ] Record repository URL, commit SHA, original paths, copied paths, license, date, and modifications.
- [ ] Preserve copyright and license headers.
- [ ] Add the source to `THIRD_PARTY_NOTICES.md`.
- [ ] Copy the smallest coherent unit; do not import an entire application to save short-term effort.
- [ ] Put Cognitio-owned adapters around upstream code.
- [ ] Never copy trademarks, branding, icons, example vaults, credentials, or hosted-service configuration unless separately permitted.
- [ ] Run dependency, license, security, type, test, and bundle checks.
- [ ] Keep an upstream-update procedure and diff against the pinned commit.

## Planned upstream use

| Upstream | Intended reuse | Explicitly excluded |
|---|---|---|
| Atomic | standalone CodeMirror editor and selected Markdown extensions | product shell, AI orchestration, transport and stores |
| Nodum | Cosmos.gl graph lifecycle, labels, interaction, filters, force controls and persistence | Next.js shell, PostgreSQL queries, authentication, server deployment |
| Lythic legacy | parser, SQLite/FTS, watcher, graph domain and clustering | PySide6 desktop/presentation as the target UI |

## Required notice entry template

```markdown
### <component>

- Upstream: <repository URL>
- Commit: `<full SHA>`
- Original paths: <paths>
- Cognitio paths: <paths>
- License: <license and link>
- Adapted on: <YYYY-MM-DD>
- Modifications: <summary>
```

## Update workflow

- [ ] Create an isolated upstream-update branch.
- [ ] Fetch and compare the last pinned commit to the proposed commit.
- [ ] Review license and dependency changes first.
- [ ] Port upstream fixes through the adapter boundary.
- [ ] Run the full component, integration, visual, performance, and license gates.
- [ ] Update notices and the pinned SHA in the same PR.
