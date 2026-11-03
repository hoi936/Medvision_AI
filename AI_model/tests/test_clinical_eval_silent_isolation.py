import pytest

from clinical_evaluation.silent_case_store import SilentCaseStore
from clinical_evaluation.silent_isolation import SilentIsolationBreach, validate_silent_isolation
from clinical_eval_fixtures import ISOLATION, clone


def test_all_silent_isolation_flags_are_false():
    result = validate_silent_isolation(clone(ISOLATION))
    assert result["valid"] is True
    assert result["mode"] == "SILENT_SHADOW"
    assert result["flags"] == ISOLATION


@pytest.mark.parametrize("flag", list(ISOLATION))
def test_any_enabled_flag_is_silent_isolation_breach(flag):
    isolation = clone(ISOLATION)
    isolation[flag] = True
    with pytest.raises(SilentIsolationBreach) as caught:
        validate_silent_isolation(isolation)
    assert caught.value.code == "SILENT_ISOLATION_BREACH"


def test_silent_store_rejects_clinical_finalization():
    store = SilentCaseStore(clone(ISOLATION))
    case = {
        "silent_case_id": "SYN-SILENT-1", "source_case_id": "SYN-1",
        "deployment_version": "DEPLOY-SYN", "ingested_at": "2026-01-01T08:04:00Z",
        "clinical_event_times": {}, "hermes_run_id": "RUN-SYN",
        "hermes_output_hash": "hash", "invariant_result": {},
        "reference_status": "REFERENCE_PENDING", "outcome_linkage": None,
        "finalized": True,
    }
    with pytest.raises(ValueError, match="cannot be clinically finalized"):
        store.add(case)
