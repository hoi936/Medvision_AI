"""Provider-independent End-to-End Clinical Validation Harness v1 tests."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from e2e.e2e_clinical_validation import run_e2e_case
from e2e.e2e_helpers import STAGE_ORDER
from e2e.e2e_invariants import evaluate_invariants
from e2e.e2e_trace_validator import E2ETraceValidationError, validate_trace
from hermes_report import CORE_HERMES_SKILLS, FINDING_SKILL_MAP, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = Path(__file__).parent / "golden_cases" / "e2e_clinical_validation" / "cases.json"
REFERENCE_ROOT = Path(__file__).parent / "e2e" / "references"
SOURCE_SHA256 = {
    "E2E_CLINICAL_VALIDATION_EVIDENCE.md": "65723600699beecd1eaddfa154469fc4ec0841c8b9d902cb7af52c1a65e98045",
    "E2E_CLINICAL_VALIDATION_POLICY.md": "e5eb8505e83ee6ca58edb7c133fa1433ef3c974466e160410782e6bd9c6e7d6e",
    "references.md": "db649d8756757aa0cf856a414e48c7c0d342505d04d18cd6feafb3df3019c67a",
}
ALL_INVARIANTS = {
    "PROVENANCE_PRESERVED", "MISSING_STAYS_UNKNOWN",
    "NO_SCORE_TO_DISEASE_PROBABILITY", "NO_UNSUPPORTED_ETIOLOGY",
    "NO_UNSUPPORTED_DIAGNOSIS", "OVERLAP_NOT_DOUBLE_COUNTED",
    "CONFLICT_PRESERVED", "SAFETY_ESCALATION_WHEN_SUPPORTED",
    "NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE", "DOCTOR_REVIEW_REQUIRED",
    "TEMPORAL_STATE_VALID", "ARBITRATION_NO_RANKING",
    "DOCTOR_REVIEW_SNAPSHOT_IMMUTABLE", "FINAL_REPORT_FROM_REVIEW_ONLY",
    "FINAL_REPORT_VERSION_BOUND", "NO_AUTO_FINALIZATION",
}


def _cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _cases() if case["id"] == case_id)


def _trace(case_id):
    return run_e2e_case(_case(case_id))[0]


def test_pack_has_exactly_thirty_six_multistage_cases():
    cases = _cases()
    assert len(cases) == 36
    assert [case["id"] for case in cases] == [f"E2E{number:02d}" for number in range(1, 37)]
    assert all(case["model_results"] for case in cases)
    assert all("doctor_review" in case or case["id"] not in {"E2E06", "E2E10", "E2E23", "E2E24", "E2E25", "E2E26", "E2E29", "E2E36"} for case in cases)


@pytest.mark.parametrize("case", _cases(), ids=lambda case: case["id"])
def test_each_case_traverses_complete_trace_and_matches_expected_boundaries(case):
    trace, result = run_e2e_case(case)
    assert validate_trace(trace) == "E2E_TRACE_COMPLETE"
    assert trace["routing"]["canonical_positive_findings"] == case["expected_positive_findings"]
    assert trace["routing"]["no_finding_state"] == case["expected_no_finding_state"]
    assert trace["final_report"]["candidate_status"] == case["expected_final_status"]
    assert [item["stage"] for item in trace["stage_snapshots"]] == STAGE_ORDER
    assert all(item["execution_mode"] in {"project_code", "fixture"} for item in trace["stage_snapshots"])
    expected_failure = case["expected_failure_invariant"]
    if expected_failure:
        assert result["status"] == "fail"
        assert result["failure_class"] == "CLINICAL_SEMANTIC_FAILURE"
        assert result["invariants"]["failed"] == [expected_failure]
    else:
        assert result["status"] == "pass"
        assert result["invariants"]["failed"] == []


def test_routing_is_positive_decision_only_once_in_payload_order_without_no_finding_skill():
    for case in _cases():
        trace = run_e2e_case(case)[0]
        selected = trace["routing"]["selected_skills"]
        expected_finding_skills = [FINDING_SKILL_MAP[name] for name in case["expected_positive_findings"]]
        assert selected == [CORE_HERMES_SKILLS[0], *expected_finding_skills, *CORE_HERMES_SKILLS[1:]]
        assert len(selected) == len(set(selected))
        assert "medvision-no-finding" not in selected

    payload = deepcopy(_trace("E2E01")["input"]["case_data_snapshot"])
    payload["model_findings"]["findings"][0]["score"] = 0.0
    payload["model_findings"]["findings"][0]["threshold"] = 1.0
    assert "medvision-atelectasis" in resolve_hermes_skills(payload)


def test_no_finding_paths_and_later_external_findings_never_rewrite_cxr_state():
    assert _trace("E2E01")["routing"]["no_finding_state"] == "POSITIVE_FINDING_WITH_NO_FINDING_NEGATIVE"
    assert _trace("E2E03")["routing"]["no_finding_state"] == "NO_FINDING_WITHIN_14_CLASS_TAXONOMY"
    assert _trace("E2E04")["routing"]["no_finding_state"] == "NO_FINDING_CONTRADICTION"
    assert _trace("E2E05")["routing"]["no_finding_state"] == "NO_FINDING_MISSING"
    assert _trace("E2E22")["routing"]["no_finding_state"] == "NO_FINDING_NOT_ESTABLISHED"
    added = _trace("E2E25")
    assert added["routing"]["canonical_positive_findings"] == []
    assert added["routing"]["selected_skills"] == list(CORE_HERMES_SKILLS)
    assert added["routing"]["no_finding_state"] == "NO_FINDING_WITHIN_14_CLASS_TAXONOMY"


def test_static_fixtures_are_explicitly_owned_fixed_and_never_presented_as_inference():
    trace = _trace("E2E36")
    fixtures = [item for item in trace["stage_snapshots"] if item["execution_mode"] == "fixture"]
    assert fixtures
    assert all(item["fixture_id"].startswith("FIXTURE-") for item in fixtures)
    assert all(item["owning_module"] for item in fixtures)
    assert all(item["fixed_timestamp"] == "2026-09-29T09:00:00+07:00" for item in fixtures)
    assert set(item["stage"] for item in trace["stage_snapshots"] if item["execution_mode"] == "project_code") == {
        "E2E_STAGE_INPUT", "E2E_STAGE_ROUTING", "E2E_STAGE_DOCTOR_REVIEW", "E2E_STAGE_FINAL_REPORT"
    }


def test_normalized_traces_are_deterministic_and_source_snapshots_are_immutable():
    for case_id in ("E2E04", "E2E13", "E2E23", "E2E24", "E2E25", "E2E30", "E2E36"):
        first = _trace(case_id)
        second = _trace(case_id)
        assert first["input"]["snapshot_hash"] == second["input"]["snapshot_hash"]
        assert first["draft_report"]["snapshot_hash"] == second["draft_report"]["snapshot_hash"]
        assert first["final_report"]["candidate_hash"] == second["final_report"]["candidate_hash"]
        assert all(first["source_immutability"].values())
        assert first["doctor_review"]["snapshot_hash_before"] == first["doctor_review"]["snapshot_hash_after"]
        assert all(item["source_ids"] for item in first["stage_snapshots"] if item["active"])


def test_unexpected_doctor_review_mutation_emits_required_failure_label():
    trace = _trace("E2E24")
    trace["doctor_review"]["snapshot_hash_after"] = "mutated"
    result = next(
        item for item in evaluate_invariants(trace)
        if item["invariant"] == "DOCTOR_REVIEW_SNAPSHOT_IMMUTABLE"
    )
    assert result["status"] == "fail"
    assert result["message"] == "E2E_UNEXPECTED_STAGE_MUTATION"


def test_disease_temporal_and_arbitration_handoffs_preserve_frozen_states():
    assert _trace("E2E08")["arbitration"]["relations"] == ["SHARED_EVIDENCE"]
    assert _trace("E2E09")["arbitration"]["relations"] == ["COEXISTING_PROCESSES_SUPPORTED"]
    assert _trace("E2E13")["temporal"]["comparisons"][0]["state"] == "WORSENED"
    assert _trace("E2E20")["temporal"]["comparisons"][0]["state"] == "COMPARISON_NOT_POSSIBLE"
    assert _trace("E2E22")["temporal"]["comparisons"][0]["state"] == "TEMPORAL_CONFLICT"
    assert _trace("E2E34")["arbitration"]["evidence_ledger"][0]["canonical_evidence_id"] == "OPACITY-GROUP-1"


def test_doctor_review_and_final_report_gates_fail_closed():
    assert _trace("E2E23")["final_report"]["candidate_snapshot"]["findings"]["structured_items"] == []
    modified = _trace("E2E24")["final_report"]["candidate_snapshot"]["findings"]["structured_items"]
    assert modified[0]["text"] == "small right pleural effusion"
    assert _trace("E2E26")["final_report"]["candidate_status"] == "FINAL_REPORT_BLOCKED_BY_REVIEW"
    assert _trace("E2E27")["final_report"]["candidate_status"] == "FINAL_REPORT_VERSION_MISMATCH"
    assert _trace("E2E28")["final_report"]["candidate_status"] == "FINAL_REPORT_SOURCE_MISMATCH"
    assert _trace("E2E35")["final_report"]["candidate_status"] == "FINAL_REPORT_NOT_GENERATABLE"


def test_full_stress_case_evaluates_and_passes_all_sixteen_invariants():
    trace, result = run_e2e_case(_case("E2E36"))
    assert {item["invariant"] for item in trace["invariant_results"]} == ALL_INVARIANTS
    assert all(item["status"] == "pass" for item in trace["invariant_results"])
    assert result["status"] == "pass"
    assert len(trace["disease_analysis"]["module_outputs"]) == 3
    assert trace["temporal"]["activated"] is True
    assert trace["arbitration"]["activated"] is True
    assert trace["safety"]["priority"] == "high"
    assert trace["final_report"]["finalized"] is False


@pytest.mark.parametrize(
    ("corruption", "expected"),
    [
        ({"score_probability": True}, "NO_SCORE_TO_DISEASE_PROBABILITY"),
        ({"missing_negative": True}, "MISSING_STAYS_UNKNOWN"),
        ({"rejected_restored": True}, "FINAL_REPORT_FROM_REVIEW_ONLY"),
        ({"conflict_removed": True}, "CONFLICT_PRESERVED"),
        ({"stale_version_accepted": True}, "FINAL_REPORT_VERSION_BOUND"),
        ({"raw_ai_to_final": True}, "DOCTOR_REVIEW_REQUIRED"),
        ({"autonomous_action": True}, "NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE"),
        ({"auto_finalized": True}, "NO_AUTO_FINALIZATION"),
        ({"duplicate_support": True}, "OVERLAP_NOT_DOUBLE_COUNTED"),
    ],
)
def test_deliberate_semantic_corruption_is_detected(corruption, expected):
    trace = _trace("E2E36")
    trace["violations"] = corruption
    failed = [item["invariant"] for item in evaluate_invariants(trace) if item["status"] == "fail"]
    assert failed == [expected]


def test_trace_validator_rejects_bad_order_hash_and_fixture_metadata():
    trace = _trace("E2E36")
    broken = deepcopy(trace)
    broken["stage_snapshots"][1]["ordinal"] = 1
    with pytest.raises(E2ETraceValidationError, match="stage order/ordinal"):
        validate_trace(broken)
    broken = deepcopy(trace)
    broken["stage_snapshots"][0]["sha256"] = "bad"
    with pytest.raises(E2ETraceValidationError, match="E2E_SNAPSHOT_MISMATCH"):
        validate_trace(broken)
    broken = deepcopy(trace)
    fixture = next(item for item in broken["stage_snapshots"] if item["execution_mode"] == "fixture")
    fixture["fixture_id"] = None
    with pytest.raises(E2ETraceValidationError, match="fixture ID missing"):
        validate_trace(broken)


def test_sources_are_byte_identical_and_integration_is_test_only():
    for filename, digest in SOURCE_SHA256.items():
        assert hashlib.sha256((REFERENCE_ROOT / filename).read_bytes()).hexdigest() == digest
    assert len(FINDING_SKILL_MAP) == 14
    assert len(list((PROJECT_ROOT / ".hermes" / "skills").glob("*/SKILL.md"))) == 17
    assert not (PROJECT_ROOT / ".hermes" / "skills" / "medvision-e2e-clinical-validation").exists()
    skill = (PROJECT_ROOT / ".hermes" / "skills" / "medvision-disease-analysis" / "SKILL.md").read_text(encoding="utf-8")
    assert "E2E_CLINICAL_VALIDATION" not in skill
