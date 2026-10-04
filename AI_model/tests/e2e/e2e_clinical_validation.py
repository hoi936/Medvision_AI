"""Deterministic orchestration for End-to-End Clinical Validation Harness v1."""

from copy import deepcopy

from clinical_schema import normalize_model_findings
from doctor_review_validator import build_review_case
from final_report_generation_validator import FinalReportValidationError, render_final_report
from hermes_report import derive_no_finding_policy, resolve_hermes_skills

from .e2e_helpers import STAGE_ORDER, snapshot_hash, stage_snapshot
from .e2e_invariants import evaluate_invariants
from .e2e_trace_validator import e2e_result


def _doctor_case(case, ai_findings):
    cfg = deepcopy(case.get("doctor_review", {}))
    cfg.setdefault("review_id", f"REVIEW-{case['id']}")
    cfg.setdefault("version", 1)
    cfg.setdefault("status", "completed")
    cfg.setdefault("reviewer_id", "DOC-E2E-1")
    cfg.setdefault("reviewer_source", "authenticated_doctor")
    cfg.setdefault("completed_at", "2026-09-29T10:00:00+07:00")
    cfg.setdefault("doctor_comment", "Completed deterministic E2E review fixture.")
    cfg.setdefault("findings", [
        {"id": f"F{index}", "ai_state": item["name"], "decision": "accept"}
        for index, item in enumerate(ai_findings, start=1)
        if item["decision"] == "POSITIVE" and item["name"] != "No finding"
    ])
    cfg.setdefault("hypotheses", [
        {"id": f"H{index}", "hermes_state": item["state"], "decision": "accept"}
        for index, item in enumerate(case.get("disease_analysis", []), start=1)
    ])
    cfg.setdefault("conflicts", [
        {"id": conflict, "decision": "preserve"}
        for conflict in case.get("conflicts", [])
    ])
    return {
        "id": case["id"], "description": case["description"],
        "input": {"results": case["model_results"], "symptoms": "", "history": "", "laboratory": ""},
        "review": cfg,
    }


