from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "math-modeling-workflow" / "scripts" / "init_workspace.py"
SPEC = importlib.util.spec_from_file_location("init_workspace", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class WorkspaceInitializationTest(unittest.TestCase):
    def test_initialization_is_non_destructive_and_reentrant(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "demo"
            first = MODULE.initialize(target)
            session = target / "planning" / "session_config.json"
            self.assertTrue(first)
            self.assertTrue(session.exists())
            config = json.loads(session.read_text(encoding="utf-8"))
            self.assertEqual(config["rigor_profile"], "lean")
            session.write_text('{"preserved": true}\n', encoding="utf-8")
            second = MODULE.initialize(target)
            self.assertEqual(session.read_text(encoding="utf-8"), '{"preserved": true}\n')
            self.assertEqual(second, [])


if __name__ == "__main__":
    unittest.main()
