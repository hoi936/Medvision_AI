"""Frozen-assistance reproducibility tests."""

import pytest

from reader_study.frozen_assistance import (
    FrozenAssistanceError,
    validate_event_assistance_bindings,
    validate_frozen_assistance,
)
from reader_study_fixtures import assistance, reader_event


def test_one_validated_snapshot_per_case_is_reused_for_all_assisted_readers():
    record = assistance()
    by_case = validate_frozen_assistance([record], case_ids=["DS001"], study_version="test-v1")
    events = [reader_event(snapshot_id=record["assistance_snapshot_id"]) for _ in range(2)]
    assert validate_event_assistance_bindings(events, by_case) is True
    assert record["finalized"] is False


def test_output_hash_mismatch_and_duplicate_snapshot_fail_closed():
    record = assistance()
    record["hermes_output"] = "mutated after freeze"
    with pytest.raises(FrozenAssistanceError, match="hash mismatch"):
        validate_frozen_assistance([record], case_ids=["DS001"], study_version="test-v1")
    first = assistance()
    second = assistance(output="Different output")
    with pytest.raises(FrozenAssistanceError, match="multiple assistance snapshots"):
        validate_frozen_assistance([first, second], case_ids=["DS001"], study_version="test-v1")


def test_assisted_event_cannot_bind_a_different_snapshot():
    record = assistance()
    by_case = validate_frozen_assistance([record], case_ids=["DS001"], study_version="test-v1")
    with pytest.raises(FrozenAssistanceError, match="snapshot mismatch"):
        validate_event_assistance_bindings(
            [reader_event(snapshot_id="ASSIST-WRONG")], by_case
        )


def test_assistance_must_be_validated_and_cover_every_case():
    record = assistance()
    record["validation_state"] = "REJECTED"
    with pytest.raises(FrozenAssistanceError, match="not validated"):
        validate_frozen_assistance([record], case_ids=["DS001"], study_version="test-v1")
    with pytest.raises(FrozenAssistanceError, match="case mismatch"):
        validate_frozen_assistance([], case_ids=["DS001"], study_version="test-v1")


def test_assistance_is_bound_to_the_frozen_ui_version():
    with pytest.raises(FrozenAssistanceError, match="UI version mismatch"):
        validate_frozen_assistance(
            [assistance()], case_ids=["DS001"], study_version="test-v1",
            ui_version="different-ui",
        )
