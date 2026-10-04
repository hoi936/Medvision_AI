"""Incident response is an active plan, separate from incident logging."""

from __future__ import annotations


def validate_incident_response(plan):
    required = {"category_owners", "severity_rules", "acknowledgement", "containment", "root_cause_review", "corrective_action", "evidence_preservation"}
    if not isinstance(plan, dict) or not required <= set(plan):
        raise ValueError("incident response plan is incomplete")
    for field in required:
        value = plan[field]
        if not value:
            raise ValueError(f"incident response {field} is missing")
    return plan
