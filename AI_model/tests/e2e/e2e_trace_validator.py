"""Structural validator and result formatter for normalized E2E traces."""

from .e2e_helpers import STAGE_ORDER, snapshot_hash


class E2ETraceValidationError(ValueError):
    pass


def validate_trace(trace):
    snapshots = trace.get("stage_snapshots", [])
    if len(snapshots) != len(STAGE_ORDER):
        raise E2ETraceValidationError("E2E_TRACE_INCOMPLETE: unexplained missing stage")
    stages = [item.get("stage") for item in snapshots]
    ordinals = [item.get("ordinal") for item in snapshots]
    if stages != STAGE_ORDER or ordinals != list(range(1, len(STAGE_ORDER) + 1)):
        raise E2ETraceValidationError("E2E_TRACE_INCOMPLETE: stage order/ordinal invalid")
    if len(ordinals) != len(set(ordinals)):
        raise E2ETraceValidationError("E2E_TRACE_INCOMPLETE: duplicate stage ordinal")
    for item in snapshots:
        if item.get("execution_mode") not in {"project_code", "fixture"}:
            raise E2ETraceValidationError(f"E2E_TRACE_INCOMPLETE: execution mode missing at {item.get('stage')}")
        if item["execution_mode"] == "fixture" and not item.get("fixture_id"):
            raise E2ETraceValidationError(f"E2E_TRACE_INCOMPLETE: fixture ID missing at {item.get('stage')}")
        if item["execution_mode"] == "fixture" and (
            not item.get("owning_module") or not item.get("fixed_timestamp")
        ):
            raise E2ETraceValidationError(f"E2E_TRACE_INCOMPLETE: fixture ownership/time missing at {item.get('stage')}")
        if item.get("sha256") != snapshot_hash(item.get("normalized_payload")):
            raise E2ETraceValidationError(f"E2E_SNAPSHOT_MISMATCH: {item.get('stage')}")
        if item.get("active") and not item.get("source_ids"):
            raise E2ETraceValidationError(f"E2E_TRACE_INCOMPLETE: source IDs missing at {item.get('stage')}")
        if not item.get("active") and item.get("normalized_payload") not in ({}, {"activated": False}):
            raise E2ETraceValidationError(f"E2E_TRACE_INCOMPLETE: inactive stage has unexplained output at {item.get('stage')}")
    expected_invariants = {
        "PROVENANCE_PRESERVED", "MISSING_STAYS_UNKNOWN",
        "NO_SCORE_TO_DISEASE_PROBABILITY", "NO_UNSUPPORTED_ETIOLOGY",
        "NO_UNSUPPORTED_DIAGNOSIS", "OVERLAP_NOT_DOUBLE_COUNTED",
        "CONFLICT_PRESERVED", "SAFETY_ESCALATION_WHEN_SUPPORTED",
        "NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE", "DOCTOR_REVIEW_REQUIRED",
        "TEMPORAL_STATE_VALID", "ARBITRATION_NO_RANKING",
        "DOCTOR_REVIEW_SNAPSHOT_IMMUTABLE", "FINAL_REPORT_FROM_REVIEW_ONLY",
        "FINAL_REPORT_VERSION_BOUND", "NO_AUTO_FINALIZATION",
    }
    actual = [item.get("invariant") for item in trace.get("invariant_results", [])]
    if set(actual) != expected_invariants or len(actual) != len(expected_invariants):
        raise E2ETraceValidationError("E2E_TRACE_INCOMPLETE: invariant result set incomplete")
    return "E2E_TRACE_COMPLETE"


def e2e_result(trace):
    validate_trace(trace)
    failed = [item for item in trace["invariant_results"] if item["status"] == "fail"]
    passed = [item["invariant"] for item in trace["invariant_results"] if item["status"] == "pass"]
    first = failed[0] if failed else None
    return {
        "case_id": trace["case_id"],
        "status": "fail" if failed else "pass",
        "failure_class": "CLINICAL_SEMANTIC_FAILURE" if failed else None,
        "stages_executed": [item["stage"] for item in trace["stage_snapshots"] if item["active"]],
        "stages_fixture_injected": [item["stage"] for item in trace["stage_snapshots"] if item["execution_mode"] == "fixture"],
        "invariants": {"passed": passed, "failed": [item["invariant"] for item in failed]},
        "first_failure": {
            "stage": first["stage"] if first else None,
            "invariant": first["invariant"] if first else None,
            "message": first["message"] if first else None,
        },
        "trace_complete": True,
    }
