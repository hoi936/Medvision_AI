"""Monitoring-plan schema for governed live stages."""

from __future__ import annotations


def validate_monitoring_plan(plan):
    required = {"metrics", "metric_owners", "cadence", "escalation", "pause_criteria", "version_stratification", "auto_adaptation"}
    if not isinstance(plan, dict) or not required <= set(plan):
        raise ValueError("monitoring plan is incomplete")
    for field in ("metrics", "metric_owners", "pause_criteria"):
        if not isinstance(plan[field], list) or not plan[field]:
            raise ValueError(f"monitoring {field} must be pre-specified")
    for field in ("cadence", "escalation", "version_stratification"):
        if not isinstance(plan[field], str) or not plan[field].strip():
            raise ValueError(f"monitoring {field} must be pre-specified")
    if plan["auto_adaptation"] is not False:
        raise ValueError("monitoring cannot auto-adapt the model")
    return plan
