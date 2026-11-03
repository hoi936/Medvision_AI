"""Task-specific reference-standard contract tests."""

import pytest

from evaluation.reference_standard import (
    ReferenceStandardError,
    validate_case_references,
    validate_reference_standard,
)
from evaluation_fixtures import evaluation_case, reference


@pytest.mark.parametrize(
    ("task", "label"),
    [
        ("finding", "POSITIVE"),
        ("disease_state", "PNEUMONIA_HYPOTHESIS_SUPPORTED"),
        ("temporal_state", "INDETERMINATE"),
        ("arbitration", {"relations": ["SHARED_EVIDENCE"]}),
        ("report_fidelity", {"rejected_content_resurrection": False}),
    ],
)
def test_task_specific_reference_types_are_preserved(task, label):
    result = validate_reference_standard(reference(task, label))
    assert result["task"] == task
    assert result["label"] == label
    assert result["source_ids"]
    assert result["limitations"]


def test_incomplete_reference_fails_closed():
    incomplete = reference()
    incomplete["source_ids"] = []
    with pytest.raises(ReferenceStandardError, match="source_type and source_ids"):
        validate_reference_standard(incomplete)


def test_case_must_cover_every_requested_task_without_binary_coercion():
    case = evaluation_case(references=[reference("finding", "POSITIVE")])
    with pytest.raises(ReferenceStandardError, match="disease_state"):
        validate_case_references(case, ["finding", "disease_state"])


def test_empty_bounded_or_structured_labels_are_incomplete():
    with pytest.raises(ReferenceStandardError):
        validate_reference_standard(reference("disease_state", ""))
    with pytest.raises(ReferenceStandardError):
        validate_reference_standard(reference("report_fidelity", {}))
