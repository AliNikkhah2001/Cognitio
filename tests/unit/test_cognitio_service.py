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

    def test_graph_exposes_tags_as_center_nodes(self) -> None:
        graph = self.service.graph()
        tags = [node for node in graph["nodes"] if node["kind"] == "tag"]
        self.assertEqual(tags[0]["id"], "tag:work")
        self.assertEqual(tags[0]["title"], "#work")
        self.assertIn(
            ("projects/plan", "tag:work", "tag"),
            {(edge["source"], edge["target"], edge["kind"]) for edge in graph["edges"]},
        )

    def test_save_uses_revision_and_refreshes_index(self) -> None:
        note = self.service.read_note("projects/plan")
        saved = self.service.save_note(
            "projects/plan",
            "# Active Plan\n\nNow links to [[archive/plan]]. #work #updated",
            expected_revision=note["revision"],
        )
        self.assertIn("updated", saved["tags"])
        self.assertEqual(
            (self.root / "projects" / "plan.md").read_text(encoding="utf-8"),
            "# Active Plan\n\nNow links to [[archive/plan]]. #work #updated",
        )
        with self.assertRaisesRegex(ValueError, "changed on disk"):
            self.service.save_note(
                "projects/plan", "stale overwrite", expected_revision=note["revision"]
            )

    def test_create_note_rejects_traversal_and_chooses_unique_path(self) -> None:
        created = self.service.create_note("Python / Patterns", parent_path="projects")
        duplicate = self.service.create_note("Python / Patterns", parent_path="projects")
        self.assertEqual(created["id"], "projects/Python Patterns")
        self.assertEqual(duplicate["id"], "projects/Python Patterns 2")
        with self.assertRaisesRegex(ValueError, "inside the vault"):
            self.service.create_note("Escape", parent_path="../outside")

    def test_related_notes_are_explainable_and_deterministic(self) -> None:
        (self.root / "projects" / "python.md").write_text(
            "# Python Automation\nPython work automation scripts and planning. #work #python",
            encoding="utf-8",
        )
        (self.root / "projects" / "cooking.md").write_text(
            "# Cooking\nRecipes, ingredients, and kitchen notes. #food",
            encoding="utf-8",
        )
        self.service.refresh()
        suggestions = self.service.suggest_connections("projects/plan")
        self.assertEqual(suggestions["related"][0]["id"], "projects/python")
        self.assertIn("work", suggestions["related"][0]["sharedTags"])
        self.assertIn("python", suggestions["suggestedTags"])

    def test_graph_has_no_120_node_limit(self) -> None:
        for index in range(150):
            (self.root / "archive" / f"note-{index}.md").write_text(
                f"# Note {index}\n[[projects/plan]] #bulk", encoding="utf-8"
            )
        self.service.refresh()
        graph = self.service.graph()
        self.assertGreaterEqual(len(graph["nodes"]), 155)
        self.assertFalse(graph["truncated"])

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
