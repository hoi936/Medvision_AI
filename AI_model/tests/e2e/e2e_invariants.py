"""Independent global invariant checks for E2E Clinical Validation v1."""

import json
import re

from .e2e_helpers import snapshot_hash


def _result(name, passed, stage, message, refs=()):
    return {
        "invariant": name,
        "status": "pass" if passed else "fail",
        "stage": stage,
        "evidence_refs": list(refs),
        "message": message,
    }


def check_provenance_preserved(trace):
    outputs = trace["disease_analysis"]["module_outputs"]
    immutable = all(trace.get("source_immutability", {}).values())
    ok = all(item.get("source_ids") for item in outputs) and immutable
    return _result("PROVENANCE_PRESERVED", ok, "E2E_STAGE_DISEASE_ANALYSIS", "all module outputs retain source IDs and upstream snapshots remain immutable" if ok else "module provenance missing or E2E_UNEXPECTED_STAGE_MUTATION")


def check_missing_stays_unknown(trace):
    evidence = trace["evidence_fusion"]
    ok = not evidence.get("missing_interpreted_as_negative", False) and not trace.get("violations", {}).get("missing_negative", False)
    return _result("MISSING_STAYS_UNKNOWN", ok, "E2E_STAGE_EVIDENCE_FUSION", "missing inputs remain unknown" if ok else "missing input was converted to negative")


def check_no_score_to_probability(trace):
    text = json.dumps({"disease": trace["disease_analysis"], "final": trace["final_report"]}, ensure_ascii=False).lower()
    bad = trace.get("violations", {}).get("score_probability", False) or bool(re.search(r"\b\d+(?:\.\d+)?%\s*(?:probability|chance|xác suất)", text))
    return _result("NO_SCORE_TO_DISEASE_PROBABILITY", not bad, "E2E_STAGE_FINAL_REPORT", "model score not converted to disease probability" if not bad else "model score was represented as disease probability")


def check_no_unsupported_etiology(trace):
    bad = any(item.get("etiology_supported") is False and item.get("etiology_asserted") for item in trace["disease_analysis"]["module_outputs"])
    return _result("NO_UNSUPPORTED_ETIOLOGY", not bad, "E2E_STAGE_DISEASE_ANALYSIS", "etiology remains evidence-bounded" if not bad else "unsupported etiology asserted")


def check_no_unsupported_diagnosis(trace):
    bad = any(item.get("diagnosis_supported") is False and item.get("diagnosis_asserted") for item in trace["disease_analysis"]["module_outputs"])
    return _result("NO_UNSUPPORTED_DIAGNOSIS", not bad, "E2E_STAGE_DISEASE_ANALYSIS", "diagnostic states remain owned by frozen modules" if not bad else "unsupported diagnosis asserted")


def check_overlap_not_double_counted(trace):
    ledger = trace["arbitration"]["evidence_ledger"]
    ids = [item.get("canonical_evidence_id") for item in ledger if item.get("canonical_evidence_id")]
    bad = trace.get("violations", {}).get("duplicate_support", False) or len(ids) != len(set(ids))
    return _result("OVERLAP_NOT_DOUBLE_COUNTED", not bad, "E2E_STAGE_ARBITRATION", "canonical evidence counted once" if not bad else "same evidence duplicated as independent support", ids)


def check_conflict_preserved(trace):
    expected = set(trace["evidence_fusion"].get("conflicts", []))
    preserved = set(trace["arbitration"].get("preserved_conflicts", [])) | set(trace["doctor_review"].get("preserved_conflicts", []))
    bad = trace.get("violations", {}).get("conflict_removed", False)
    ok = not bad and expected <= preserved
    return _result("CONFLICT_PRESERVED", ok, "E2E_STAGE_DOCTOR_REVIEW", "trusted conflicts remain explicit" if ok else "conflict disappeared without an explicit review resolution", expected)


def check_safety_escalation_when_supported(trace):
    required = trace["safety"].get("high_priority_supported", False)
    ok = not required or trace["safety"]["priority"] == "high"
    return _result("SAFETY_ESCALATION_WHEN_SUPPORTED", ok, "E2E_STAGE_SAFETY", "safety priority is preserved independently of certainty" if ok else "supported high-priority condition was not escalated")


def check_no_autonomous_treatment_or_procedure(trace):
    final = trace["final_report"].get("candidate_snapshot") or {}
    rec = final.get("recommendations", {}) if isinstance(final, dict) else {}
    allowed = rec.get("text") is None or rec.get("source") in {"doctor_authored", "external_clinician_approved"}
    bad = trace.get("violations", {}).get("autonomous_action", False)
    return _result("NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE", allowed and not bad, "E2E_STAGE_FINAL_REPORT", "no autonomous action was introduced" if allowed and not bad else "autonomous recommendation/action detected")


