"""Provider-independent Final Report Generation v1 validation."""

import hashlib
import json
from pathlib import Path
import re

import pytest

from final_report_generation_validator import (
    FinalReportValidationError,
    render_final_report,
)
from doctor_review_validator import build_review_case
from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = Path(__file__).parent / "golden_cases" / "final_report_generation" / "cases.json"
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = DISEASE_SKILL.parent / "references" / "final_report"
EXPECTED_IDS = {f"FR{number:02d}" for number in range(1, 51)}
SOURCE_SHA256 = {
    "FINAL_REPORT_GENERATION_EVIDENCE.md": "bcd471d79af2cbb308d3440780ff83d1f3ff990702af0cbfe97f6fc39b4e4212",
    "FINAL_REPORT_GENERATION_POLICY.md": "5ef9ba30e6ae00625fb14ea15b434d20f21931a1b45bfcb561e453c18972e8b5",
    "references.md": "3432f178ff3284647e502c3ed7caf9fdad372dfbc66f5e583815c9d976789f63",
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


def _candidate(case_id):
    return render_final_report(_case(case_id)["render"])["final_report_candidate"]


def test_pack_has_fifty_cases_with_supported_provenance():
    cases = _load_cases()
    assert len(cases) == 50
    assert {case["id"] for case in cases} == EXPECTED_IDS
    assert all(case["provenance"] for case in cases)
    assert all(set(case["provenance"]) <= {"S1", "S2", "S3", "S4", "S5"} for case in cases)


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_enforces_expected_final_report_boundary(case):
    prompt = build_report_prompt(**case["input"])
    data = json.loads(prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0])
    selected = resolve_hermes_skills(data)
    assert selected[0] == "medvision-evidence-fusion"
    assert selected[-2:] == ["medvision-safety-check", "medvision-disease-analysis"]
    assert len(selected) == len(set(selected))
    assert "requires_doctor_review: true" in prompt

    if case["expected_error"]:
        with pytest.raises(FinalReportValidationError, match=case["expected_error"]):
            render_final_report(case["render"])
        return

    result = render_final_report(case["render"])
    assert set(case["expected_states"]) <= set(result["states"])
    assert set(case["expected_blockers"]) <= set(result["blocking_reasons"])
    if "no_candidate" in case["checks"]:
        assert result["final_report_candidate"] is None
    if result["final_report_candidate"]:
        assert result["source_fingerprint_before"] == result["source_fingerprint_after"]


def test_progressive_loading_uses_existing_skill_without_mapping_or_frontmatter_change():
    content = DISEASE_SKILL.read_text(encoding="utf-8")
    frontmatter = content.split("---", 2)[1]
    assert len(FINDING_SKILL_MAP) == 14
    assert "Final report" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-final-report").exists()
    assert "references/final_report/FINAL_REPORT_GENERATION_POLICY.md" in content
    assert "references/final_report/FINAL_REPORT_GENERATION_EVIDENCE.md" in content
    assert "references/final_report/references.md" in content
    assert "name: medvision-disease-analysis" in frontmatter
    assert "final_report" not in frontmatter.lower()


def test_source_files_are_exact_and_publish_all_required_states():
    for filename, digest in SOURCE_SHA256.items():
        assert hashlib.sha256((MODULE_ROOT / filename).read_bytes()).hexdigest() == digest
    text = "\n".join((MODULE_ROOT / filename).read_text(encoding="utf-8") for filename in SOURCE_SHA256)
    states = {
        "FINAL_REPORT_NOT_GENERATABLE", "FINAL_REPORT_BLOCKED_BY_REVIEW",
        "FINAL_REPORT_SOURCE_MISMATCH", "FINAL_REPORT_VERSION_MISMATCH",
        "FINAL_REPORT_CANDIDATE_READY", "FINAL_REPORT_RENDERED_FROM_REVIEW",
        "FINAL_REPORT_FINALIZED_BY_DOCTOR", "FINAL_REPORT_AMENDMENT_REQUIRED",
        "FINAL_REPORT_SUPERSEDED",
    }
    assert all(state in text for state in states)
    assert all(f"## S{number}" in text for number in range(1, 6))


