"""Readiness gates, isolation, and explicit session start tests."""

import pytest

from reader_study.case_manifest import CaseIsolationError, validate_case_isolation, validate_reader_case
from reader_study.protocol import ReaderStudyHarness, ReaderStudyState
from reader_study.randomization import build_randomization_plan
from reader_study.session_manager import begin_session, build_session_plan
from reader_study_fixtures import assistance, reader, study_case, study_protocol, training_case


def test_unconfigured_study_reports_all_actual_study_blocker_categories():
    result = ReaderStudyHarness().assess(
        protocol=None, readers=None, training_cases=None,
        evaluation_cases=None, frozen_assistance=None,
    )
    assert result["state"] == ReaderStudyState.PROTOCOL_INCOMPLETE.value
    assert result["actual_study_run"] is False
    assert result["readiness_blockers"] == [
        "protocol not configured", "independent dataset not configured",
        "readers not configured", "ethics/privacy determination unresolved",
        "provider/frozen assistance not configured",
    ]


def test_unresolved_ethics_is_not_assumed_exempt():
    result = ReaderStudyHarness().assess(
        protocol=study_protocol(ethics_status="UNRESOLVED"),
        readers=[reader("R1"), reader("R2")],
        training_cases=[training_case()], evaluation_cases=[study_case()],
        frozen_assistance=[assistance()],
    )
    assert result["state"] == ReaderStudyState.ETHICS_STATUS_UNRESOLVED.value
    assert "ethics/privacy" in result["readiness_blockers"][0]


def test_missing_dataset_readers_and_assistance_have_distinct_states():
    harness = ReaderStudyHarness()
    missing_dataset = harness.assess(
        protocol=study_protocol(), readers=[], training_cases=[],
        evaluation_cases=[], frozen_assistance=[],
    )
    assert missing_dataset["state"] == ReaderStudyState.DATASET_MISSING.value
    missing_readers = harness.assess(
        protocol=study_protocol(), readers=[], training_cases=[training_case()],
        evaluation_cases=[study_case()], frozen_assistance=[assistance()],
    )
    assert missing_readers["state"] == ReaderStudyState.READERS_MISSING.value
    missing_assistance = harness.assess(
        protocol=study_protocol(), readers=[reader("R1"), reader("R2")],
        training_cases=[training_case()], evaluation_cases=[study_case()], frozen_assistance=[],
    )
    assert missing_assistance["state"] == ReaderStudyState.PROVIDER_BLOCKED.value


def test_training_overlap_golden_case_and_reference_leakage_fail_closed():
    evaluation = study_case()
    overlapping = training_case(case_id=evaluation["case_id"])
    with pytest.raises(CaseIsolationError) as exc_info:
        validate_case_isolation([overlapping], [evaluation])
    assert "TRAINING_CASE_OVERLAP" in {item["code"] for item in exc_info.value.violations}

    golden = study_case(case_id="E2E04")
    with pytest.raises(CaseIsolationError) as exc_info:
        validate_case_isolation([], [golden])
    assert "GOLDEN_CASE_AS_EVALUATION" in {item["code"] for item in exc_info.value.violations}

    leaked = study_case()
    leaked["metadata"]["reader_visible_fields"].append("reference_standards")
    with pytest.raises(CaseIsolationError) as exc_info:
        validate_case_isolation([], [leaked])
    assert "REFERENCE_STANDARD_LEAKAGE" in {item["code"] for item in exc_info.value.violations}

    incomplete_binding = study_case()
    incomplete_binding["metadata"].pop("case_stratum")
    with pytest.raises(CaseIsolationError, match="READER_CASE_BINDING_INCOMPLETE"):
        validate_reader_case(incomplete_binding)


def test_training_set_is_required_even_when_protocol_names_one():
    result = ReaderStudyHarness().assess(
        protocol=study_protocol(), readers=[reader("R1"), reader("R2")],
        training_cases=[], evaluation_cases=[study_case()],
        frozen_assistance=[assistance()],
    )
    assert result["state"] == ReaderStudyState.PROTOCOL_INCOMPLETE.value
    assert "training set" in result["readiness_blockers"][0]


def test_complete_configuration_becomes_ready_but_never_starts_automatically():
    result = ReaderStudyHarness().assess(
        protocol=study_protocol(), readers=[reader("R1"), reader("R2")],
        training_cases=[training_case()], evaluation_cases=[study_case()],
        frozen_assistance=[assistance()],
    )
    assert result["state"] == ReaderStudyState.READY.value
    assert result["actual_study_run"] is False
    assert {item["assigned_sequence"] for item in result["readers"]} == {"AB", "BA"}

    plan = build_randomization_plan(
        result["readers"], ["DS001"],
        session_ids=["SESSION-1", "SESSION-2"], seed=17,
    )
    session = build_session_plan(
        result["readers"], plan,
        study_id="SYNTHETIC-READER-STUDY", ui_version="synthetic-ui-v1",
    )[0]
    with pytest.raises(PermissionError, match="explicit authorized start"):
        begin_session(session)


def test_state_vocabulary_is_exact():
    assert {state.value for state in ReaderStudyState} == {
        "READER_STUDY_SCAFFOLD_READY", "READER_STUDY_PROTOCOL_INCOMPLETE",
        "READER_STUDY_DATASET_MISSING", "READER_STUDY_PROVIDER_BLOCKED",
        "READER_STUDY_ETHICS_STATUS_UNRESOLVED", "READER_STUDY_READERS_MISSING",
        "READER_STUDY_READY", "READER_STUDY_RUNNING",
        "READER_STUDY_COMPLETE", "READER_STUDY_FAILED",
    }
