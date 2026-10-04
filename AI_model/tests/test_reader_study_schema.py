"""Reader-study protocol, reader, and event schema tests."""

import hashlib
from pathlib import Path

import pytest

from reader_study.event_log import (
    ReaderEventError, event_duration_seconds, validate_human_factors_issue,
    validate_reader_event,
)
from reader_study.study_schema import StudySchemaError, validate_reader, validate_study_protocol
from reader_study_fixtures import reader, reader_event, study_protocol


REFERENCE_HASHES = {
    "HUMAN_AI_READER_STUDY_EVIDENCE.md": "13d646f96fbde1281e7f88247387c5db21b3586aec37cfca2537e77dc61bd6f6",
    "HUMAN_AI_READER_STUDY_POLICY.md": "e1098de08bf9b7445dbfa2a1ca31bbe2e79839f71032ccdb455c26d8bf61bbb5",
    "references.md": "64f9a8dd8e966a4555b00fd1619a7980309a1c2950028d9a2952ee96e051e071",
}


def test_complete_paired_protocol_selects_one_assistance_mode_and_washout():
    protocol = validate_study_protocol(study_protocol())
    assert set(protocol["conditions"]) == {"UNAIDED", "HERMES_ASSISTED"}
    assert protocol["assistance_mode"] == "DRAFT_REPORT_ASSIST"
    assert protocol["sessions"]["washout"]["rationale"]


def test_protocol_rejects_missing_primary_endpoint_and_incomplete_washout():
    protocol = study_protocol()
    protocol["primary_endpoint"] = ""
    with pytest.raises(StudySchemaError, match="primary_endpoint"):
        validate_study_protocol(protocol)
    protocol = study_protocol()
    protocol["sessions"]["washout"]["rationale"] = ""
    with pytest.raises(StudySchemaError, match="washout"):
        validate_study_protocol(protocol)


def test_protocol_requires_frozen_system_ui_and_approved_storage():
    protocol = study_protocol()
    protocol["system_snapshot"] = {}
    with pytest.raises(StudySchemaError, match="system snapshot"):
        validate_study_protocol(protocol)
    protocol = study_protocol()
    protocol["data_storage"]["status"] = "UNRESOLVED"
    with pytest.raises(StudySchemaError, match="data storage"):
        validate_study_protocol(protocol)


def test_reader_schema_rejects_direct_identifiers():
    item = reader()
    assert validate_reader(item)["assigned_sequence"] == "PENDING"
    item["email"] = "forbidden@example.test"
    with pytest.raises(StudySchemaError, match="direct reader identifiers"):
        validate_reader(item)


def test_event_schema_records_actions_and_time_without_chain_of_thought():
    event = validate_reader_event(reader_event())
    assert event_duration_seconds(event) == 120
    event["chain_of_thought"] = "forbidden"
    with pytest.raises(ReaderEventError, match="chain-of-thought"):
        validate_reader_event(event)


def test_unaided_event_cannot_receive_assistance_snapshot():
    event = reader_event(condition="UNAIDED")
    event["hermes_snapshot_id"] = "ASSIST-FORBIDDEN"
    with pytest.raises(ReaderEventError, match="unaided"):
        validate_reader_event(event)


def test_technical_failure_cannot_be_silently_marked_complete():
    event = reader_event()
    event["technical_status"] = "TECHNICAL_FAILURE"
    with pytest.raises(ReaderEventError, match="silently marked complete"):
        validate_reader_event(event)


def test_human_factors_issue_logs_ui_problem_without_hidden_cognition():
    issue = {
        "issue_id": "HF1", "reader_id": "R1", "case_id": "DS001",
        "condition": "HERMES_ASSISTED", "category": "provenance_unclear",
        "severity": "moderate", "description": "Provenance panel label unclear.",
        "ui_component": "provenance_panel", "reproducible": True,
    }
    assert validate_human_factors_issue(issue) == issue
    issue["reasoning_trace"] = "forbidden"
    with pytest.raises(ReaderEventError, match="chain-of-thought"):
        validate_human_factors_issue(issue)


def test_supplied_reader_study_documents_are_byte_preserved():
    root = Path(__file__).parents[1] / "reader_study" / "references"
    actual = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in REFERENCE_HASHES}
    assert actual == REFERENCE_HASHES