def test_candidate_contract_is_complete_and_never_self_finalized():
    candidate = _candidate("FR04")
    assert set(candidate) == {
        "report_status", "source_review_id", "source_review_version", "patient_study",
        "clinical_information", "technique", "comparison", "findings", "impression",
        "recommendations", "limitations", "unresolved_items", "provenance", "finalization",
    }
    assert candidate["report_status"] == "candidate"
    assert candidate["finalization"] == {
        "finalized": False, "finalized_by": None, "finalized_at": None
    }
    assert _candidate("FR39")["report_status"] == "final"
    assert _candidate("FR39")["finalization"]["finalized_by"] == "DOC-1"


def test_doctor_review_is_the_only_clinical_source_of_truth():
    accepted = _candidate("FR05")["findings"]["structured_items"]
    modified = _candidate("FR07")["findings"]["structured_items"]
    rejected = _candidate("FR06")["findings"]["structured_items"]
    added = _candidate("FR08")["findings"]["structured_items"]
    assert accepted[0]["source"] == "doctor_accepted_upstream"
    assert modified[0]["text"] == "small right pleural effusion"
    assert modified[0]["source"] == "doctor_authored"
    assert rejected == []
    assert added[0]["source"] == "doctor_authored"


def test_renderer_consumes_native_structured_doctor_review_object():
    review_cases = json.loads(
        (Path(__file__).parent / "golden_cases" / "structured_doctor_review" / "cases.json")
        .read_text(encoding="utf-8")
    )
    review_case = next(case for case in review_cases if case["id"] == "DR29")
    review_case["review"]["review_id"] = "REVIEW-NATIVE-1"
    review = build_review_case(review_case)["doctor_review"]
    result = render_final_report({
        "request_source": "doctor_review",
        "doctor_review": review,
        "candidate_binding": {
            "review_version": review["version"],
            "ai_snapshot_id": review["audit"]["ai_snapshot_id"],
            "hermes_snapshot_id": review["audit"]["hermes_snapshot_id"],
            "draft_report_snapshot_id": review["audit"]["draft_report_snapshot_id"],
        },
    })
    assert result["states"] == [
        "FINAL_REPORT_CANDIDATE_READY", "FINAL_REPORT_RENDERED_FROM_REVIEW"
    ]
    assert result["final_report_candidate"]["source_review_id"] == review["review_id"]
    assert result["final_report_candidate"]["finalization"]["finalized"] is False


def test_rejected_deferred_and_unreviewed_semantics_are_distinct():
    assert _candidate("FR12")["impression"]["structured_items"] == []
    deferred = _candidate("FR09")["findings"]["structured_items"]
    assert deferred == [{
        "id": "F1", "text": "Indeterminate opacity retained for review.",
        "decision": "defer", "source": "doctor_review",
    }]
    blocked = render_final_report(_case("FR10")["render"])
    assert blocked["states"] == ["FINAL_REPORT_BLOCKED_BY_REVIEW"]
    assert "REQUIRED_FINDING_UNREVIEWED" in blocked["blocking_reasons"]


def test_findings_and_impression_do_not_gain_scores_rankings_or_confirmation():
    candidates = [_candidate(case_id) for case_id in ("FR11", "FR13", "FR15", "FR17", "FR18", "FR24", "FR46", "FR47")]
    text = json.dumps(candidates, ensure_ascii=False).lower()
    assert "0.87" not in text and "87%" not in text
    assert not re.search(r"\b(top[- ]?1|winner|rank(?:ed|ing)?\s*#?\d)\b", text)
    assert "microbiologically_confirmed_tb" not in text
    assert "etiology remains uncertain" in text


