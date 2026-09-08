#!/usr/bin/env python3
"""Deterministic gate enforcer for a mathematical-modeling workspace.

The workflow Skills describe gates G0-G6 in prose, which an LLM can skip under
time pressure. This script turns the gate *evidence contract* into code:

* ``status``  evaluates, per active question, the highest gate actually backed
  by artifacts on disk and compares it with the self-reported manifest gate and
  ``allowed`` flags. A manifest that runs ahead of the evidence is an integrity
  violation (exit code 2), not merely "work in progress".
* ``guard``   is the hard pre-action check. Run it before generating model code,
  freezing results, writing paper sections, or running final assembly; missing
  evidence makes the command fail (exit code 1).

Only the Python standard library is used. Gate evaluation is a pure function of
a collected evidence dict so it can be unit-tested without a filesystem.

Canonical artifact paths mirror the Skills under ``../skills`` (problem-parser,
method-selector, model-code-analyzer, python/matlab-code-reviewer,
solution-package-builder, paper-section-writer, full-paper-assembler,
national-modeling-paper-formatter and the three final auditors).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ordered gate ladder. G5.5/G5.6/G6 are global gates evaluated once per workspace.
QUESTION_GATES = ["G0", "G1", "G2", "G2.5", "G3", "G4", "G5"]
GLOBAL_GATES = ["G5.5", "G5.6", "G6"]
ALL_GATES = QUESTION_GATES + GLOBAL_GATES
GATE_ORDER = {gate: index for index, gate in enumerate(ALL_GATES)}

# Authorized decision makers for gate advancement: human or autonomous agent
VALID_DECIDED_BY = {"human", "autonomous_agent", "agent", "agent_auto"}

REQUIRED_REVIEW_CHECKS = [
    "syntax",
    "input_contract",
    "method_alignment",
    "reproducibility",
    "output_contract",
]

# Action -> minimum question gate that must be evidenced on disk.
ACTION_REQUIRES = {
    "code_generation": "G2.5",
    "freeze": "G3",
    "paper_writing": "G4",
    "final_assembly": "G5",  # required for EVERY active question
}

GLOBAL_MASTER_FILES = [
    "paper/master/cross_question_matrix.md",
    "paper/master/assembly_manifest.json",
    "paper/master/claim_map.json",
    "paper/master/renumber_map.json",
    "paper/master/full_paper.md",
]
FINAL_AUDITS = [
    "paper/audits/cross_media_consistency_audit.md",
    "paper/audits/completeness_audit.md",
    "paper/audits/qa_report.md",
]

PLACEHOLDER = re.compile(r"todo|tbd|placeholder|待补充|待定|占位", re.IGNORECASE)
ROUND_SUFFIX = re.compile(r"round[_\s]*(\d+)$", re.IGNORECASE)


@dataclass
class GateResult:
    """Evaluation outcome for one gate."""

    gate: str
    passed: bool
    missing: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def fail(self, reason: str) -> "GateResult":
        self.passed = False
        self.missing.append(reason)
        return self


# --------------------------------------------------------------------------- #
# Small parsing helpers (pure)
# --------------------------------------------------------------------------- #
def _find_subquestion(parse_doc: dict[str, Any], qid: str) -> dict[str, Any] | None:
    for item in parse_doc.get("subquestions", []) or []:
        if str(item.get("id", "")).upper() == qid.upper():
            return item
    return None


def _find_classification(class_doc: dict[str, Any], qid: str) -> dict[str, Any] | None:
    for item in class_doc.get("subquestions", []) or []:
        if str(item.get("id", "")).upper() == qid.upper():
            return item
    return None


_find_subclassification = _find_classification


def active_decisions(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Collapse an append-only JSONL ledger to the latest live decision per type.

    A later ``decision_stale`` record (naming the old id via ``stale_of`` or
    ``supersedes``) invalidates an earlier decision; a fresh DECIDED record of
    the same decision_type then takes over.
    """
    live: dict[str, dict[str, Any]] = {}
    stale_ids: set[str] = set()
    decided: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        dtype = record.get("decision_type")
        if dtype == "decision_stale":
            for key in ("stale_of", "supersedes", "target_decision_id"):
                if record.get(key):
                    stale_ids.add(str(record[key]))
            continue
        # Human-owned or autonomous agent decisions advance a gate.
        decided_by = str(record.get("decided_by", "")).lower()
        if record.get("status") == "DECIDED" and decided_by in VALID_DECIDED_BY:
            decided.append(record)
    for record in decided:
        if record.get("decision_id") and record["decision_id"] in stale_ids:
            continue
        if record.get("supersedes"):
            stale_ids.add(str(record["supersedes"]))
        if dtype := record.get("decision_type"):
            live[dtype] = record
    # Drop decisions invalidated by a supersede encountered later.
    for record in decided:
        did = record.get("decision_id")
        if did and did in stale_ids and live.get(record.get("decision_type")) is record:
            live.pop(record["decision_type"], None)
    return live


