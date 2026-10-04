import pytest

from clinical_evaluation.data_source_contract import DataSourceContractError, classify_payload_fields, validate_data_source_contract
from clinical_eval_fixtures import DATA_SOURCE_CONTRACT, SYNTHETIC_PAYLOAD, clone


def test_contract_has_explicit_owner_allowlist_exclusions_and_time_semantics():
    contract = validate_data_source_contract(clone(DATA_SOURCE_CONTRACT))
    assert contract["owner"]
    assert "patient_name" in contract["fields_excluded"]
    assert "acquisition_time" in contract["timestamp_semantics"]


def test_unknown_field_is_rejected_or_quarantined_by_explicit_policy():
    payload = clone(SYNTHETIC_PAYLOAD)
    payload["unknown_clinical_field"] = "must not enter"
    assert classify_payload_fields(clone(DATA_SOURCE_CONTRACT), payload)["status"] == "REJECTED"
    contract = clone(DATA_SOURCE_CONTRACT)
    contract["unknown_field_policy"] = "QUARANTINE"
    assert classify_payload_fields(contract, payload)["status"] == "QUARANTINED"


def test_excluded_direct_identifier_is_always_rejected():
    payload = clone(SYNTHETIC_PAYLOAD)
    payload["patient_name"] = "synthetic prohibited identifier"
    result = classify_payload_fields(clone(DATA_SOURCE_CONTRACT), payload)
    assert result == {"status": "REJECTED", "reason": "excluded fields present", "fields": ["patient_name"]}


def test_generic_contract_without_validation_rules_is_invalid():
    contract = clone(DATA_SOURCE_CONTRACT)
    contract["validation_rules"] = []
    with pytest.raises(DataSourceContractError, match="pre-specified"):
        validate_data_source_contract(contract)
