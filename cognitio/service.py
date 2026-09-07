"""Small, dependency-free knowledge service for the first IMPERIUM slice.

This deliberately scans Markdown directly. SQLite/FTS and watcher integration
remain later roadmap work; the API shape can stay stable while the provider is
replaced underneath it.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_WIKILINK_RE = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
_TAG_RE = re.compile(r"(?:^|\s)#([\w/-]+)")
_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_IGNORED_PARTS = frozenset({".git", ".obsidian", ".cognitio", ".lythic", "__pycache__"})


@dataclass(frozen=True, slots=True)
class _IndexedNote:
    note_id: str
    title: str
    relative_path: str
    absolute_path: Path
    content: str
    modified_at: float
    tags: tuple[str, ...]
    links: tuple[str, ...]

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.note_id,
            "title": self.title,
            "path": self.relative_path,
            "modifiedAt": self.modified_at,
            "tags": list(self.tags),
        }


class KnowledgeService:
    """Read-only Markdown vault facade with stable JSON-safe responses."""

    schema_version = 1

    def __init__(self, vault_root: str | Path) -> None:
        root = Path(vault_root).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError("vault path must be an existing directory")
        self._root = root
        self._lock = threading.RLock()
        self._notes: dict[str, _IndexedNote] = {}
        self.refresh()

    @property
    def vault_root(self) -> Path:
        return self._root

    def refresh(self) -> dict[str, Any]:
        """Re-scan Markdown. Safe baseline before incremental indexing exists."""
        indexed: dict[str, _IndexedNote] = {}
        for path in sorted(self._root.rglob("*.md"), key=lambda item: item.as_posix().casefold()):
            relative = path.relative_to(self._root)
            if any(part in _IGNORED_PARTS or part.startswith(".") for part in relative.parts):
                continue
            try:
                content = path.read_text(encoding="utf-8")
                modified_at = path.stat().st_mtime
            except (OSError, UnicodeError):
                continue
            relative_path = relative.as_posix()
            note_id = relative.with_suffix("").as_posix()
            heading = _HEADING_RE.search(content)
            title = heading.group(1).strip() if heading else path.stem
            tags = tuple(dict.fromkeys(match.group(1) for match in _TAG_RE.finditer(content)))
            links = tuple(match.group(1).strip() for match in _WIKILINK_RE.finditer(content))
            indexed[note_id] = _IndexedNote(
                note_id=note_id,
                title=title,
                relative_path=relative_path,
                absolute_path=path,
                content=content,
                modified_at=modified_at,
                tags=tags,
                links=links,
            )
        with self._lock:
            self._notes = indexed
        return self.status()

    def status(self) -> dict[str, Any]:
        with self._lock:
            note_count = len(self._notes)
        return {
            "schemaVersion": self.schema_version,
            "provider": "local-markdown",
            "mode": "read-only",
            "vaultPath": str(self._root),
            "noteCount": note_count,
        }

    def list_notes(self, query: str = "", limit: int = 200) -> list[dict[str, Any]]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        needle = query.strip().casefold()
        with self._lock:
            notes = tuple(self._notes.values())
        if needle:
            notes = tuple(
                note
                for note in notes
                if needle in note.title.casefold()
                or needle in note.relative_path.casefold()
                or needle in note.content.casefold()
            )
        return [note.summary() for note in notes[:limit]]

    def read_note(self, note_id: str) -> dict[str, Any]:
        with self._lock:
            note = self._notes.get(note_id)
        if note is None:
            raise KeyError("note was not found in this vault")
        result = note.summary()
        result["content"] = note.content
        result["links"] = list(note.links)
        return result

    def graph(self) -> dict[str, Any]:
        with self._lock:
            notes = tuple(self._notes.values())
        exact = {note.note_id.casefold(): note.note_id for note in notes}
        stems: dict[str, list[str]] = {}
        for note in notes:
            stems.setdefault(Path(note.note_id).name.casefold(), []).append(note.note_id)

        edges: list[dict[str, str]] = []
        ghosts: dict[str, str] = {}
        degree: dict[str, int] = {note.note_id: 0 for note in notes}
        seen_edges: set[tuple[str, str]] = set()
        for note in notes:
            for raw_target in note.links:
                target_key = _normalize_target(raw_target)
                resolved = exact.get(target_key)
                if resolved is None and "/" not in target_key:
                    candidates = stems.get(Path(target_key).name, [])
                    if len(candidates) == 1:
                        resolved = candidates[0]
                if resolved is None:
                    resolved = f"ghost:{target_key}"
                    ghosts.setdefault(resolved, raw_target)
                edge_key = (note.note_id, resolved)
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                edges.append({"source": note.note_id, "target": resolved, "kind": "explicit"})
                degree[note.note_id] = degree.get(note.note_id, 0) + 1
                degree[resolved] = degree.get(resolved, 0) + 1

        nodes = [
            {
                "id": note.note_id,
                "title": note.title,
                "path": note.relative_path,
                "kind": "note",
                "degree": degree[note.note_id],
                "unresolved": False,
                "tags": list(note.tags),
            }
            for note in notes
        ]
        nodes.extend(
            {
                "id": ghost_id,
                "title": label,
                "kind": "ghost",
                "degree": degree[ghost_id],
                "unresolved": True,
                "tags": [],
            }
            for ghost_id, label in sorted(ghosts.items())
        )
        return {
            "schemaVersion": self.schema_version,
            "nodes": nodes,
            "edges": edges,
            "truncated": False,
        }

    def bootstrap(self, query: str = "") -> dict[str, Any]:
        return {
            "status": self.status(),
            "notes": self.list_notes(query=query),
            "graph": self.graph(),
        }


def _normalize_target(target: str) -> str:
    normalized = target.strip().replace("\\", "/")
    if normalized.casefold().endswith(".md"):
        normalized = normalized[:-3]
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.casefold()
