import pytest

from release_review.risk_register import CORE_RISK_HAZARDS, RiskRegister, RiskRegisterError, seed_core_risk_templates


def test_core_risk_templates_cover_required_current_project_examples_without_incident_claim():
    templates = seed_core_risk_templates()
    assert len(templates) == 15
    assert {item["hazard"] for item in templates} == set(CORE_RISK_HAZARDS)
    assert all(item["template_only"] is True and item["incident_occurred"] is False for item in templates)


def test_software_cannot_mark_risk_accepted_without_external_acceptance():
    risk = seed_core_risk_templates()[0]
    risk["state"] = "ACCEPTED"
    with pytest.raises(RiskRegisterError, match="external risk_acceptance"):
        RiskRegister([risk])


def test_unresolved_high_or_critical_risk_is_blocking():
    risk = seed_core_risk_templates()[0]
    risk["residual_risk"] = "CRITICAL"
    register = RiskRegister([risk])
    assert [item["risk_id"] for item in register.blocking()] == [risk["risk_id"]]
