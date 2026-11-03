"""Adapter to the frozen E2E invariant engine; no clinical policy is redefined here."""

from __future__ import annotations

from e2e.e2e_invariants import INVARIANT_CHECKS, evaluate_invariants


def evaluate_silent_trace(trace):
    results = evaluate_invariants(trace)
    if len(results) != len(INVARIANT_CHECKS) or len(results) != 16:
        raise ValueError("frozen invariant result set is incomplete")
    failed = [item for item in results if item["status"] == "fail"]
    return {
        "invariant_results": results,
        "passed": [item["invariant"] for item in results if item["status"] == "pass"],
        "failed": [item["invariant"] for item in failed],
        "semantic_safety_incident_required": bool(failed),
    }
