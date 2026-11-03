"""Descriptive endpoint and Human-AI interaction tests."""

from reader_study.endpoints import descriptive_endpoints
from reader_study.human_ai_analysis import human_ai_endpoints
from reader_study_fixtures import reader_event


def test_descriptive_endpoints_keep_accuracy_errors_completion_and_raw_time_separate():
    correct = reader_event()
    error = reader_event(completed=False)
    error.update({"reference_agreement": False, "major_error": True, "unsafe_false_upgrade": True, "critical_miss": True})
    result = descriptive_endpoints([correct, error])
    assert result["reference_agreement"]["estimate"] == 0.5
    assert result["major_error"]["numerator"] == 1
    assert result["unsafe_false_upgrade"]["numerator"] == 1
    assert result["critical_miss"]["numerator"] == 1
    assert result["completion"]["estimate"] == 0.5
    assert result["reading_time_seconds"] == {"count": 1, "values": [120.0], "mean": 120.0}
    assert "composite" not in result


def test_human_ai_actions_and_correctness_are_not_interpreted_as_one_benefit_score():
    event = reader_event()
    event["ai_suggestions"] = [
        {"suggestion_id": "A", "ai_correct": False, "action": "ACCEPTED"},
        {"suggestion_id": "B", "ai_correct": True, "action": "REJECTED"},
        {"suggestion_id": "C", "ai_correct": True, "action": "MODIFIED"},
    ]
    result = human_ai_endpoints([event])
    assert result["incorrect_ai_accepted"]["estimate"] == 1
    assert result["correct_ai_rejected"]["estimate"] == 0.5
    assert result["ai_suggestion_modified"]["numerator"] == 1
    assert "benefit" not in result


def test_undefined_human_ai_denominators_remain_null():
    result = human_ai_endpoints([reader_event(condition="UNAIDED")])
    assert result["incorrect_ai_accepted"]["estimate"] is None
    assert result["assistance_use"]["denominator"] == 0
