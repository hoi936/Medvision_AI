"""Confidence interval and patient-resampling tests."""

import pytest

from evaluation.confidence_intervals import patient_level_bootstrap, wilson_interval


def test_wilson_interval_is_bounded_and_handles_undefined_denominator():
    result = wilson_interval(5, 10)
    assert result["method"] == "wilson"
    assert result["lower"] == pytest.approx(0.236593, abs=1e-6)
    assert result["upper"] == pytest.approx(0.763407, abs=1e-6)
    assert wilson_interval(0, 0)["lower"] is None
    with pytest.raises(ValueError):
        wilson_interval(2, 1)


def test_bootstrap_is_patient_level_and_deterministic_with_test_seed():
    records = [
        {"patient_group_id": "P1", "correct": 1, "study": "S1"},
        {"patient_group_id": "P1", "correct": 1, "study": "S2"},
        {"patient_group_id": "P2", "correct": 0, "study": "S3"},
    ]
    metric_fn = lambda rows: sum(row["correct"] for row in rows) / len(rows)
    first = patient_level_bootstrap(records, metric_fn, iterations=200, seed=7)
    second = patient_level_bootstrap(records, metric_fn, iterations=200, seed=7)
    assert first == second
    assert first["unit"] == "patient"
    assert first["patient_count"] == 2
    assert first["lower"] == 0
    assert first["upper"] == 1


def test_bootstrap_requires_patient_group_ids():
    with pytest.raises(ValueError, match="patient_group_id"):
        patient_level_bootstrap([{"correct": 1}], lambda rows: 1, iterations=2, seed=1)