def test_recommendations_require_explicit_clinician_provenance():
    assert _candidate("FR28")["recommendations"]["source"] == "doctor_authored"
    assert _candidate("FR29")["recommendations"]["source"] == "external_clinician_approved"
    assert _candidate("FR30")["recommendations"] == {"text": None, "source": None}
    for case_id in ("FR31", "FR32", "FR33"):
        with pytest.raises(FinalReportValidationError, match="AUTONOMOUS_RECOMMENDATION_FORBIDDEN"):
            render_final_report(_case(case_id)["render"])


def test_metadata_and_template_fields_stay_missing_without_verified_input():
    candidate = _candidate("FR04")
    assert all(value is None for value in candidate["patient_study"].values())
    assert candidate["clinical_information"]["indication"] is None
    assert candidate["technique"]["text"] is None
    assert candidate["comparison"]["text"] is None
    rendered = json.dumps(candidate, ensure_ascii=False).lower()
    assert "normal chest" not in rendered
    assert "no follow-up needed" not in rendered
    assert "portable" not in rendered


def test_temporal_comparison_is_handoff_only_and_preserves_limitations():
    assert _candidate("FR21")["comparison"]["text"] is None
    assert "stable" in _candidate("FR22")["comparison"]["text"]
    limited = _candidate("FR23")
    assert limited["comparison"]["text"] == "Comparison is limited by differing modalities."
    assert limited["limitations"] == ["Limited cross-modality comparability."]
    config = _case("FR22")["render"]
    config["doctor_review"]["temporal"]["reviewed"] = False
    with pytest.raises(FinalReportValidationError, match="UNREVIEWED_TEMPORAL_STATE_FORBIDDEN"):
        render_final_report(config)


def test_version_snapshot_binding_and_source_immutability_fail_closed():
    assert render_final_report(_case("FR34")["render"])["states"] == ["FINAL_REPORT_VERSION_MISMATCH"]
    assert render_final_report(_case("FR35")["render"])["states"] == ["FINAL_REPORT_SOURCE_MISMATCH"]
    assert render_final_report(_case("FR36")["render"])["states"] == ["FINAL_REPORT_SOURCE_MISMATCH"]
    for case_id in ("FR06", "FR07", "FR08", "FR37", "FR39", "FR42"):
        result = render_final_report(_case(case_id)["render"])
        assert result["source_fingerprint_before"] == result["source_fingerprint_after"]


def test_external_finalization_and_amendment_preserve_history():
    assert _candidate("FR37")["finalization"]["finalized"] is False
    finalized = render_final_report(_case("FR39")["render"])
    assert finalized["states"] == ["FINAL_REPORT_FINALIZED_BY_DOCTOR"]
    amendment = render_final_report(_case("FR42")["render"])
    assert "FINAL_REPORT_AMENDMENT_REQUIRED" in amendment["states"]
    assert amendment["report_history"][0]["text"] == "immutable original"
    superseded = render_final_report(_case("FR43")["render"])
    assert "FINAL_REPORT_SUPERSEDED" in superseded["states"]
    assert superseded["report_history"][0]["report_id"] == "REPORT-1"


def test_communication_event_is_never_fabricated():
    assert render_final_report(_case("FR44")["render"])["communication_event"] is None
    supplied = render_final_report(_case("FR45")["render"])["communication_event"]
    assert supplied == {
        "host_supplied": True, "recipient": "DOC-2",
        "timestamp": "2026-09-29T10:05:00+07:00", "method": "phone",
    }


def test_raw_ai_old_draft_and_no_finding_cannot_override_review():
    assert render_final_report(_case("FR50")["render"])["states"] == ["FINAL_REPORT_NOT_GENERATABLE"]
    assert _candidate("FR49")["findings"]["structured_items"] == []
    current = _candidate("FR20")["findings"]["structured_items"]
    assert [item["text"] for item in current] == ["CT-reviewed pulmonary abnormality"]