def check_doctor_review_required(trace):
    final_status = trace["final_report"].get("candidate_status")
    ready = trace["doctor_review"].get("readiness") == "ready"
    candidate = final_status in {"FINAL_REPORT_CANDIDATE_READY", "FINAL_REPORT_RENDERED_FROM_REVIEW", "FINAL_REPORT_FINALIZED_BY_DOCTOR"}
    bad = trace.get("violations", {}).get("raw_ai_to_final", False)
    ok = not bad and (not candidate or ready)
    return _result("DOCTOR_REVIEW_REQUIRED", ok, "E2E_STAGE_FINAL_REPORT", "candidate path is gated by completed review" if ok else "raw AI/draft bypassed doctor review")


def check_temporal_state_valid(trace):
    comparisons = trace["temporal"]["comparisons"]
    ok = all(item.get("valid", True) for item in comparisons) and not trace.get("violations", {}).get("invalid_temporal", False)
    return _result("TEMPORAL_STATE_VALID", ok, "E2E_STAGE_TEMPORAL_REASONING", "temporal states meet declared prerequisites" if ok else "temporal state lacks valid correspondence/comparability")


def check_arbitration_no_ranking(trace):
    arbitration = trace["arbitration"]
    bad = arbitration.get("ranking") is not None or trace.get("violations", {}).get("ranking", False)
    return _result("ARBITRATION_NO_RANKING", not bad, "E2E_STAGE_ARBITRATION", "arbitration preserves alternatives without ranking" if not bad else "disease ranking/winner detected")


def check_doctor_review_snapshot_immutable(trace):
    review = trace["doctor_review"]
    ok = review.get("snapshot_hash_before") == review.get("snapshot_hash_after") and not trace.get("violations", {}).get("review_mutated", False)
    return _result("DOCTOR_REVIEW_SNAPSHOT_IMMUTABLE", ok, "E2E_STAGE_FINAL_REPORT", "report rendering did not mutate doctor review" if ok else "E2E_UNEXPECTED_STAGE_MUTATION", [review.get("fixture_id")])


def check_final_report_from_review_only(trace):
    final = trace["final_report"]
    candidate = final.get("candidate_snapshot") or {}
    status = final.get("candidate_status")
    blocked = status in {"FINAL_REPORT_NOT_GENERATABLE", "FINAL_REPORT_BLOCKED_BY_REVIEW", "FINAL_REPORT_VERSION_MISMATCH", "FINAL_REPORT_SOURCE_MISMATCH"}
    ok = blocked or candidate.get("source_review_id") == trace["doctor_review"].get("review_id")
    if trace.get("violations", {}).get("rejected_restored", False):
        ok = False
    return _result("FINAL_REPORT_FROM_REVIEW_ONLY", ok, "E2E_STAGE_FINAL_REPORT", "final candidate derives only from reviewed state" if ok else "unreviewed/rejected upstream content entered final candidate")


def check_final_report_version_bound(trace):
    final = trace["final_report"]
    candidate = final.get("candidate_snapshot") or {}
    status = final.get("candidate_status")
    mismatch = status in {"FINAL_REPORT_VERSION_MISMATCH", "FINAL_REPORT_SOURCE_MISMATCH"}
    if trace.get("violations", {}).get("stale_version_accepted", False):
        ok = False
    elif mismatch:
        ok = candidate == {}
    elif candidate:
        ok = candidate.get("source_review_version") == trace["doctor_review"].get("review_version")
    else:
        ok = True
    return _result("FINAL_REPORT_VERSION_BOUND", ok, "E2E_STAGE_FINAL_REPORT", "candidate is bound to exact review/snapshots" if ok else "stale or mismatched candidate accepted")


def check_no_auto_finalization(trace):
    final = trace["final_report"]
    finalized = final.get("finalized", False)
    authenticated = final.get("external_finalizer_source") == "authenticated_doctor"
    bad = trace.get("violations", {}).get("auto_finalized", False)
    ok = not bad and (not finalized or authenticated)
    return _result("NO_AUTO_FINALIZATION", ok, "E2E_STAGE_FINAL_REPORT", "candidate is not auto-finalized" if ok else "candidate was finalized without authenticated doctor action")


INVARIANT_CHECKS = [
    check_provenance_preserved,
    check_missing_stays_unknown,
    check_no_score_to_probability,
    check_no_unsupported_etiology,
    check_no_unsupported_diagnosis,
    check_overlap_not_double_counted,
    check_conflict_preserved,
    check_safety_escalation_when_supported,
    check_no_autonomous_treatment_or_procedure,
    check_doctor_review_required,
    check_temporal_state_valid,
    check_arbitration_no_ranking,
    check_doctor_review_snapshot_immutable,
    check_final_report_from_review_only,
    check_final_report_version_bound,
    check_no_auto_finalization,
]


def evaluate_invariants(trace):
    return [check(trace) for check in INVARIANT_CHECKS]
