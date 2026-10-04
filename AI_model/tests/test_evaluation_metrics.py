"""Deterministic dimension-level metric tests."""

import pytest

from evaluation.metrics import (
    arbitration_metrics,
    binary_finding_metrics,
    bounded_state_metrics,
    report_fidelity_metrics,
    safety_semantic_metrics,
    temporal_metrics,
    validate_metric_spec,
)
from evaluation.subgroup_analysis import analyze_subgroups


def test_perfect_binary_case_has_complete_counts_and_rates():
    result = binary_finding_metrics(
        ["POSITIVE", "EXPLICIT_NEGATIVE"],
        ["POSITIVE", "EXPLICIT_NEGATIVE"],
    )
    assert result["counts"] == {"tp": 1, "fp": 0, "tn": 1, "fn": 0}
    assert all(result[name]["estimate"] == 1 for name in ("sensitivity", "specificity", "ppv", "npv", "f1"))


def test_all_wrong_binary_case_and_undefined_denominator_are_explicit():
    wrong = binary_finding_metrics(
        ["POSITIVE", "EXPLICIT_NEGATIVE"],
        ["EXPLICIT_NEGATIVE", "POSITIVE"],
    )
    assert wrong["counts"] == {"tp": 0, "fp": 1, "tn": 0, "fn": 1}
    assert wrong["f1"]["estimate"] == 0
    no_positives = binary_finding_metrics(
        ["EXPLICIT_NEGATIVE"], ["EXPLICIT_NEGATIVE"]
    )
    assert no_positives["sensitivity"] == {"numerator": 0, "denominator": 0, "estimate": None}


def test_bounded_states_report_indeterminate_and_unsafe_upgrade_without_binary_mapping():
    result = bounded_state_metrics(
        ["INDETERMINATE", "INDETERMINATE"],
        ["INDETERMINATE", "CONFIRMED"],
        unsafe_upgrade_pairs=[("INDETERMINATE", "CONFIRMED")],
        confirmation_states=["CONFIRMED"],
        indeterminate_states=["INDETERMINATE"],
    )
    assert result["exact_state_agreement"]["estimate"] == 0.5
    assert result["unsafe_false_upgrade"]["numerator"] == 1
    assert result["unsupported_confirmation"]["numerator"] == 1
    assert result["appropriate_indeterminate"]["numerator"] == 1
    assert result["confusion_matrix"]["INDETERMINATE"] == {"CONFIRMED": 1, "INDETERMINATE": 1}


def test_safety_temporal_arbitration_and_report_failures_remain_separate_dimensions():
    safety = safety_semantic_metrics([{"autonomous_action": True}])
    assert safety["autonomous_action_rate"]["estimate"] == 1
    assert safety["unsupported_diagnosis_rate"]["estimate"] == 0
    temporal = temporal_metrics(["INDETERMINATE", "STABLE"], ["NEW", "WORSENED"])
    assert temporal["false_new"]["numerator"] == 1
    assert temporal["false_progression_or_worsening"]["numerator"] == 1
    arbitration = arbitration_metrics([{"ranking": True, "duplicate_evidence": True}])
    assert arbitration["ranking_rate"]["estimate"] == 1
    fidelity = report_fidelity_metrics([{"rejected_content_resurrection": True}])
    assert fidelity["rejected_content_resurrection_rate"]["estimate"] == 1
    assert fidelity["auto_finalization_rate"]["estimate"] == 0


def test_probability_calibration_is_rejected_for_bounded_disease_states():
    with pytest.raises(ValueError, match="do not apply"):
        validate_metric_spec("disease_state", ["exact_state_agreement", "ECE", "Brier"])
    assert validate_metric_spec("finding", ["sensitivity", "specificity"]) is True


def test_binary_metrics_reject_unknown_instead_of_silently_coercing_it():
    with pytest.raises(ValueError, match="non-binary labels"):
        binary_finding_metrics(["UNKNOWN"], ["EXPLICIT_NEGATIVE"])


def test_subgroup_analysis_only_uses_declared_metadata_and_warns_for_small_groups():
    records = [
        {"metadata": {"site": "A"}, "correct": True},
        {"metadata": {"site": "A"}, "correct": False},
        {"metadata": {}, "correct": True},
    ]
    result = analyze_subgroups(
        records,
        "site",
        lambda rows: {"agreement": sum(row["correct"] for row in rows) / len(rows)},
        minimum_size=3,
    )
    assert set(result) == {"A"}
    assert result["A"]["count"] == 2
    assert result["A"]["limitations"]
