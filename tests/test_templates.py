from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/math-modeling-workflow"
TEMPLATE = PLUGIN / "assets/workspace-template/planning"
SCHEMAS = PLUGIN / "assets/schemas"
GATE_SCRIPT = PLUGIN / "scripts/gate_check.py"
SPEC = importlib.util.spec_from_file_location("gate_check_tpl", GATE_SCRIPT)
gate_check = importlib.util.module_from_spec(SPEC)
sys.modules["gate_check_tpl"] = gate_check
assert SPEC and SPEC.loader
SPEC.loader.exec_module(gate_check)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class TemplateContractTest(unittest.TestCase):
    def test_session_template_is_valid_and_lean(self):
        config = load(TEMPLATE / "session_config.json")
        for key in ("schema_version", "rigor_profile", "code_language", "random_seed", "active_questions"):
            self.assertIn(key, config)
        self.assertEqual(config["rigor_profile"], "lean")
        self.assertIn(config["code_language"], {"python", "matlab"})

    def test_manifest_template_starts_blocked(self):
        manifest = load(TEMPLATE / "manifests/Q1.json")
        self.assertEqual(manifest["current_gate"], "G0")
        self.assertFalse(any(manifest["allowed"].values()))
        self.assertTrue(manifest["blockers"])

    def test_manifest_schema_gate_enum_matches_enforcer(self):
        schema = load(SCHEMAS / "manifest.schema.json")
        enum_gates = set(schema["properties"]["current_gate"]["enum"])
        self.assertEqual(enum_gates, set(gate_check.ALL_GATES))

    def test_manifest_schema_declares_data_waiver(self):
        schema = load(SCHEMAS / "manifest.schema.json")
        self.assertIn("waivers", schema["properties"])
        self.assertEqual(schema["properties"]["waivers"]["items"]["enum"], ["data_profile"])

    def test_action_requirements_reference_real_gates(self):
        for action, gate in gate_check.ACTION_REQUIRES.items():
            self.assertIn(gate, gate_check.ALL_GATES, action)


if __name__ == "__main__":
    unittest.main()
