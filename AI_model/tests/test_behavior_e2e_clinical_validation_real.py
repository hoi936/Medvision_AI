"""Provider-backed End-to-End Clinical Validation v1 REAL_GATE cases."""

import os

import pytest

from hermes_real_runtime import ProviderPreflightError, run_provider_preflight
from real_validation.provider_backed_e2e_runner import ProviderBackedE2ERunner, load_manifest


RUN_REAL = os.environ.get("RUN_HERMES_REAL") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_REAL,
    reason="real Hermes tests disabled; set RUN_HERMES_REAL=1 to use the configured provider",
)
REAL_CASE_IDS = [case["case_id"] for case in load_manifest() if case["real_gate"]]


@pytest.fixture(scope="module")
def provider_preflight():
    try:
        return run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")


@pytest.fixture(scope="module")
def real_artifact_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("provider-backed-e2e")


@pytest.mark.parametrize("case_id", REAL_CASE_IDS)
def test_provider_backed_real_gate(case_id, provider_preflight, real_artifact_dir):
    result = ProviderBackedE2ERunner().run_case(
        case_id,
        artifact_dir=real_artifact_dir,
        preflight_metadata=provider_preflight,
    )["provider_backed_result"]
    failure = result["failure"]
    assert failure["class"] == "PASS", (
        f"{failure['class']}: {case_id}: "
        f"{failure['first_invariant'] or 'infrastructure'}: {failure['message']}"
    )
    assert len(result["invariants"]["passed"]) == 16
    assert result["invariants"]["failed"] == []
    assert len(result["execution"]["attempts"]) == 1
    assert result["report"]["finalized"] is False
