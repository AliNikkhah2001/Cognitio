# AGENTS.md — Cognitio repository contract

## Mission

Convert the legacy Lythic codebase into IMPERIUM's local-first knowledge submodule. The target is not a second desktop shell. Cognitio supplies storage/index/graph services and reusable editor/graph web packages; IMPERIUM owns the application experience.

## Required reading

1. `README.md`
2. `ROADMAP.md`
3. `docs/ARCHITECTURE.md`
4. `docs/INTEGRATION_WITH_IMPERIUM.md`
5. `docs/TEST_EVALUATION_BUILD.md`
6. `docs/UPSTREAM_CODE_POLICY.md`
7. `docs/agents/IMPLEMENTATION_PLAN.md`

## Hard boundaries

- Markdown is authoritative in local mode; the database is rebuildable.
- Core code imports no Qt binding.
- IMPERIUM and Cognitio communicate through versioned contracts.
- One provider is authoritative for each vault.
- New note IDs must be path-stable or UUID-based, never filename stems.
- Unresolved links remain explicit ghost nodes.
- Upstream code requires commit-level attribution and retained license notices.
- Do not mark a roadmap checkbox complete without evidence in the PR.

## Quality commands

Current legacy gate:

```bash
ruff check .
ruff format --check .
mypy lythic
pytest --cov=lythic --cov-report=term-missing
```

Run host-level tests from an IMPERIUM checkout whenever the public service contract, built web assets, or submodule pin changes.

## Git workflow

- Use conventional commits and focused branches.
- Keep Cognitio code changes in this repository.
- Update IMPERIUM's submodule pointer in a separate host PR after the Cognitio commit is reviewable.
- PR descriptions must include exact commands/results, manual evaluation, risks, attribution changes, and rollback SHAs.
- Avoid unrelated cleanup during migration slices.

## Plan of record

`ROADMAP.md` is authoritative. `RESEARCH-ARCHIVE.md` and `REFERENCES.md` are background material, not proof that a feature is implemented.
