from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/math-modeling-workflow/scripts/validate_repo.py"
SPEC = importlib.util.spec_from_file_location("validate_repo", SCRIPT)
vr = importlib.util.module_from_spec(SPEC)
sys.modules["validate_repo"] = vr
assert SPEC and SPEC.loader
SPEC.loader.exec_module(vr)


class FrontmatterTest(unittest.TestCase):
    def test_basic(self):
        fields, problems = vr.frontmatter("---\nname: foo-bar\ndescription: hi there\n---\nbody\n")
        self.assertEqual(fields["name"], "foo-bar")
        self.assertEqual(fields["description"], "hi there")
        self.assertEqual(problems, [])

    def test_crlf_and_bom_tolerated(self):
        text = "﻿---\r\nname: foo-bar\r\ndescription: d\r\n---\r\n"
        fields, problems = vr.frontmatter(text)
        self.assertEqual(fields["name"], "foo-bar")
        self.assertEqual(problems, [])

    def test_value_with_colon_kept(self):
        fields, _ = vr.frontmatter('---\nname: x\ndescription: "role: main"\n---\n')
        self.assertEqual(fields["description"], "role: main")

    def test_missing_closing_delimiter_reported(self):
        _, problems = vr.frontmatter("---\nname: x\nbody without close\n")
        self.assertTrue(any("closing" in p for p in problems))

    def test_duplicate_key_reported(self):
        _, problems = vr.frontmatter("---\nname: x\nname: y\n---\n")
        self.assertTrue(any("duplicate" in p for p in problems))


class RoutingRegistryTest(unittest.TestCase):
    def test_shipped_registry_matches_disk(self):
        skills_root = ROOT / "plugins/math-modeling-workflow/skills"
        disk = {p.name for p in skills_root.iterdir() if p.is_dir()}
        self.assertEqual(vr.validate_routing_registry(disk), [])
        self.assertEqual(len(disk), sum(len(v) for v in vr.STAGE_ROUTES.values()))

    def test_unregistered_skill_is_caught(self):
        disk = {name for stage in vr.STAGE_ROUTES.values() for name in stage}
        disk.add("brand-new-skill")
        errors = vr.validate_routing_registry(disk)
        self.assertTrue(any("brand-new-skill" in e for e in errors))

    def test_ghost_route_is_caught(self):
        disk = {name for stage in vr.STAGE_ROUTES.values() for name in stage}
        disk.discard("robustness-checker")
        errors = vr.validate_routing_registry(disk)
        self.assertTrue(any("robustness-checker" in e for e in errors))


class OrchestratorReferenceTest(unittest.TestCase):
    def test_unknown_reference_caught(self):
        text = "route to `ghost-skill` next, then `method-selector`."
        errors = vr.validate_orchestrator_references(text, {"method-selector"})
        self.assertTrue(any("ghost-skill" in e for e in errors))

    def test_known_reference_passes(self):
        text = "route to `method-selector` or $problem-parser next."
        self.assertEqual(vr.validate_orchestrator_references(text, {"method-selector", "problem-parser"}), [])


if __name__ == "__main__":
    unittest.main()
