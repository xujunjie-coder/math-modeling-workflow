from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/math-modeling-workflow/scripts/gate_check.py"
SPEC = importlib.util.spec_from_file_location("gate_check", SCRIPT)
gate_check = importlib.util.module_from_spec(SPEC)
sys.modules["gate_check"] = gate_check
assert SPEC and SPEC.loader
SPEC.loader.exec_module(gate_check)


def decision(dtype, did="d1", **extra):
    record = {
        "decision_type": dtype,
        "decision_id": did,
        "status": "DECIDED",
        "decided_by": "human",
        "evidence_refs": ["methods/Q1/probes/risk_probe_summary.json"],
    }
    record.update(extra)
    return record


def evidence_through(level: str, tmp: Path, profile: str = "lean") -> dict:
    """Build evidence dict satisfied through a given gate for table-driven tests."""
    ev = {
        "workspace": tmp,
        "qid": "Q1",
        "waivers": [],
        "manifest_exists": True,
        "parse_exists": True,
        "parse": {"subquestions": [{
            "id": "Q1", "required_outputs": ["ranking"], "success_criteria": ["stable top-k"], "ambiguities": []
        }]},
        "ambiguities": False,
        "classification_exists": True,
        "classification": {"subquestions": [{"id": "Q1", "primary_type": "evaluation", "confidence": "high"}]},
        "data_profile_exists": True,
        "data_readiness": "ready",
        "decisions": {},
        "framing_decided": False,
        "method_card_exists": False,
        "method_card_text": "",
        "risk_probe_exists": False,
        "risk_probe": None,
        "code_plan_exists": False,
        "run_summary_exists": False,
        "latest_run_summary": None,
        "review_exists": False,
        "review": None,
        "early_code_files": [],
        "final_method_explanation_exists": False,
        "final_result_analysis_exists": False,
        "robustness_report_exists": False,
        "robustness_needs_verdict": False,
        "solution_package_exists": False,
        "frozen_exists": False,
        "frozen_numbers": None,
        "paper_section_exists": False,
        "section_manifest_exists": False,
        "plan_has_paper_figures": False,
        "paper_figures_present": False,
    }
    order = ["G0", "G1", "G2", "G2.5", "G3", "G4", "G5"]
    target = gate_check.GATE_ORDER[level]

    def reached(gate):
        return gate_check.GATE_ORDER[gate] <= target

    if reached("G2"):
        ev["method_card_exists"] = True
        ev["method_card_text"] = "## Main candidate\n## Usable baseline"
        ev["risk_probe_exists"] = True
        ev["risk_probe"] = {"methods": [
            {"id": "M0", "role": "usable_baseline", "verdict": "PASS"},
            {"id": "M1", "role": "main_candidate", "verdict": "PASS"},
        ]}
    if reached("G2.5"):
        ev["decisions"]["method_choice"] = decision("method_choice")
    if reached("G3"):
        ev["code_plan_exists"] = True
        ev["run_summary_exists"] = True
        ev["latest_run_summary"] = {"methods": [
            {"method_id": "M0", "role": "usable_baseline", "status": "success"},
            {"method_id": "M1", "role": "main", "status": "success"},
        ]}
        ev["review_exists"] = True
        ev["review"] = {
            "verdict": "PASSED",
            "checks": {name: {"status": "PASS"} for name in gate_check.REQUIRED_REVIEW_CHECKS},
        }
    if reached("G4"):
        ev["decisions"]["result_verdict"] = decision("result_verdict", "rv")
        if profile == "submission":
            ev["final_method_explanation_exists"] = True
            ev["final_result_analysis_exists"] = True
            ev["robustness_report_exists"] = True
            ev["solution_package_exists"] = True
            ev["decisions"]["package_signoff"] = decision("package_signoff", "ps")
            ev["frozen_exists"] = True
            ev["frozen_numbers"] = [{"claim_id": "v", "value": 1.0, "source_file": None}]
    if reached("G5") and profile == "submission":
        ev["paper_section_exists"] = True
        ev["section_manifest_exists"] = True
        ev["decisions"]["claim_scope"] = decision("claim_scope", "cs")
    return ev


class PureLogicTest(unittest.TestCase):
    def test_latest_round_sorts_numerically(self):
        self.assertEqual(gate_check.latest_round_name(["round1", "round10", "round2"]), "round10")
        self.assertIsNone(gate_check.latest_round_name([]))

    def test_active_decisions_supersession(self):
        records = [
            decision("method_choice", "a"),
            decision("method_choice", "b", supersedes="a"),
        ]
        live = gate_check.active_decisions(records)
        self.assertEqual(live["method_choice"]["decision_id"], "b")

    def test_active_decisions_stale_record_invalidates(self):
        records = [
            decision("method_choice", "a"),
            {"decision_type": "decision_stale", "status": "DECIDED", "stale_of": "a"},
        ]
        self.assertNotIn("method_choice", gate_check.active_decisions(records))

    def test_ai_decided_choice_does_not_count(self):
        records = [decision("method_choice", "a", decided_by="ai")]
        self.assertNotIn("method_choice", gate_check.active_decisions(records))

    def test_autonomous_agent_decided_choice_counts(self):
        records = [decision("method_choice", "a", decided_by="autonomous_agent")]
        self.assertIn("method_choice", gate_check.active_decisions(records))


