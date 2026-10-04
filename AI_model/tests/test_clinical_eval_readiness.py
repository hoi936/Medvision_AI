from clinical_evaluation.readiness import ClinicalEvaluationHarness, ClinicalEvaluationState
from clinical_eval_fixtures import (
    DATA_SOURCE_CONTRACT, GOVERNANCE_APPROVAL, PROVIDER_EVIDENCE,
    PROSPECTIVE_PROTOCOL, SILENT_PROTOCOL, authorized_event, clone,
)


def test_scaffold_and_missing_protocol_states_are_explicit():
    harness = ClinicalEvaluationHarness()
    assert harness.scaffold_status().state == ClinicalEvaluationState.CLINICAL_EVAL_SCAFFOLD_READY
    missing = harness.assess_silent()
    assert missing.state == ClinicalEvaluationState.SILENT_PROTOCOL_INCOMPLETE
    assert "protocol not configured" in missing.blockers


def test_missing_data_source_and_provider_fail_closed():
    harness = ClinicalEvaluationHarness()
    missing_source = harness.assess_silent(clone(SILENT_PROTOCOL), [])
    assert missing_source.state == ClinicalEvaluationState.SILENT_DATA_SOURCE_MISSING
    provider_blocked = harness.assess_silent(clone(SILENT_PROTOCOL), [clone(DATA_SOURCE_CONTRACT)])
    assert provider_blocked.state == ClinicalEvaluationState.SILENT_PROVIDER_BLOCKED


def test_unresolved_ethics_privacy_and_security_block_readiness():
    harness = ClinicalEvaluationHarness()
    protocol = clone(SILENT_PROTOCOL)
    protocol["ethics"]["status"] = "UNRESOLVED"
    result = harness.assess_silent(protocol, [clone(DATA_SOURCE_CONTRACT)], clone(PROVIDER_EVIDENCE))
    assert result.state == ClinicalEvaluationState.SILENT_ETHICS_STATUS_UNRESOLVED
    protocol = clone(SILENT_PROTOCOL)
    protocol["security"]["status"] = "UNRESOLVED"
    result = harness.assess_silent(protocol, [clone(DATA_SOURCE_CONTRACT)], clone(PROVIDER_EVIDENCE))
    assert result.state == ClinicalEvaluationState.SILENT_SECURITY_STATUS_UNRESOLVED


def test_isolation_breach_fails_readiness_with_incident_category():
    protocol = clone(SILENT_PROTOCOL)
    protocol["isolation"]["doctor_message_enabled"] = True
    result = ClinicalEvaluationHarness().assess_silent(
        protocol, [clone(DATA_SOURCE_CONTRACT)], clone(PROVIDER_EVIDENCE)
    )
    assert result.state == ClinicalEvaluationState.SILENT_FAILED
    assert result.incident_category == "SILENT_ISOLATION_BREACH"


def test_ready_does_not_mean_running_without_explicit_authorized_event():
    harness = ClinicalEvaluationHarness()
    ready = harness.assess_silent(
        clone(SILENT_PROTOCOL), [clone(DATA_SOURCE_CONTRACT)], clone(PROVIDER_EVIDENCE)
    )
    assert ready.state == ClinicalEvaluationState.SILENT_READY
    assert ready.actual_run_started is False
    failed = harness.authorize_silent_start(ready, clone(SILENT_PROTOCOL), {})
    assert failed.state == ClinicalEvaluationState.SILENT_FAILED
    running = harness.authorize_silent_start(
        ready, clone(SILENT_PROTOCOL), authorized_event("SILENT")
    )
    assert running.state == ClinicalEvaluationState.SILENT_RUNNING
    assert running.actual_run_started is True


def test_authorized_start_must_match_protocol_and_snapshot():
    harness = ClinicalEvaluationHarness()
    ready = harness.assess_silent(
        clone(SILENT_PROTOCOL), [clone(DATA_SOURCE_CONTRACT)], clone(PROVIDER_EVIDENCE)
    )
    event = authorized_event("SILENT")
    event["snapshot_hash"] = "wrong"
    assert harness.authorize_silent_start(ready, clone(SILENT_PROTOCOL), event).state == ClinicalEvaluationState.SILENT_FAILED


def test_interventional_needs_protocol_then_explicit_governance_review():
    harness = ClinicalEvaluationHarness()
    assert harness.assess_interventional().state == ClinicalEvaluationState.INTERVENTIONAL_PROTOCOL_INCOMPLETE
    review = harness.assess_interventional(clone(PROSPECTIVE_PROTOCOL))
    assert review.state == ClinicalEvaluationState.INTERVENTIONAL_READINESS_REVIEW_REQUIRED
    assert review.actual_run_started is False


def test_governance_approval_makes_ready_but_never_auto_starts():
    harness = ClinicalEvaluationHarness()
    ready = harness.assess_interventional(clone(PROSPECTIVE_PROTOCOL), clone(GOVERNANCE_APPROVAL))
    assert ready.state == ClinicalEvaluationState.INTERVENTIONAL_READY
    assert ready.actual_run_started is False
    running = harness.authorize_interventional_start(
        ready, clone(PROSPECTIVE_PROTOCOL), authorized_event("INTERVENTIONAL")
    )
    assert running.state == ClinicalEvaluationState.INTERVENTIONAL_RUNNING
    assert running.actual_run_started is True


def test_silent_software_metrics_never_promote_interventional_state():
    harness = ClinicalEvaluationHarness()
    silent = harness.assess_silent(
        clone(SILENT_PROTOCOL), [clone(DATA_SOURCE_CONTRACT)], clone(PROVIDER_EVIDENCE)
    )
    assert silent.state == ClinicalEvaluationState.SILENT_READY
    assert harness.assess_interventional(clone(PROSPECTIVE_PROTOCOL)).state == ClinicalEvaluationState.INTERVENTIONAL_READINESS_REVIEW_REQUIRED