def latest_round_name(round_dirs: list[str]) -> str | None:
    """Return the highest roundN directory name among experiment round dirs."""
    best_name: str | None = None
    best_index = -1
    for name in round_dirs:
        match = ROUND_SUFFIX.search(name)
        index = int(match.group(1)) if match else 0
        if index >= best_index:
            best_index, best_name = index, name
    return best_name


# --------------------------------------------------------------------------- #
# Pure gate evaluation
# --------------------------------------------------------------------------- #
def _passed(gate: str, missing: list[str] | None = None, notes: list[str] | None = None) -> GateResult:
    return GateResult(gate, not missing, missing or [], notes or [])


def evaluate_question_gates(ev: dict[str, Any], profile: str) -> dict[str, GateResult]:
    """Evaluate G0-G5 for one question from a collected evidence dict."""
    submission = profile == "submission"
    results: dict[str, GateResult] = {}
    qid = ev["qid"]

    # G0 — manifest exists.
    results["G0"] = _passed("G0") if ev.get("manifest_exists") else GateResult(
        "G0", False, [f"planning/manifests/{qid}.json missing"]
    )

    # G1 — problem framed, classified, data profiled, human framing when ambiguous.
    missing: list[str] = []
    notes: list[str] = []
    parse = ev.get("parse")
    if not ev.get("parse_exists"):
        missing.append("planning/parse/problem_parse.json missing")
    elif not isinstance(parse, dict) or _find_subquestion(parse, qid) is None:
        missing.append(f"problem_parse.json has no subquestion entry for {qid}")
    else:
        subq = _find_subquestion(parse, qid)
        if not subq.get("required_outputs"):
            missing.append(f"{qid} parse: required_outputs is empty")
        if not subq.get("success_criteria"):
            missing.append(f"{qid} parse: human success_criteria is empty")
        ambiguities = subq.get("ambiguities") or []
    classification = ev.get("classification")
    if not ev.get("classification_exists"):
        missing.append("planning/classification/problem_classification.json missing")
    elif not isinstance(classification, dict) or _find_subclassification(classification, qid) is None:
        missing.append(f"problem_classification.json has no entry for {qid}")
    needs_framing = False
    if isinstance(classification, dict) and (cls := _find_subclassification(classification, qid)):
        if str(cls.get("confidence", "")).lower() not in {"high", ""}:
            needs_framing = True
    if ev.get("ambiguities"):
        needs_framing = True
    if "data_profile" in ev.get("waivers", []):
        notes.append("data_profile waived (data-free question declared in manifest waivers)")
    elif not ev.get("data_profile_exists"):
        missing.append("workspace/data/data_profile.json missing (waive via manifest waivers:[\"data_profile\"] for a data-free question)")
    else:
        readiness = ev.get("data_readiness")
        if readiness is not None and readiness not in {"ready", "ready_with_warnings"}:
            missing.append(f"data readiness for {qid} is '{readiness}', not ready/ready_with_warnings")
    if needs_framing and not ev.get("framing_decided"):
        missing.append("ambiguous framing requires a human 'framing' DECIDED record in the decision ledger")
    results["G1"] = _passed("G1", missing, notes)

    # G2 — method card + risk probe for main and usable baseline.
    missing = []
    if not ev.get("method_card_exists"):
        missing.append(f"methods/{qid}/qx_method_card.md missing")
    else:
        card = ev.get("method_card_text", "").lower()
        if not ("main" in card):
            missing.append("method card does not name a main candidate")
        if not ("baseline" in card):
            missing.append("method card does not name a usable baseline")
    probe = ev.get("risk_probe")
    if not ev.get("risk_probe_exists"):
        missing.append(f"methods/{qid}/probes/risk_probe_summary.json missing")
    elif not isinstance(probe, dict):
        missing.append("risk_probe_summary.json is not a valid JSON object")
    else:
        methods = probe.get("methods") or []
        roles = {str(m.get("role", "")).lower() for m in methods if isinstance(m, dict)}
        verdicts = [str(m.get("verdict", "")).upper() for m in methods if isinstance(m, dict)]
        if not any("baseline" in role for role in roles):
            missing.append("risk probe has no usable_baseline entry")
        if not any("main" in role for role in roles):
            missing.append("risk probe has no main entry")
        if any(v == "FAIL" for v in verdicts):
            missing.append("risk probe contains a FAIL verdict for main/baseline")
        elif not any(v in {"PASS", "CONDITIONAL"} for v in verdicts):
            missing.append("risk probe has no PASS/CONDITIONAL verdict")
    results["G2"] = _passed("G2", missing)

    # G2.5 — human or autonomous method choice recorded and evidence-linked.
    decisions = ev.get("decisions", {})
    method_choice = decisions.get("method_choice")
    missing = []
    if not method_choice:
        missing.append(f"no DECIDED method_choice in methods/{qid}/qx_decisions.jsonl")
    elif str(method_choice.get("decided_by", "")).lower() not in VALID_DECIDED_BY:
        missing.append("method_choice decided_by is not 'human' or 'autonomous_agent'")
    elif not method_choice.get("evidence_refs"):
        missing.append("method_choice has no evidence_refs (must cite the risk probe)")
    results["G2.5"] = _passed("G2.5", missing)

    # G3 — code plan, successful main+baseline run, named-check review passed.
    missing = []
    if not ev.get("code_plan_exists"):
        missing.append("code plan missing (code/Qx/qx_code_plan.md or code/matlab/Qx/qx_code_plan.md)")
    run_summary = ev.get("latest_run_summary")
    if not ev.get("run_summary_exists"):
        missing.append("no results/Qx/experiments/roundN/run_summary.json")
    elif not isinstance(run_summary, dict):
        missing.append("latest run_summary.json is invalid JSON")
    else:
        ran = [m for m in run_summary.get("methods", []) if isinstance(m, dict)]
        ok = [m for m in ran if m.get("status") == "success"]
        roles = {str(m.get("role", "")).lower() for m in ran}
        if len(ok) < 2 or not any("main" in r for r in roles) or not any("baseline" in r for r in roles):
            missing.append("run summary must show successful main AND usable_baseline runs")
    review = ev.get("review")
    if not ev.get("review_exists"):
        missing.append("language code review JSON missing (code/Qx/reviews or code/matlab/Qx/reviews)")
    elif not isinstance(review, dict):
        missing.append("code review JSON is invalid")
    else:
        checks = review.get("checks", {})
        for name in REQUIRED_REVIEW_CHECKS:
            status = str((checks.get(name) or {}).get("status", "")).upper()
            if status == "FAIL":
                missing.append(f"review check '{name}' = FAIL")
            elif status == "NOT_RUN":
                missing.append(f"review check '{name}' = NOT_RUN (blocks G3 until executed)")
            elif status not in {"PASS", "NOT_APPLICABLE"}:
                missing.append(f"review check '{name}' missing or not PASS/NOT_APPLICABLE")
            elif status == "NOT_APPLICABLE" and not (checks.get(name) or {}).get("reason"):
                missing.append(f"review check '{name}' is NOT_APPLICABLE without a reason")
        if str(review.get("verdict", "")).upper() != "PASSED":
            missing.append(f"code review verdict is '{review.get('verdict')}', expected PASSED")
    results["G3"] = _passed("G3", missing)

    # G4 — result judged (both profiles); submission additionally freezes evidence.
    missing = []
    if not decisions.get("result_verdict"):
        missing.append("no DECIDED result_verdict in the decision ledger")
    if submission:
        if not ev.get("final_method_explanation_exists"):
            missing.append(f"methods/{qid}/qx_final_method_explanation.md missing")
        if not ev.get("final_result_analysis_exists"):
            missing.append("results/Qx/reports/qx_final_result_analysis.md missing")
        if not ev.get("robustness_report_exists"):
            missing.append("robustness/Qx/qx_robustness_report.md missing")
        if not ev.get("solution_package_exists"):
            missing.append("results/Qx/reports/qx_solution_package_for_writer.md missing")
        if not decisions.get("package_signoff"):
            missing.append("no DECIDED package_signoff; freeze is not authorized")
        frozen = ev.get("frozen_numbers")
        if not ev.get("frozen_exists"):
            missing.append("results/Qx/reports/frozen_numbers.json missing")
        elif not isinstance(frozen, list) or not frozen:
            missing.append("frozen_numbers.json contains no frozen entries")
        else:
            for entry in frozen:
                source = entry.get("source_file") if isinstance(entry, dict) else None
                if source and not (ev["workspace"] / source).exists():
                    missing.append(f"frozen entry '{entry.get('claim_id', '?')}' cites missing source_file: {source}")
    # A failed/conditional robustness check requires an explicit stability verdict.
    if ev.get("robustness_needs_verdict") and not decisions.get("stability_verdict"):
        missing.append("robustness evidence is CONDITIONAL/FAIL but no stability_verdict exists")
    results["G4"] = _passed("G4", missing)

    # G5 — per-question paper section (submission only).
    missing = []
    notes = []
    if not submission:
        notes.append("submission-only gate, not evaluated in lean")
    if submission:
        if not ev.get("paper_section_exists"):
            missing.append("paper/sections/Qx/qx_model_and_results.md missing")
        if not ev.get("section_manifest_exists"):
            missing.append("paper/sections/Qx/qx_section_manifest.json missing")
        if not decisions.get("claim_scope"):
            missing.append("no DECIDED claim_scope for paper claims")
        if ev.get("plan_has_paper_figures") and not ev.get("paper_figures_present"):
            missing.append("figure plan declares Type 3/4 figures but paper/figures/Qx has no outputs")
    results["G5"] = _passed("G5", missing, notes)
    return results