class QuestionGateTest(unittest.TestCase):
    def test_each_gate_unlocks_in_order_lean(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for level in ["G1", "G2", "G2.5", "G3", "G4"]:
                ev = evidence_through(level, tmp)
                gates = gate_check.evaluate_question_gates(ev, "lean")
                for gate in gate_check.QUESTION_GATES:
                    if gate_check.GATE_ORDER[gate] <= gate_check.GATE_ORDER[level]:
                        self.assertTrue(gates[gate].passed, f"{level} should pass {gate}: {gates[gate].missing}")

    def test_g1_requires_human_success_criteria(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = evidence_through("G1", Path(tmp))
            ev["parse"]["subquestions"][0]["success_criteria"] = []
            gates = gate_check.evaluate_question_gates(ev, "lean")
            self.assertFalse(gates["G1"].passed)
            self.assertTrue(any("success_criteria" in m for m in gates["G1"].missing))

    def test_data_profile_waiver(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = evidence_through("G1", Path(tmp))
            ev["data_profile_exists"] = False
            ev["waivers"] = ["data_profile"]
            gates = gate_check.evaluate_question_gates(ev, "lean")
            self.assertTrue(gates["G1"].passed)
            self.assertTrue(any("waived" in n for n in gates["G1"].notes))

    def test_g2_rejects_failed_probe(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = evidence_through("G2", Path(tmp))
            ev["risk_probe"]["methods"][1]["verdict"] = "FAIL"
            gates = gate_check.evaluate_question_gates(ev, "lean")
            self.assertFalse(gates["G2"].passed)

    def test_g3_blocks_on_not_run_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = evidence_through("G3", Path(tmp))
            ev["review"]["checks"]["syntax"]["status"] = "NOT_RUN"
            gates = gate_check.evaluate_question_gates(ev, "lean")
            self.assertFalse(gates["G3"].passed)

    def test_g4_submission_requires_freeze_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev = evidence_through("G4", tmp, profile="submission")
            self.assertTrue(gate_check.evaluate_question_gates(ev, "submission")["G4"].passed)
            ev["frozen_exists"] = False
            self.assertFalse(gate_check.evaluate_question_gates(ev, "submission")["G4"].passed)

    def test_frozen_entry_with_missing_source_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev = evidence_through("G4", tmp, profile="submission")
            ev["frozen_numbers"] = [{"claim_id": "x", "value": 2, "source_file": "results/missing.json"}]
            gates = gate_check.evaluate_question_gates(ev, "submission")
            self.assertTrue(any("missing source_file" in m for m in gates["G4"].missing))


class GuardEndToEndTest(unittest.TestCase):
    def _workspace(self, root: Path, evidence_level: str, profile: str = "lean"):
        def write(rel, obj=None, text=None):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(obj, ensure_ascii=False) if obj is not None else (text or ""), encoding="utf-8")
        write("planning/session_config.json", {
            "schema_version": 1, "rigor_profile": profile, "code_language": "python",
            "random_seed": 2026, "active_questions": ["Q1"]})
        write("planning/manifests/Q1.json", {
            "schema_version": 1, "question_id": "Q1", "rigor_profile": profile,
            "current_gate": evidence_level, "status": "x",
            "allowed": {"code_generation": False, "freeze": False,
                        "paper_writing": False, "final_assembly": False},
            "blockers": [], "next_action": None})
        if gate_check.GATE_ORDER[evidence_level] >= gate_check.GATE_ORDER["G1"]:
            write("planning/parse/problem_parse.json", {"subquestions": [{
                "id": "Q1", "required_outputs": ["r"], "success_criteria": ["s"], "ambiguities": []}]})
            write("planning/classification/problem_classification.json",
                  {"subquestions": [{"id": "Q1", "primary_type": "evaluation", "confidence": "high"}]})
            write("workspace/data/data_profile.json", {"per_question_readiness": {"Q1": "ready"}})
        if gate_check.GATE_ORDER[evidence_level] >= gate_check.GATE_ORDER["G2"]:
            write("methods/Q1/qx_method_card.md", text="## Main\n## Usable baseline")
            write("methods/Q1/probes/risk_probe_summary.json", {"methods": [
                {"id": "M0", "role": "usable_baseline", "verdict": "PASS"},
                {"id": "M1", "role": "main", "verdict": "PASS"}]})
        if gate_check.GATE_ORDER[evidence_level] >= gate_check.GATE_ORDER["G2.5"]:
            write("methods/Q1/qx_decisions.jsonl",
                  text=json.dumps(decision("method_choice"), ensure_ascii=False) + "\n")

    def test_guard_blocks_before_g25(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace(root, "G1")
            allowed, blockers = gate_check.guard(root, "code_generation", "Q1")
            self.assertFalse(allowed)
            self.assertTrue(any("needs G2.5" in b for b in blockers))

    def test_guard_allows_after_g25(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace(root, "G2.5")
            allowed, blockers = gate_check.guard(root, "code_generation", "Q1")
            self.assertTrue(allowed, blockers)

    def test_manifest_running_ahead_is_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace(root, "G2.5")
            manifest = json.loads((root / "planning/manifests/Q1.json").read_text(encoding="utf-8"))
            manifest["current_gate"] = "G4"
            (root / "planning/manifests/Q1.json").write_text(json.dumps(manifest), encoding="utf-8")
            state = gate_check.evaluate_workspace(root)
            self.assertTrue(any("runs ahead" in v for v in state["questions"]["Q1"].violations))

    def test_early_code_is_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace(root, "G1")
            (root / "code/Q1").mkdir(parents=True)
            (root / "code/Q1/q1_main.py").write_text("print('early')", encoding="utf-8")
            state = gate_check.evaluate_workspace(root)
            violations = state["questions"]["Q1"].violations
            self.assertTrue(any("before human method choice" in v and "q1_main.py" in v for v in violations))


if __name__ == "__main__":
    unittest.main()
