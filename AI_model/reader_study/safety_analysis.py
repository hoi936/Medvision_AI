"""Human-AI safety measures; these are study outcomes, not psychological diagnoses."""

from __future__ import annotations

from .endpoints import rate


def _flag_rate(events, flag, *, denominator_filter=None):
    eligible = [event for event in events if denominator_filter is None or denominator_filter(event)]
    return rate(sum(bool(event.get(flag, False)) for event in eligible), len(eligible))


def incorrect_assistance_acceptance(events):
    suggestions = [
        suggestion for event in events for suggestion in event.get("ai_suggestions", [])
        if suggestion.get("ai_correct") is False
    ]
    return rate(sum(item.get("action") == "ACCEPTED" for item in suggestions), len(suggestions))


def correct_assistance_rejection(events):
    suggestions = [
        suggestion for event in events for suggestion in event.get("ai_suggestions", [])
        if suggestion.get("ai_correct") is True
    ]
    return rate(sum(item.get("action") == "REJECTED" for item in suggestions), len(suggestions))


def uncertainty_over_upgrade(events):
    return _flag_rate(events, "uncertainty_over_upgrade")


def high_priority_acknowledgement_failure(events):
    return _flag_rate(events, "high_priority_miss", denominator_filter=lambda event: event.get("high_priority_present") is True)


def doctor_review_boundary_violation(events):
    return _flag_rate(events, "doctor_review_boundary_violation")


def provenance_confusion(events):
    return _flag_rate(events, "provenance_confusion")


def unsupported_action_retained(events):
    return _flag_rate(events, "unsupported_action_retained")


def conflict_suppression(events):
    return _flag_rate(events, "conflict_suppression")


def safety_endpoints(events):
    return {
        "incorrect_assistance_acceptance": incorrect_assistance_acceptance(events),
        "correct_assistance_rejection": correct_assistance_rejection(events),
        "uncertainty_over_upgrade": uncertainty_over_upgrade(events),
        "high_priority_acknowledgement_failure": high_priority_acknowledgement_failure(events),
        "doctor_review_boundary_violation": doctor_review_boundary_violation(events),
        "provenance_confusion": provenance_confusion(events),
        "unsupported_action_retained": unsupported_action_retained(events),
        "conflict_suppression": conflict_suppression(events),
    }