def _find_subclassification(doc: dict[str, Any], qid: str) -> dict[str, Any] | None:
    for item in doc.get("subquestions", []) or []:
        if str(item.get("id", "")).upper() == qid.upper():
            return item
    return None


def evaluate_global_gates(ev: dict[str, Any], profile: str, all_questions_at_g5: bool) -> dict[str, GateResult]:
    """Evaluate workspace-wide gates G5.5, G5.6, G6 (submission-only)."""
    results: dict[str, GateResult] = {}
    if profile != "submission":
        for gate in GLOBAL_GATES:
            results[gate] = GateResult(gate, False, notes=["submission-only gate, skipped in lean"])
        return results
    missing = [path for path in GLOBAL_MASTER_FILES if not (ev["workspace"] / path).exists()]
    manifest_path = ev["workspace"] / "paper/master/assembly_manifest.json"
    if manifest_path.exists():
        try:
            assembly = json.loads(manifest_path.read_text(encoding="utf-8"))
            if assembly.get("paper_scope") != "full_submission":
                missing.append("assembly_manifest paper_scope must be 'full_submission'")
            mapping = assembly.get("question_mapping", {})
            targets = [v.get("target_section") for v in mapping.values() if isinstance(v, dict)]
            if len(targets) != len(set(targets)):
                missing.append("assembly_manifest target_section values are not unique")
            active = ev.get("active_questions", [])
            if active and not all(q in mapping for q in active):
                missing.append("assembly_manifest question_mapping does not cover every active question")
        except json.JSONDecodeError as exc:
            missing.append(f"assembly_manifest.json is invalid JSON: {exc}")
    if not all_questions_at_g5:
        missing.append("not every active question has reached G5")
    # Automated paper-rigor-gatekeeper pre-flight check on full_paper.md
    rigor_script = Path(__file__).resolve().parent / "audit_paper_rigor.py"
    master_paper = ev["workspace"] / "paper/master/full_paper.md"
    if rigor_script.exists() and master_paper.exists():
        import subprocess
        res = subprocess.run([sys.executable, str(rigor_script), "--file", str(master_paper)], capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            missing.append("paper-rigor-gatekeeper audit failed: text-formula, DoE matrix, or threshold inconsistencies detected")
    # Automated narrative & de-AI anti-cliché audit check on full_paper.md
    narrative_script = Path(__file__).resolve().parent / "audit_paper_narrative.py"
    if narrative_script.exists() and master_paper.exists():
        import subprocess
        res_narrative = subprocess.run([sys.executable, str(narrative_script), "--file", str(master_paper)], capture_output=True, text=True, encoding="utf-8")
        if res_narrative.returncode != 0:
            missing.append("narrative & de-AI audit failed: AI clichés, evasion wording, or weak interface sentences detected")
    results["G5.5"] = _passed("G5.5", missing)

    missing = []
    for final_file in ("paper/final/final_paper.docx", "paper/final/final_paper.pdf"):
        if not (ev["workspace"] / final_file).exists():
            missing.append(f"{final_file} missing")
    rendered = ev["workspace"] / "paper/final/rendered_pages"
    if not rendered.is_dir() or not any(rendered.iterdir()):
        missing.append("paper/final/rendered_pages/ is empty (page-by-page visual inspection evidence)")
    results["G5.6"] = _passed("G5.6", missing)

    missing = []
    if profile == "submission":
        for audit in FINAL_AUDITS:
            path = ev["workspace"] / audit
            if not path.exists():
                missing.append(f"{audit} missing")
                continue
            text = path.read_text(encoding="utf-8", errors="replace").upper()
            if "PASSED" not in text:
                missing.append(f"{audit} has no PASSED verdict")
            if re.search(r"VERDICT[^\n]*\b(FAILED|NOT_RUN)\b", text):
                missing.append(f"{audit} final verdict is FAILED/NOT_RUN")
    results["G6"] = _passed("G6", missing)
    return results


def highest_reached(gate_results: dict[str, GateResult], ladder: list[str]) -> str:
    """Highest consecutive gate that passes (a failed gate blocks later ones)."""
    highest = "G0"
    for gate in ladder:
        if gate_results[gate].passed:
            highest = gate
        else:
            break
    return highest


# --------------------------------------------------------------------------- #
# Evidence collection (filesystem IO)
# --------------------------------------------------------------------------- #
def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def collect_question_evidence(workspace: Path, qid: str, waivers: list[str]) -> dict[str, Any]:
    """Collect every on-disk signal a question gate decision depends on."""
    ev: dict[str, Any] = {"workspace": workspace, "qid": qid, "waivers": waivers}
    ql = qid.lower()
    ev["manifest_exists"] = (workspace / "planning/manifests" / f"{qid}.json").exists()

    parse_path = workspace / "planning/parse/problem_parse.json"
    ev["parse_exists"] = parse_path.exists()
    ev["parse"] = _read_json(parse_path)
    ev["ambiguities"] = bool(
        isinstance(ev["parse"], dict)
        and (subq := _find_subquestion(ev["parse"], qid))
        and subq.get("ambiguities")
    )

    class_path = workspace / "planning/classification/problem_classification.json"
    ev["classification_exists"] = class_path.exists()
    ev["classification"] = _read_json(class_path)

    profile_path = workspace / "workspace/data/data_profile.json"
    ev["data_profile_exists"] = profile_path.exists()
    profile_doc = _read_json(profile_path) if ev["data_profile_exists"] else None
    readiness = None
    if isinstance(profile_doc, dict):
        readiness = (profile_doc.get("per_question_readiness") or {}).get(qid)
        if isinstance(readiness, dict):
            readiness = readiness.get("status")
    ev["data_readiness"] = readiness

    # Human decisions: per-question ledger, with global framing ledger as fallback.
    records = _read_jsonl(workspace / f"methods/{qid}/qx_decisions.jsonl")
    records += _read_jsonl(workspace / "planning/framing_decisions.jsonl")
    ev["decisions"] = active_decisions(records)
    ev["framing_decided"] = "framing" in ev["decisions"]

    card_path = workspace / f"methods/{qid}/qx_method_card.md"
    ev["method_card_exists"] = card_path.exists()
    ev["method_card_text"] = card_path.read_text(encoding="utf-8", errors="replace") if card_path.exists() else ""

    probe_path = workspace / f"methods/{qid}/probes/risk_probe_summary.json"
    ev["risk_probe_exists"] = probe_path.exists()
    ev["risk_probe"] = _read_json(probe_path)

    plan_py = workspace / f"code/{qid}/qx_code_plan.md"
    plan_ml = workspace / f"code/matlab/{qid}/qx_code_plan.md"
    ev["code_plan_exists"] = plan_py.exists() or plan_ml.exists()

    exp_root = workspace / f"results/{qid}/experiments"
    round_dirs = [p.name for p in exp_root.iterdir() if p.is_dir()] if exp_root.is_dir() else []
    latest = latest_round_name(round_dirs)
    run_summary_path = exp_root / latest / "run_summary.json" if latest else None
    ev["run_summary_exists"] = bool(run_summary_path and run_summary_path.exists())
    ev["latest_run_summary"] = _read_json(run_summary_path) if ev["run_summary_exists"] else None

    review_py = workspace / f"code/{qid}/reviews/qx_python_review.json"
    review_ml = workspace / f"code/matlab/{qid}/reviews/qx_matlab_review.json"
    review_path = review_py if review_py.exists() else review_ml
    ev["review_exists"] = review_path.exists()
    ev["review"] = _read_json(review_path) if ev["review_exists"] else None

    # Files written before G2.5 are out-of-order artifacts worth surfacing.
    code_dirs = [workspace / f"code/{qid}", workspace / f"code/matlab/{qid}"]
    early = []
    for directory in code_dirs:
        if directory.is_dir():
            early += [str(p.relative_to(workspace)) for p in directory.rglob("*.py")]
            early += [str(p.relative_to(workspace)) for p in directory.rglob("*.m")]
    ev["early_code_files"] = sorted(set(early))

    ev["final_method_explanation_exists"] = (workspace / f"methods/{qid}/qx_final_method_explanation.md").exists()
    ev["final_result_analysis_exists"] = (workspace / f"results/{qid}/reports/qx_final_result_analysis.md").exists()
    ev["robustness_report_exists"] = (workspace / f"robustness/{qid}/qx_robustness_report.md").exists()
    robustness_summary = _read_json(workspace / f"robustness/{qid}/qx_robustness_summary.json")
    needs_stability = False
    if isinstance(robustness_summary, dict):
        blob = json.dumps(robustness_summary, ensure_ascii=False).upper()
        needs_stability = '"STATUS": "CONDITIONAL"' in blob or '"STATUS": "FAIL"' in blob
    ev["robustness_needs_verdict"] = needs_stability
    reports_dir = workspace / f"results/{qid}/reports"
    ev["solution_package_exists"] = (reports_dir / "qx_solution_package_for_writer.md").exists()
    frozen_path = reports_dir / "frozen_numbers.json"
    ev["frozen_exists"] = frozen_path.exists()
    frozen_doc = _read_json(frozen_path) if ev["frozen_exists"] else None
    if isinstance(frozen_doc, dict):
        frozen_doc = frozen_doc.get("numbers") or frozen_doc.get("claims") or []
    ev["frozen_numbers"] = frozen_doc

    section_dir = workspace / f"paper/sections/{qid}"
    ev["paper_section_exists"] = (section_dir / "qx_model_and_results.md").exists()
    ev["section_manifest_exists"] = (section_dir / "qx_section_manifest.json").exists()
    plan_path = workspace / f"methods/{qid}/qx_figure_table_plan.md"
    plan_text = plan_path.read_text(encoding="utf-8", errors="replace") if plan_path.exists() else ""
    ev["plan_has_paper_figures"] = bool(re.search(r"type\s*[34]|类型\s*[34三四]", plan_text, re.IGNORECASE))
    fig_dir = workspace / f"paper/figures/{qid}"
    ev["paper_figures_present"] = fig_dir.is_dir() and any(
        p.suffix.lower() in {".pdf", ".svg", ".png"} for p in fig_dir.rglob("*") if p.is_file()
    )
    return ev


def load_session(workspace: Path) -> dict[str, Any]:
    config = _read_json(workspace / "planning/session_config.json")
    return config if isinstance(config, dict) else {}


def load_manifest(workspace: Path, qid: str) -> dict[str, Any]:
    doc = _read_json(workspace / "planning/manifests" / f"{qid}.json")
    return doc if isinstance(doc, dict) else {}


# --------------------------------------------------------------------------- #
# Workspace evaluation
# --------------------------------------------------------------------------- #
@dataclass
class QuestionStatus:
    qid: str
    gates: dict[str, GateResult]
    highest: str
    violations: list[str]


def evaluate_workspace(workspace: Path, only: str | None = None) -> dict[str, Any]:
    session = load_session(workspace)
    profile = session.get("rigor_profile", "lean")
    active = session.get("active_questions") or []
    if only:
        active = [q for q in active if q == only] or [only]

    questions: dict[str, QuestionStatus] = {}
    for qid in active:
        manifest = load_manifest(workspace, qid)
        waivers = manifest.get("waivers", []) if isinstance(manifest.get("waivers"), list) else []
        ev = collect_question_evidence(workspace, qid, waivers)
        gates = evaluate_question_gates(ev, profile)
        # G5+ are submission-only; a lean workspace tops out at G4.
        question_ladder = QUESTION_GATES if profile == "submission" else QUESTION_GATES[:-1]
        highest = highest_reached(gates, question_ladder)
        violations = _manifest_violations(manifest, gates, highest, ev)
        questions[qid] = QuestionStatus(qid, gates, highest, violations)

    all_at_g5 = bool(questions) and all(
        GATE_ORDER[qs.highest] >= GATE_ORDER["G5"] for qs in questions.values()
    )
    global_ev = {"workspace": workspace, "active_questions": active}
    global_gates = evaluate_global_gates(global_ev, profile, all_at_g5)
    return {
        "profile": profile,
        "active_questions": active,
        "questions": questions,
        "global_gates": global_gates,
    }


def _manifest_violations(manifest: dict[str, Any], gates: dict[str, GateResult], highest: str, ev: dict[str, Any]) -> list[str]:
    """Ways a self-reported manifest can lie about the evidence on disk."""
    violations: list[str] = []
    if not manifest:
        return violations
    reported = manifest.get("current_gate")
    if reported and reported in GATE_ORDER and GATE_ORDER[reported] > GATE_ORDER[highest]:
        violations.append(
            f"manifest current_gate={reported} runs ahead of evidenced gate {highest}"
        )
    allowed = manifest.get("allowed", {}) or {}
    expected = {
        "code_generation": GATE_ORDER[highest] >= GATE_ORDER["G2.5"],
        "freeze": GATE_ORDER[highest] >= GATE_ORDER["G3"],
        "paper_writing": GATE_ORDER[highest] >= GATE_ORDER["G4"],
    }
    for flag, should_be in expected.items():
        if allowed.get(flag) is True and not should_be:
            violations.append(f"manifest allows '{flag}' but evidence only reaches {highest}")
    if GATE_ORDER[highest] < GATE_ORDER["G2.5"] and ev.get("early_code_files"):
        violations.append(
            "model code exists before human method choice (G2.5): " + ", ".join(ev["early_code_files"])
        )
    return violations


def guard(workspace: Path, action: str, qid: str | None) -> tuple[bool, list[str]]:
    """Hard pre-action gate. Returns (allowed, blocking reasons)."""
    state = evaluate_workspace(workspace, qid if action != "final_assembly" else None)
    required = ACTION_REQUIRES[action]
    blockers: list[str] = []
    targets = state["active_questions"]
    if action != "final_assembly":
        if qid is None and len(targets) == 1:
            qid = targets[0]
        if not qid:
            return False, ["--question is required when multiple questions are active"]
        targets = [qid]
    for question in targets:
        qs = state["questions"].get(question)
        if qs is None:
            blockers.append(f"{question}: no manifest / not active in session_config")
            continue
        if GATE_ORDER[qs.highest] < GATE_ORDER[required]:
            failed = qs.gates[qs.highest] if qs.highest in qs.gates else None
            blockers.append(
                f"{question}: action '{action}' needs {required}, evidence reaches {qs.highest}"
            )
            gate = qs.gates.get(required)
            if gate and gate.missing:
                blockers.extend(f"    - {item}" for item in gate.missing)
        blockers.extend(f"{question}: {v}" for v in qs.violations)
    return not blockers, blockers


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def format_status(state: dict[str, Any]) -> str:
    lines = [f"profile: {state['profile']}   active: {', '.join(state['active_questions']) or '(none)'}"]
    for qid, qs in state["questions"].items():
        lines.append(f"\n[{qid}] evidenced highest gate: {qs.highest}")
        for gate in QUESTION_GATES:
            result = qs.gates[gate]
            mark = "PASS" if result.passed else "BLOCK"
            lines.append(f"  {mark:5} {gate}")
            for reason in result.missing:
                lines.append(f"        missing: {reason}")
            for note in result.notes:
                lines.append(f"        note: {note}")
        for violation in qs.violations:
            lines.append(f"  !! INTEGRITY: {violation}")
    lines.append("\n[global]")
    for gate in GLOBAL_GATES:
        result = state["global_gates"][gate]
        if any("skipped in lean" in note for note in result.notes):
            lines.append(f"  SKIP  {gate} (submission-only, lean profile)")
            continue
        lines.append(f"  {'PASS' if result.passed else 'BLOCK'} {gate}")
        for reason in result.missing:
            lines.append(f"        missing: {reason}")
    return "\n".join(lines)


def state_to_json(state: dict[str, Any]) -> str:
    payload = {
        "profile": state["profile"],
        "active_questions": state["active_questions"],
        "questions": {
            qid: {
                "highest_gate": qs.highest,
                "gates": {g: {"passed": r.passed, "missing": r.missing, "notes": r.notes} for g, r in qs.gates.items()},
                "violations": qs.violations,
            }
            for qid, qs in state["questions"].items()
        },
        "global_gates": {
            g: {"passed": r.passed, "missing": r.missing} for g, r in state["global_gates"].items()
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="Project workspace root")
    sub = parser.add_subparsers(dest="command", required=True)

    status_parser = sub.add_parser("status", help="Evaluate gates from on-disk evidence (default view)")
    status_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    guard_parser = sub.add_parser("guard", help="Hard pre-action enforcement")
    guard_parser.add_argument("--action", required=True, choices=sorted(ACTION_REQUIRES))
    guard_parser.add_argument("--question", help="Question id (e.g. Q1); omit only for final_assembly")
    guard_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"workspace not found: {workspace}", file=sys.stderr)
        return 2

    if args.command == "guard":
        allowed, blockers = guard(workspace, args.action, args.question)
        if args.json:
            print(json.dumps({"action": args.action, "allowed": allowed, "blockers": blockers}, ensure_ascii=False, indent=2))
        elif allowed:
            print(f"GUARD PASS: '{args.action}' is authorized by on-disk evidence.")
        else:
            print(f"GUARD BLOCK: '{args.action}' is not yet authorized:", file=sys.stderr)
            for item in blockers:
                print(item, file=sys.stderr)
        return 0 if allowed else 1

    state = evaluate_workspace(workspace)
    print(state_to_json(state) if args.json else format_status(state))
    integrity = [v for qs in state["questions"].values() for v in qs.violations]
    return 2 if integrity else 0


if __name__ == "__main__":
    raise SystemExit(main())
