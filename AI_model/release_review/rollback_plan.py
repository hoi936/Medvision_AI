"""Rollback-plan schema for governed live stages."""

from __future__ import annotations


def validate_rollback_plan(plan):
    required = {"triggers", "owner", "last_known_good_version", "data_compatibility", "communication_path"}
    if not isinstance(plan, dict) or not required <= set(plan):
        raise ValueError("rollback plan is incomplete")
    if not isinstance(plan["triggers"], list) or not plan["triggers"]:
        raise ValueError("rollback triggers must be pre-specified")
    if any(not isinstance(plan[field], str) or not plan[field].strip() for field in required - {"triggers"}):
        raise ValueError("rollback ownership/version/communication must be explicit")
    return plan
