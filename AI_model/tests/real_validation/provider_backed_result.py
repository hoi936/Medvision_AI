"""Result schema and failure taxonomy for provider-backed E2E trials."""

from __future__ import annotations

from copy import deepcopy


FAILURE_CLASSES = {
    "INFRASTRUCTURE_CONFIGURATION",
    "INFRASTRUCTURE_TRANSIENT",
    "CLINICAL_SEMANTIC_FAILURE",
    "PASS",
}
MODES = {"REAL_GATE", "REAL_ROBUSTNESS"}


def build_result(
    *,
    case_id,
    trial_id,
    mode,
    runtime,
    provider,
    started_at,
    duration_ms,
    invariant_results=(),
    failure_class="PASS",
    failure_message=None,
    candidate_state=None,
    finalized=False,
    raw_output_ref=None,
    normalized_trace_ref=None,
    attempts=(),
):
    """Build the stable, secret-free result document for one trial."""
    if mode not in MODES:
        raise ValueError(f"unsupported provider-backed mode: {mode}")
    if failure_class not in FAILURE_CLASSES:
        raise ValueError(f"unsupported failure class: {failure_class}")
    invariant_results = [deepcopy(item) for item in invariant_results]
    failed = [item for item in invariant_results if item.get("status") == "fail"]
    passed = [item["invariant"] for item in invariant_results if item.get("status") == "pass"]
    first = failed[0] if failed else None
    return {
        "provider_backed_result": {
            "case_id": case_id,
            "trial_id": trial_id,
            "mode": mode,
            "runtime": {
                "hermes_version": runtime.get("hermes_version"),
                "hermes_commit": runtime.get("hermes_commit"),
                "python_version": runtime.get("python_version") or runtime.get("python"),
            },
            "provider": {
                "name": provider.get("name") or provider.get("provider"),
                "model": provider.get("model"),
                "model_version": provider.get("model_version"),
                "request_id": provider.get("request_id"),
            },
            "execution": {
                "started_at": started_at,
                "duration_ms": duration_ms,
                "attempts": [deepcopy(item) for item in attempts],
            },
            "invariants": {
                "passed": passed,
                "failed": [item["invariant"] for item in failed],
            },
            "failure": {
                "class": failure_class,
                "first_invariant": first.get("invariant") if first else None,
                "stage": first.get("stage") if first else None,
                "message": failure_message or (first.get("message") if first else None),
            },
            "report": {
                "candidate_state": candidate_state,
                "finalized": bool(finalized),
            },
            "raw_output_ref": raw_output_ref,
            "normalized_trace_ref": normalized_trace_ref,
        }
    }


def validate_result_schema(document):
    """Fail closed when a result omits a required v1 field."""
    root = document.get("provider_backed_result", {})
    required = {
        "case_id", "trial_id", "mode", "runtime", "provider", "execution",
        "invariants", "failure", "report", "raw_output_ref", "normalized_trace_ref",
    }
    if set(root) != required:
        raise ValueError("provider-backed result schema mismatch")
    if root["mode"] not in MODES or root["failure"].get("class") not in FAILURE_CLASSES:
        raise ValueError("provider-backed result enum mismatch")
    if set(root["runtime"]) != {"hermes_version", "hermes_commit", "python_version"}:
        raise ValueError("provider-backed runtime schema mismatch")
    if set(root["provider"]) != {"name", "model", "model_version", "request_id"}:
        raise ValueError("provider-backed provider schema mismatch")
    return document
