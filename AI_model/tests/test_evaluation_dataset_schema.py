"""Dataset manifest/case schema tests."""

import hashlib
from pathlib import Path

import pytest

from evaluation.dataset_loader import IndependentDatasetRequiredError, load_dataset
from evaluation.dataset_schema import DatasetSchemaError, validate_case, validate_manifest
from evaluation_fixtures import evaluation_case, manifest, write_dataset


REFERENCE_HASHES = {
    "CLINICAL_DATASET_EVALUATION_EVIDENCE.md": "06cd942fadca646c20804907d8a24b82035fef38b14be7330ec02fa8cfec1ef5",
    "CLINICAL_DATASET_EVALUATION_POLICY.md": "21363af9a0e83e19acfa6b5e1c6b6f3ffb9e35ccfa76cfb281ecb68b9cb41f9d",
    "references.md": "9a0aa1ddbd5c65e8c5728616554947532c38f7a47e2901125108e72277889cb7",
}


def test_valid_manifest_and_case_preserve_explicit_missingness_states(tmp_path):
    case = evaluation_case()
    validated = validate_case(case)
    validate_manifest(manifest([case]))
    path = write_dataset(tmp_path, [case])
    loaded_manifest, loaded_cases = load_dataset(path)
    assert loaded_manifest["deidentified"] is True
    assert loaded_cases[0]["missingness"] == {
        "laboratory": "MISSING", "microbiology": "UNKNOWN",
        "pathology": "EXPLICIT_NEGATIVE", "imaging": "POSITIVE",
    }


def test_case_rejects_direct_identifiers_and_invalid_missingness():
    direct = evaluation_case()
    direct["clinical"]["patient_name"] = "forbidden"
    with pytest.raises(DatasetSchemaError, match="direct patient identifier"):
        validate_case(direct)
    invalid = evaluation_case()
    invalid["missingness"]["laboratory"] = ""
    with pytest.raises(DatasetSchemaError, match="invalid missingness"):
        validate_case(invalid)


def test_loader_never_selects_a_dataset_implicitly_or_from_golden_cases():
    with pytest.raises(IndependentDatasetRequiredError, match="not configured"):
        load_dataset(None)
    golden = Path(__file__).parent / "golden_cases" / "e2e_clinical_validation" / "cases.json"
    with pytest.raises(IndependentDatasetRequiredError, match="cannot be used"):
        load_dataset(golden)


def test_supplied_evaluation_documents_are_byte_preserved():
    root = Path(__file__).parents[1] / "evaluation" / "references"
    actual = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in REFERENCE_HASHES}
    assert actual == REFERENCE_HASHES
