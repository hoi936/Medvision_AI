"""Reader-study reporting and MRMC export tests."""

import json

from reader_study.mrmc_export import MRMC_ANALYSIS_NOTE, export_csv, export_json
from reader_study.protocol import ReaderStudyHarness
from reader_study.reporting import build_report, render_csv, render_json, render_markdown
from reader_study_fixtures import reader_event


def test_not_run_report_separates_scaffold_blockers_and_has_no_benefit_claim():
    assessment = ReaderStudyHarness().assess(
        protocol=None, readers=None, training_cases=None,
        evaluation_cases=None, frozen_assistance=None,
    )
    report = build_report(
        assessment=assessment,
        limitations=["No actual readers or independent dataset were configured."],
    )
    root = report["human_ai_reader_study"]
    assert root["infrastructure"] == "implemented"
    assert root["actual_study_status"] == "NOT_RUN"
    assert root["clinical_benefit_claim"] is None
    assert len(root["readiness_blockers"]) == 5
    assert json.loads(render_json(report)) == report
    markdown = render_markdown(report)
    assert "Actual study: `NOT_RUN`" in markdown
    assert "Clinical benefit claim: none" in markdown


def test_report_csv_keeps_endpoint_dimensions_separate():
    assessment = {"state": "READER_STUDY_COMPLETE", "actual_study_run": True}
    report = build_report(
        assessment=assessment,
        endpoints={"reference_agreement": {"numerator": 8, "denominator": 10, "estimate": 0.8}},
        safety={"critical_miss": {"numerator": 1, "denominator": 10, "estimate": 0.1}},
        human_ai={"incorrect_ai_accepted": {"numerator": 1, "denominator": 2, "estimate": 0.5}},
    )
    csv_text = render_csv(report)
    assert "endpoints.reference_agreement,8,10,0.8" in csv_text
    assert "safety.critical_miss,1,10,0.1" in csv_text
    assert "human_ai.incorrect_ai_accepted,1,2,0.5" in csv_text
    assert "composite" not in csv_text.lower()


def test_mrmc_exports_tidy_rows_without_naive_inferential_statistics():
    event = reader_event()
    csv_text = export_csv([event])
    assert "reader_id,case_id,condition,reference,reader_result" in csv_text
    assert "R1,DS001,HERMES_ASSISTED,POSITIVE,POSITIVE" in csv_text
    document = json.loads(export_json([event]))
    assert document["analysis_note"] == MRMC_ANALYSIS_NOTE
    assert len(document["rows"]) == 1
    assert "p_value" not in document
    assert "t_test" not in document
