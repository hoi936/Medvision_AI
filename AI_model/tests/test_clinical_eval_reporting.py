import csv
import io
import json

from clinical_evaluation.readiness import ClinicalEvaluationHarness
from clinical_evaluation.reporting import build_evaluation_report, render_csv, render_json, render_markdown
from clinical_eval_fixtures import PROSPECTIVE_PROTOCOL, clone


def report_fixture():
    harness = ClinicalEvaluationHarness()
    return build_evaluation_report(
        silent_readiness=harness.assess_silent(),
        interventional_readiness=harness.assess_interventional(clone(PROSPECTIVE_PROTOCOL)),
        synthetic_fixture_results={"tests_passed": 1, "scope": "synthetic_only"},
    )


def test_report_separates_infrastructure_actual_runs_blockers_and_synthetic_results():
    report = report_fixture()
    assert report["harness_status"].endswith("IMPLEMENTED")
    assert report["silent_clinical_evaluation"] == "NOT RUN"
    assert report["prospective_interventional_evaluation"] == "NOT RUN"
    assert report["blockers"]["silent"]
    assert report["synthetic_results_are_clinical_results"] is False
    assert report["clinical_benefit_claim"] is None


def test_json_csv_and_markdown_exports_preserve_no_run_boundary():
    report = report_fixture()
    parsed = json.loads(render_json(report))
    assert parsed["silent_clinical_evaluation"] == "NOT RUN"
    rows = list(csv.DictReader(io.StringIO(render_csv(report))))
    assert [row["status"] for row in rows[:2]] == ["NOT RUN", "NOT RUN"]
    markdown = render_markdown(report)
    assert "SILENT CLINICAL EVALUATION: NOT RUN" in markdown
    assert "PROSPECTIVE INTERVENTIONAL EVALUATION: NOT RUN" in markdown
    assert "No clinical benefit" in markdown
    assert "Synthetic fixture results are not clinical results" in markdown


def test_supplied_reference_files_are_preserved_verbatim():
    import hashlib
    from pathlib import Path

    base = Path(__file__).parents[1] / "clinical_evaluation/references"
    expected_hashes = {
        "SILENT_PROSPECTIVE_CLINICAL_EVALUATION_POLICY.md": "dadcf9a8db3439b695dda00157f41b5dea2ed681fc2402d5911ee1f8b1bcee8c",
        "SILENT_PROSPECTIVE_CLINICAL_EVALUATION_EVIDENCE.md": "623afeb1d2e8cccd05731def655fa2a54a028a775c4388884844efe92414afce",
        "references.md": "a838b5d8f0eebedc8e6738695cff14d42e9d70fa017ae19d7cec231ffb7fe37c",
    }
    for name, expected_hash in expected_hashes.items():
        assert hashlib.sha256((base / name).read_bytes()).hexdigest() == expected_hash
