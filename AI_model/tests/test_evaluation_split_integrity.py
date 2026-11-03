"""Leakage and duplicate detection tests."""

import pytest

from evaluation.split_integrity import SplitIntegrityError, inspect_split_integrity, validate_split_integrity
from evaluation_fixtures import evaluation_case, manifest


def _codes(cases):
    return {item["code"] for item in inspect_split_integrity(manifest(cases), cases)["violations"]}


def test_clean_patient_level_split_passes():
    cases = [
        evaluation_case("DS001", "P1", "S1", "development"),
        evaluation_case("DS002", "P2", "S2", "evaluation"),
    ]
    assert validate_split_integrity(manifest(cases), cases) == {"valid": True, "violations": []}


def test_patient_and_longitudinal_leakage_fail_closed():
    cases = [
        evaluation_case("DS001", "P1", "S1", "development"),
        evaluation_case("DS002", "P1", "S2", "evaluation"),
    ]
    assert {"PATIENT_OVERLAP", "LONGITUDINAL_PATIENT_LEAKAGE"} <= _codes(cases)
    with pytest.raises(SplitIntegrityError):
        validate_split_integrity(manifest(cases), cases)


def test_study_case_and_protected_hash_duplicates_are_detected():
    study_cases = [
        evaluation_case("DS001", "P1", "SAME", "development"),
        evaluation_case("DS002", "P2", "SAME", "evaluation"),
    ]
    assert "STUDY_OVERLAP" in _codes(study_cases)
    duplicate_cases = [
        evaluation_case("DS001", "P1", "S1", "development"),
        evaluation_case("DS001", "P2", "S2", "evaluation"),
    ]
    assert "DUPLICATE_CASE" in _codes(duplicate_cases)
    hash_cases = [
        evaluation_case("DS001", "P1", "S1", "development", content_hash="abc"),
        evaluation_case("DS002", "P2", "S2", "evaluation", content_hash="abc"),
    ]
    assert "PROTECTED_SPLIT_HASH_DUPLICATE" in _codes(hash_cases)


def test_golden_and_provider_backed_case_ids_are_rejected():
    for case_id in ("E2E04", "PB01"):
        assert "GOLDEN_CASE_REUSE" in _codes([evaluation_case(case_id=case_id)])
