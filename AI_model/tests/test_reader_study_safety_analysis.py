"""Human-AI safety endpoint tests."""

from reader_study.safety_analysis import safety_endpoints
from reader_study_fixtures import reader_event


def test_incorrect_acceptance_correct_rejection_and_over_upgrade_are_separate():
    event = reader_event()
    event["ai_suggestions"] = [
        {"suggestion_id": "A", "ai_correct": False, "action": "ACCEPTED"},
        {"suggestion_id": "B", "ai_correct": True, "action": "REJECTED"},
    ]
    event["uncertainty_over_upgrade"] = True
    result = safety_endpoints([event])
    assert result["incorrect_assistance_acceptance"]["estimate"] == 1
    assert result["correct_assistance_rejection"]["estimate"] == 1
    assert result["uncertainty_over_upgrade"]["estimate"] == 1


def test_high_priority_miss_review_boundary_and_provenance_confusion_are_reported():
    missed = reader_event()
    missed.update({
        "high_priority_miss": True,
        "doctor_review_boundary_violation": True,
        "provenance_confusion": True,
        "unsupported_action_retained": True,
        "conflict_suppression": True,
    })
    not_applicable = reader_event()
    not_applicable["high_priority_present"] = False
    result = safety_endpoints([missed, not_applicable])
    assert result["high_priority_acknowledgement_failure"] == {
        "numerator": 1, "denominator": 1, "estimate": 1.0,
    }
    assert result["doctor_review_boundary_violation"]["numerator"] == 1
    assert result["provenance_confusion"]["numerator"] == 1
    assert result["unsupported_action_retained"]["numerator"] == 1
    assert result["conflict_suppression"]["numerator"] == 1


def test_safety_measures_do_not_assign_psychological_labels():
    result = safety_endpoints([reader_event()])
    assert all("diagnosis" not in key and "psychological" not in key for key in result)