def run_e2e_case(case):
    """Run project code plus explicitly-labelled static fixtures and emit one trace."""
    model_findings = normalize_model_findings(case["model_results"])
    case_data = {"model_findings": model_findings}
    input_hash = snapshot_hash(case_data)
    ai_findings = deepcopy(model_findings["findings"])

    no_finding = derive_no_finding_policy(case_data)
    selected_skills = resolve_hermes_skills(case_data)
    positives = [item["name"] for item in ai_findings if item["decision"] == "POSITIVE" and item["name"] != "No finding"]

    evidence = {
        "evidence_objects": deepcopy(case.get("evidence_objects", [])),
        "conflicts": deepcopy(case.get("conflicts", [])),
        "missing_information": deepcopy(case.get("missing_information", [])),
        "missing_interpreted_as_negative": case.get("violations", {}).get("missing_negative", False),
    }
    finding_outputs = [
        {"finding": name, "skill": selected_skills[index + 1], "source_id": f"AI-{index + 1}"}
        for index, name in enumerate(positives)
    ]
    safety = deepcopy(case.get("safety", {"priority": "routine", "flags": [], "high_priority_supported": False}))
    disease = {"module_outputs": deepcopy(case.get("disease_analysis", []))}
    temporal_cfg = deepcopy(case.get("temporal", {"activated": False, "comparisons": []}))
    arbitration_cfg = deepcopy(case.get("arbitration", {"activated": False, "hypotheses": [], "evidence_ledger": [], "relations": [], "preserved_conflicts": []}))
    arbitration_cfg.setdefault("ranking", None)
    arbitration_cfg.setdefault("preserved_conflicts", deepcopy(case.get("conflicts", [])))
    ai_hash_before = snapshot_hash(ai_findings)
    disease_hash_before = snapshot_hash(disease)
    arbitration_hash_before = snapshot_hash(arbitration_cfg)

    draft = {
        "id": f"DRAFT-{case['id']}", "status": "DRAFT_REPORT",
        "text": "Deterministic provider-independent draft fixture.",
        "source_ids": [item.get("source_ids", []) for item in disease["module_outputs"]],
    }
    draft_hash = snapshot_hash(draft)

    review_input = _doctor_case(case, ai_findings)
    review_result = build_review_case(review_input)
    review = review_result["doctor_review"]
    review_before = snapshot_hash(review)

    binding = {
        "review_version": review["version"],
        "ai_snapshot_id": review["audit"]["ai_snapshot_id"],
        "hermes_snapshot_id": review["audit"]["hermes_snapshot_id"],
        "draft_report_snapshot_id": review["audit"]["draft_report_snapshot_id"],
    }
    final_cfg = {
        "request_source": case.get("final_request_source", "doctor_review"),
        "doctor_review": review,
        "candidate_binding": binding,
    }
    if case.get("final_request_source") == "raw_ai":
        final_cfg.pop("doctor_review")
    if case.get("stale_review_version"):
        final_cfg["candidate_binding"]["review_version"] = review["version"] - 1
    if case.get("snapshot_mismatch"):
        final_cfg["candidate_binding"]["ai_snapshot_id"] = "AI-UNREVIEWED-RERUN"
    if case.get("external_finalization"):
        final_cfg["external_finalization"] = deepcopy(case["external_finalization"])
    if case.get("new_evidence_after_finalization"):
        final_cfg["new_evidence_after_finalization"] = True
        final_cfg["report_history"] = [{"report_id": "REPORT-OLD", "version": 1, "text": "immutable old report"}]
    if case.get("recommendation"):
        review.setdefault("report_review", {})["recommendation"] = deepcopy(case["recommendation"])

    final_error = None
    try:
        final_result = render_final_report(final_cfg)
    except FinalReportValidationError as exc:
        final_error = str(exc)
        final_result = {"states": ["FINAL_REPORT_NOT_GENERATABLE"], "blocking_reasons": [final_error], "final_report_candidate": None}
    review_after = snapshot_hash(review)
    states = final_result["states"]
    preferred = [state for state in ("FINAL_REPORT_AMENDMENT_REQUIRED", "FINAL_REPORT_VERSION_MISMATCH", "FINAL_REPORT_SOURCE_MISMATCH", "FINAL_REPORT_BLOCKED_BY_REVIEW", "FINAL_REPORT_NOT_GENERATABLE", "FINAL_REPORT_CANDIDATE_READY", "FINAL_REPORT_FINALIZED_BY_DOCTOR") if state in states]
    final_status = preferred[0] if preferred else states[0]
    candidate = final_result.get("final_report_candidate")

    trace = {
        "case_id": case["id"], "case_version": 1,
        "input": {"case_data_snapshot": case_data, "snapshot_hash": input_hash},
        "routing": {
            "canonical_positive_findings": positives,
            "no_finding_state": no_finding["policy_state"],
            "selected_skills": selected_skills,
            "selector_order": selected_skills,
        },
        "evidence_fusion": evidence,
        "finding_reasoning": {"outputs": finding_outputs},
        "safety": safety,
        "disease_analysis": disease,
        "temporal": temporal_cfg,
        "arbitration": arbitration_cfg,
        "draft_report": {"snapshot": draft, "snapshot_hash": draft_hash},
        "doctor_review": {
            "fixture_id": f"FIXTURE-REVIEW-{case['id']}",
            "owning_module": "Structured Doctor Review v1",
            "fixed_timestamp": "2026-09-29T10:00:00+07:00",
            "review_id": review["review_id"], "review_version": review["version"],
            "decisions": [item["decision"] for item in review["finding_reviews"] + review["hypothesis_reviews"]],
            "readiness": review["finalization"]["readiness"],
            "preserved_conflicts": [item["conflict_id"] for item in review["conflict_reviews"] if item["decision"] == "preserve"],
            "snapshot_hash_before": review_before, "snapshot_hash_after": review_after,
        },
        "final_report": {
            "candidate_status": final_status,
            "candidate_snapshot": candidate,
            "candidate_hash": snapshot_hash(candidate) if candidate else None,
            "finalized": bool(candidate and candidate["finalization"]["finalized"]),
            "external_finalizer_source": (case.get("external_finalization") or {}).get("source"),
            "error": final_error,
        },
        "source_immutability": {
            "case_data": input_hash == snapshot_hash(case_data),
            "ai_result": ai_hash_before == snapshot_hash(ai_findings),
            "disease_analysis": disease_hash_before == snapshot_hash(disease),
            "arbitration": arbitration_hash_before == snapshot_hash(arbitration_cfg),
        },
        "violations": deepcopy(case.get("violations", {})),
        "failure_class": None,
    }

    evidence_ids = [item.get("id") for item in evidence["evidence_objects"] if item.get("id")]
    disease_source_ids = sorted({source_id for item in disease["module_outputs"] for source_id in item.get("source_ids", [])})
    temporal_source_ids = sorted({source_id for item in temporal_cfg.get("comparisons", []) for source_id in item.get("source_ids", [])})
    arbitration_source_ids = [item.get("canonical_evidence_id") for item in arbitration_cfg.get("evidence_ledger", []) if item.get("canonical_evidence_id")]
    review_source_ids = [review["audit"][key] for key in ("ai_snapshot_id", "hermes_snapshot_id", "draft_report_snapshot_id") if review["audit"].get(key)]
    final_source_ids = [value for value in (candidate or {}).get("provenance", {}).values() if isinstance(value, str) and value]
    stage_payloads = [
        (trace["input"], "project_code", None, True, [f"CASE_DATA-{case['id']}"]),
        (trace["routing"], "project_code", None, True, [f"CASE_DATA-{case['id']}"]),
        (trace["evidence_fusion"], "fixture", f"FIXTURE-EVIDENCE-{case['id']}", True, evidence_ids or [f"CASE_DATA-{case['id']}"]),
        (trace["finding_reasoning"], "fixture", f"FIXTURE-FINDINGS-{case['id']}", True, [item["source_id"] for item in finding_outputs] or [f"AI-{case['id']}"]),
        (trace["safety"], "fixture", f"FIXTURE-SAFETY-{case['id']}", True, evidence_ids or [f"CASE_DATA-{case['id']}"]),
        (trace["disease_analysis"], "fixture", f"FIXTURE-DISEASE-{case['id']}", True, disease_source_ids or evidence_ids or [f"CASE_DATA-{case['id']}"]),
        (trace["temporal"] if temporal_cfg.get("activated") else {"activated": False}, "fixture", f"FIXTURE-TEMPORAL-{case['id']}", temporal_cfg.get("activated", False), temporal_source_ids or (evidence_ids if temporal_cfg.get("activated") else [])),
        (trace["arbitration"] if arbitration_cfg.get("activated") else {"activated": False}, "fixture", f"FIXTURE-ARBITRATION-{case['id']}", arbitration_cfg.get("activated", False), arbitration_source_ids or (evidence_ids if arbitration_cfg.get("activated") else [])),
        (trace["draft_report"], "fixture", f"FIXTURE-DRAFT-{case['id']}", True, disease_source_ids or evidence_ids),
        (trace["doctor_review"], "project_code", None, True, review_source_ids),
        (trace["final_report"], "project_code", None, True, final_source_ids or review_source_ids),
    ]
    trace["stage_snapshots"] = [
        stage_snapshot(stage, ordinal, payload, mode, fixture_id=fixture_id, active=active, source_ids=source_ids)
        for ordinal, (stage, (payload, mode, fixture_id, active, source_ids)) in enumerate(zip(STAGE_ORDER, stage_payloads), start=1)
    ]
    trace["invariant_results"] = evaluate_invariants(trace)
    result = e2e_result(trace)
    trace["failure_class"] = result["failure_class"]
    return trace, result
