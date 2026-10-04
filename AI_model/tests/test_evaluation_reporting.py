"""Machine-readable and human-readable reporting tests."""

import json

import pytest

from evaluation.error_analysis import build_error_case
from evaluation.metrics import metric
from evaluation.reporting import build_report, render_json, render_markdown, render_metrics_csv


def test_scaffold_report_cannot_be_mistaken_for_an_actual_evaluation():
    run_result = {
        "state": "EVALUATION_DATASET_MISSING",
        "reason": "independent evaluation dataset not configured",
        "actual_dataset_run": False,
    }
    report = build_report(
        run_result=run_result,
        limitations=["No independent dataset was configured."],
    )
    root = report["clinical_dataset_evaluation"]
    assert root["execution"] == "scaffold_only"
    assert root["dataset"]["case_count"] == 0
    assert root["metrics"] == {}
    assert json.loads(render_json(report)) == report
    markdown = render_markdown(report)
    assert "EVALUATION_DATASET_MISSING" in markdown
    assert "independent evaluation dataset not configured" in markdown


def test_metric_csv_keeps_numerator_denominator_and_estimate():
    run_result = {"state": "EVALUATION_COMPLETE", "actual_dataset_run": True}
    report = build_report(
        run_result=run_result,
        metrics={"finding": {"sensitivity": metric(8, 10)}},
    )
    csv_text = render_metrics_csv(report)
    assert "finding.sensitivity,8,10,0.8" in csv_text
    assert "composite" not in csv_text.lower()


def test_error_review_record_is_deidentified_and_versioned():
    item = build_error_case(
        case_id="DS001",
        category="safety_error",
        expected={"autonomous_action": False},
        observed={"autonomous_action": True},
        evidence_refs=["REF-1"],
        system_version="snapshot-abc",
    )
    assert item["case_id"] == "DS001"
    assert item["system_version"] == "snapshot-abc"
    assert set(item) == {"case_id", "category", "expected", "observed", "evidence_refs", "system_version"}


def test_error_review_rejects_nested_direct_identifiers():
    with pytest.raises(ValueError, match="direct identifiers"):
        build_error_case(
            case_id="DS001", category="input_data_error",
            expected={"patient_name": "forbidden"}, observed={},
            evidence_refs=[], system_version="snapshot-abc",
        )
