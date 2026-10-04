import csv
import hashlib
import io
import json
from pathlib import Path

from release_review.readiness import ReleaseReviewHarness
from release_review.reporting import build_report, render_evidence_csv, render_json, render_markdown
from release_review_fixtures import current_baseline_review


def report_fixture():
    review = current_baseline_review("PRODUCTION_CLINICAL_USE")
    return build_report(review, ReleaseReviewHarness().assess(review))


def test_report_includes_required_governance_sections_and_no_composite_score():
    report = report_fixture()
    assert report["harness_status"] == "RELEASE-READINESS & SAFETY REVIEW HARNESS: IMPLEMENTED"
    for field in (
        "target_stage", "system_snapshot", "evidence_inventory", "blockers",
        "conditions", "incomplete_evidence", "residual_risks", "monitoring_plan", "rollback_plan",
        "governance_status", "decision", "limitations",
    ):
        assert field in report
    serialized = json.dumps(report).lower()
    assert "release_score" not in serialized
    assert "overall_score" not in serialized
    assert "safety_score" not in serialized


def test_json_csv_and_markdown_preserve_blocked_decision_and_limitations():
    report = report_fixture()
    assert json.loads(render_json(report))["decision"] == "RELEASE_BLOCKED"
    rows = list(csv.DictReader(io.StringIO(render_evidence_csv(report))))
    assert len(rows) == len(report["evidence_inventory"])
    assert next(row for row in rows if row["evidence_id"] == "EV-PROVIDER")["status"] == "NOT_AVAILABLE"
    markdown = render_markdown(report)
    assert "PRODUCTION_CLINICAL_USE" in markdown
    assert "RELEASE_BLOCKED" in markdown
    assert "does not claim regulatory compliance" in markdown


def test_supplied_release_review_references_are_preserved_verbatim():
    base = Path(__file__).parents[1] / "release_review/references"
    expected = {
        "RELEASE_READINESS_SAFETY_REVIEW_EVIDENCE.md": "0f704f19eb89cb6dc9a29417305ec00242a7efd3d36514e1dc6ddd326a191d38",
        "RELEASE_READINESS_SAFETY_REVIEW_POLICY.md": "995de7e34e33f5d6f5c2c45c8c69788e5c5ff4c18ca9cb900d47c032738f06f3",
        "references.md": "564febec024bb846f4f691b64aa0ea369a2419aecd75dcd07c598175cd1776e9",
    }
    for name, digest in expected.items():
        assert hashlib.sha256((base / name).read_bytes()).hexdigest() == digest
