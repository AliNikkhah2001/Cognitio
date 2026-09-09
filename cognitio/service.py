"""Small, dependency-free knowledge service for the first IMPERIUM slice.

This deliberately scans Markdown directly. SQLite/FTS and watcher integration
remain later roadmap work; the API shape can stay stable while the provider is
replaced underneath it.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import threading
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_WIKILINK_RE = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
_TAG_RE = re.compile(r"(?:^|\s)#([\w/-]+)")
_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_IGNORED_PARTS = frozenset({".git", ".obsidian", ".cognitio", ".lythic", "__pycache__"})
_WORD_RE = re.compile(r"[\w-]{3,}", re.UNICODE)
_STOP_WORDS = frozenset(
    {
        "and",
        "are",
        "for",
        "from",
        "into",
        "that",
        "the",
        "this",
        "with",
        "your",
    }
)


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
            "revision": _revision(self.content),
        }


class KnowledgeService:
    """Markdown vault facade with atomic writes and JSON-safe responses."""

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
            "mode": "read-write",
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

    def save_note(
        self, note_id: str, content: str, *, expected_revision: str | None = None
    ) -> dict[str, Any]:
        """Atomically save a note, rejecting stale editor revisions."""
        if not isinstance(content, str):
            raise ValueError("content must be text")
        with self._lock:
            note = self._notes.get(note_id)
        if note is None:
            raise KeyError("note was not found in this vault")
        if expected_revision and expected_revision != _revision(note.content):
            raise ValueError("note changed on disk; reload it before saving")
        _atomic_write(note.absolute_path, content)
        self.refresh()
        return self.read_note(note_id)

    def create_note(
        self, title: str, *, parent_path: str = "", content: str | None = None
    ) -> dict[str, Any]:
        """Create a uniquely named Markdown note inside the vault."""
        clean_title = re.sub(r"\s+", " ", re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title)).strip(" .")
        if not clean_title:
            clean_title = "Untitled Note"
        parent = (self._root / parent_path.strip()).resolve()
        if parent != self._root and self._root not in parent.parents:
            raise ValueError("parent path must stay inside the vault")
        parent.mkdir(parents=True, exist_ok=True)
        candidate = parent / f"{clean_title}.md"
        suffix = 2
        while candidate.exists():
            candidate = parent / f"{clean_title} {suffix}.md"
            suffix += 1
        initial = content if content is not None else f"# {clean_title}\n"
        _atomic_write(candidate, initial, create_only=True)
        self.refresh()
        note_id = candidate.relative_to(self._root).with_suffix("").as_posix()
        return self.read_note(note_id)

    def suggest_connections(self, note_id: str, limit: int = 6) -> dict[str, Any]:
        """Suggest transparent local relationships using tags and weighted keywords."""
        if limit < 1 or limit > 20:
            raise ValueError("limit must be between 1 and 20")
        with self._lock:
            source = self._notes.get(note_id)
            notes = tuple(self._notes.values())
        if source is None:
            raise KeyError("note was not found in this vault")
        source_words = _keywords(source)
        source_tags = set(source.tags)
        ranked: list[tuple[float, _IndexedNote, set[str], set[str]]] = []
        for candidate in notes:
            if candidate.note_id == note_id:
                continue
            shared_words = source_words & _keywords(candidate)
            shared_tags = source_tags & set(candidate.tags)
            score = len(shared_words) + (3 * len(shared_tags))
            if score:
                ranked.append((float(score), candidate, shared_words, shared_tags))
        ranked.sort(key=lambda item: (-item[0], item[1].note_id.casefold()))
        selected = ranked[:limit]
        tag_counts: Counter[str] = Counter(
            tag
            for _, candidate, _, _ in selected
            for tag in candidate.tags
            if tag not in source_tags
        )
        return {
            "noteId": note_id,
            "method": "local-keyword-v1",
            "related": [
                {
                    "id": candidate.note_id,
                    "title": candidate.title,
                    "score": score,
                    "sharedKeywords": sorted(shared_words)[:8],
                    "sharedTags": sorted(shared_tags),
                }
                for score, candidate, shared_words, shared_tags in selected
            ],
            "suggestedTags": [tag for tag, _ in tag_counts.most_common(6)],
        }

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

        tag_labels: dict[str, str] = {}
        for note in notes:
            for tag in note.tags:
                tag_id = f"tag:{tag.casefold()}"
                tag_labels.setdefault(tag_id, tag)
                edge_key = (note.note_id, tag_id)
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)
                edges.append({"source": note.note_id, "target": tag_id, "kind": "tag"})
                degree[note.note_id] = degree.get(note.note_id, 0) + 1
                degree[tag_id] = degree.get(tag_id, 0) + 1

        nodes = [
            {
                "id": note.note_id,
                "title": note.title,
                "path": note.relative_path,
                "kind": "note",
                "degree": degree[note.note_id],
                "unresolved": False,
                "tags": list(note.tags),
                "community": note.tags[0].casefold()
                if note.tags
                else (Path(note.note_id).parts[0].casefold() if "/" in note.note_id else "notes"),
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
        nodes.extend(
            {
                "id": tag_id,
                "title": f"#{label}",
                "kind": "tag",
                "degree": degree[tag_id],
                "unresolved": False,
                "tags": [label],
                "community": label.casefold(),
            }
            for tag_id, label in sorted(tag_labels.items())
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


def _revision(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _keywords(note: _IndexedNote) -> set[str]:
    text = f"{note.title}\n{note.content}".casefold()
    return {
        word for word in _WORD_RE.findall(text) if word not in _STOP_WORDS and not word.isdigit()
    }


def _atomic_write(path: Path, content: str, *, create_only: bool = False) -> None:
    """Write UTF-8 through a same-directory temporary file and atomic replace."""
    if create_only and path.exists():
        raise ValueError("note already exists")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if create_only and path.exists():
            raise ValueError("note already exists")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
