"""Provider-independent validation of the provider-backed case bank."""

import hashlib
import json
from pathlib import Path

from e2e.e2e_clinical_validation import run_e2e_case
from real_validation.provider_backed_e2e_runner import (
    MANIFEST_PATH,
    SOURCE_CASES_PATH,
    load_manifest,
)


TESTS_ROOT = Path(__file__).parent
REFERENCE_ROOT = TESTS_ROOT / "real_validation" / "references"
EXPECTED_REFERENCE_SHA256 = {
    "PROVIDER_BACKED_E2E_VALIDATION_EVIDENCE.md": "814051a72d1daf0d01cbd4c4f5cfc6f320e2e62f6fa79622ed22bd0a505f9671",
    "PROVIDER_BACKED_E2E_VALIDATION_POLICY.md": "f460558b47f6a2600f368d158858d191315ec4ec036b17299c71898da5a99aaf",
    "references.md": "941d0eb98536a80133679e5bb13efbfa4947131c293116eab1b54fc6437ed0e4",
}


EXPECTED_MAPPING = {
    "PB01": "E2E04", "PB02": "E2E08", "PB03": "E2E09", "PB04": "E2E06",
    "PB05": "E2E07", "PB06": "E2E10", "PB07": "E2E11", "PB08": "E2E12",
    "PB09": "E2E13", "PB10": "E2E16", "PB11": "E2E15", "PB12": "E2E17",
    "PB13": "E2E18", "PB14": "E2E19", "PB15": "E2E20", "PB16": "E2E22",
    "PB17": "E2E23", "PB18": "E2E24", "PB19": "E2E27", "PB20": "E2E31",
    "PB21": "E2E32", "PB22": "E2E33", "PB23": "E2E35", "PB24": "E2E36",
}


def test_manifest_has_exact_real_gate_case_set_and_reuses_source_payloads():
    cases = load_manifest()
    sources = {case["id"]: case for case in json.loads(SOURCE_CASES_PATH.read_text(encoding="utf-8"))}

    assert {case["case_id"]: case["source_case_id"] for case in cases} == EXPECTED_MAPPING
    assert all(case["source_case_id"] in sources for case in cases)
    assert all(case["real_gate"] is True for case in cases)
    assert all(case["robustness_trials"] == 3 for case in cases)
    assert all("model_results" not in case and "evidence_objects" not in case for case in cases)


def test_manifest_reuses_the_exact_frozen_16_invariants():
    source = next(
        case for case in json.loads(SOURCE_CASES_PATH.read_text(encoding="utf-8"))
        if case["id"] == "E2E01"
    )
    trace, result = run_e2e_case(source)
    frozen = [item["invariant"] for item in trace["invariant_results"]]

    assert result["trace_complete"] is True
    assert len(frozen) == 16
    assert all(case["required_invariants"] == frozen for case in load_manifest())


def test_manifest_schema_is_complete_and_has_no_duplicate_ids():
    cases = load_manifest()
    required = {
        "case_id", "source_case_id", "purpose", "required_invariants",
        "doctor_review_fixture", "expected_final_report_state", "real_gate",
        "robustness_trials",
    }
    assert len({case["case_id"] for case in cases}) == len(cases) == 24
    assert all(required <= set(case) for case in cases)
    assert MANIFEST_PATH.is_file()


def test_manifest_doctor_fixture_and_final_state_match_each_source_case():
    sources = {case["id"]: case for case in json.loads(SOURCE_CASES_PATH.read_text(encoding="utf-8"))}
    for manifest_case in load_manifest():
        source_id = manifest_case["source_case_id"]
        trace, _ = run_e2e_case(sources[source_id])
        assert manifest_case["doctor_review_fixture"] == f"FIXTURE-REVIEW-{source_id}"
        assert trace["final_report"]["candidate_status"] == manifest_case["expected_final_report_state"]


def test_supplied_provider_backed_documents_are_preserved_verbatim():
    actual = {
        name: hashlib.sha256((REFERENCE_ROOT / name).read_bytes()).hexdigest()
        for name in EXPECTED_REFERENCE_SHA256
    }
    assert actual == EXPECTED_REFERENCE_SHA256
