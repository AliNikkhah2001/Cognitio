"""Tests for the first Qt-free Cognitio service contract."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from cognitio import KnowledgeService


class KnowledgeServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="cognitio_")
        self.root = Path(self.temp_dir.name)
        (self.root / "projects").mkdir()
        (self.root / "archive").mkdir()
        (self.root / "projects" / "plan.md").write_text(
            "# Active Plan\nLinks to [[archive/plan]] and [[Missing Idea]]. #work",
            encoding="utf-8",
        )
        (self.root / "archive" / "plan.md").write_text(
            "# Archived Plan\nBack to [[projects/plan]].",
            encoding="utf-8",
        )
        self.service = KnowledgeService(self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_duplicate_filenames_keep_distinct_path_ids(self) -> None:
        note_ids = {note["id"] for note in self.service.list_notes()}
        self.assertEqual(note_ids, {"archive/plan", "projects/plan"})

    def test_graph_keeps_resolved_and_ghost_links(self) -> None:
        graph = self.service.graph()
        node_ids = {node["id"] for node in graph["nodes"]}
        self.assertIn("archive/plan", node_ids)
        self.assertIn("projects/plan", node_ids)
        self.assertIn("ghost:missing idea", node_ids)
        edges = {(edge["source"], edge["target"]) for edge in graph["edges"]}
        self.assertIn(("projects/plan", "archive/plan"), edges)
        self.assertIn(("projects/plan", "ghost:missing idea"), edges)

    def test_search_and_read_return_json_safe_data(self) -> None:
        results = self.service.list_notes(query="active")
        self.assertEqual([note["id"] for note in results], ["projects/plan"])
        note = self.service.read_note("projects/plan")
        self.assertIn("Missing Idea", note["content"])
        self.assertEqual(note["tags"], ["work"])

    def test_invalid_vault_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            KnowledgeService(self.root / "does-not-exist")

    def test_core_does_not_import_qt(self) -> None:
        imported = set(sys.modules)
        self.assertNotIn("PySide6", imported)
        self.assertNotIn("PyQt6", imported)


if __name__ == "__main__":
    unittest.main()
