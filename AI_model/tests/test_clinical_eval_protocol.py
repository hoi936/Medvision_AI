import pytest

from clinical_evaluation.deployment_snapshot import (
    DeploymentVersionMismatch, build_deployment_snapshot, validate_deployment_match,
)
from clinical_evaluation.prospective_protocol import validate_prospective_protocol
from clinical_evaluation.protocol_schema import ClinicalProtocolError, validate_silent_protocol
from clinical_eval_fixtures import PROSPECTIVE_PROTOCOL, SILENT_PROTOCOL, SYSTEM_SNAPSHOT, clone


def test_valid_silent_and_prospective_protocols_are_infrastructure_only():
    assert validate_silent_protocol(clone(SILENT_PROTOCOL))["mode"] == "SILENT_SHADOW"
    result = validate_prospective_protocol(clone(PROSPECTIVE_PROTOCOL))
    assert result["mode"] == "PROSPECTIVE_INTERVENTIONAL"
    assert result["intervention"]["autonomous_action"] is False


def test_prospective_protocol_requires_predeclared_pause_rules():
    protocol = clone(PROSPECTIVE_PROTOCOL)
    protocol["pause_rules"] = []
    with pytest.raises(ClinicalProtocolError, match="pause_rules"):
        validate_prospective_protocol(protocol)


def test_deployment_snapshot_is_protocol_bound_and_mismatch_creates_new_stratum():
    built = build_deployment_snapshot(SYSTEM_SNAPSHOT, protocol_version="1.0")
    assert built["hermes_version"] == "0.21.4"
    observed = clone(built)
    observed["config_hash"] = "changed"
    with pytest.raises(DeploymentVersionMismatch) as caught:
        validate_deployment_match(built, observed)
    assert caught.value.fields == ["config_hash"]
    assert caught.value.new_stratum_id.startswith("DEPLOY-")
