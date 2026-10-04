"""Structured reader event and human-factors issue schemas without thought-process capture."""

from __future__ import annotations

from datetime import datetime

from .study_schema import CONDITIONS


FORBIDDEN_COGNITION_FIELDS = {
    "chain_of_thought", "reasoning_trace", "hidden_reasoning", "internal_monologue",
}


class ReaderEventError(ValueError):
    pass


def _timestamp(value, field):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ReaderEventError(f"invalid {field}") from exc


def validate_reader_event(event):
    if not isinstance(event, dict):
        raise ReaderEventError("reader event must be an object")
    forbidden = FORBIDDEN_COGNITION_FIELDS & set(event)
    if forbidden:
        raise ReaderEventError("reader chain-of-thought fields are forbidden")
    required = {
        "study_id", "session_id", "reader_id", "case_id", "condition", "case_order",
        "started_at", "completed_at", "finding_decisions", "hypothesis_decisions",
        "report_text", "high_priority_acknowledgements", "confidence",
        "doctor_review_actions", "hermes_snapshot_id", "ui_version", "ui_interactions",
        "technical_status", "completed",
    }
    missing = sorted(required - set(event))
    if missing:
        raise ReaderEventError(f"reader event missing fields: {', '.join(missing)}")
    if event["condition"] not in CONDITIONS:
        raise ReaderEventError("invalid study condition")
    if not isinstance(event["case_order"], int) or event["case_order"] < 1:
        raise ReaderEventError("case_order must be a positive integer")
    started = _timestamp(event["started_at"], "started_at")
    completed = _timestamp(event["completed_at"], "completed_at")
    if completed < started:
        raise ReaderEventError("completed_at precedes started_at")
    for field in ("finding_decisions", "hypothesis_decisions", "high_priority_acknowledgements", "doctor_review_actions"):
        if not isinstance(event[field], list):
            raise ReaderEventError(f"{field} must be a list")
    if not isinstance(event["ui_interactions"], dict):
        raise ReaderEventError("ui_interactions must be an object")
    required_ui = {
        "warning_seen", "warning_acknowledged", "conflict_viewed",
        "provenance_panel_viewed", "accept_count", "modify_count", "reject_count",
    }
    if not required_ui <= set(event["ui_interactions"]):
        raise ReaderEventError("UI interaction fields are incomplete")
    if event["technical_status"] not in {"OK", "TECHNICAL_FAILURE"}:
        raise ReaderEventError("technical_status is invalid")
    if event["technical_status"] == "TECHNICAL_FAILURE" and event["completed"] is True:
        raise ReaderEventError("technical failure cannot be silently marked complete")
    if event["condition"] == "UNAIDED" and event["hermes_snapshot_id"] is not None:
        raise ReaderEventError("unaided event cannot bind Hermes assistance")
    if event["condition"] == "HERMES_ASSISTED" and not event["hermes_snapshot_id"]:
        raise ReaderEventError("assisted event requires Hermes snapshot ID")
    return event


def event_duration_seconds(event):
    validate_reader_event(event)
    return (_timestamp(event["completed_at"], "completed_at") - _timestamp(event["started_at"], "started_at")).total_seconds()


def validate_human_factors_issue(issue):
    required = {
        "issue_id", "reader_id", "case_id", "condition", "category", "severity",
        "description", "ui_component", "reproducible",
    }
    if not isinstance(issue, dict) or not required <= set(issue):
        raise ReaderEventError("human-factors issue is incomplete")
    if issue["condition"] not in CONDITIONS or not isinstance(issue["reproducible"], bool):
        raise ReaderEventError("human-factors issue has invalid fields")
    if FORBIDDEN_COGNITION_FIELDS & set(issue):
        raise ReaderEventError("reader chain-of-thought fields are forbidden")
    return issue
