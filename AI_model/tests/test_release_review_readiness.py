from release_review.readiness import ReleaseReviewHarness, ReleaseReviewState
from release_review_fixtures import (
    current_baseline_review, external_approval, live_plans, mark_category_pass,
    resolved_provider,
)


def assess(stage):
    return ReleaseReviewHarness().assess(current_baseline_review(stage))


def test_current_internal_research_is_conditional_not_organizationally_approved():
    decision = assess("INTERNAL_RESEARCH")
    assert decision.state == ReleaseReviewState.CONDITIONAL_REVIEW_REQUIRED
    assert decision.blockers == ()
    assert decision.conditions == ("external governance approval required for stage transition",)


def test_current_silent_evaluation_is_blocked_by_exact_evidence_and_governance_gaps():
    decision = assess("SILENT_EVALUATION")
    assert decision.state == ReleaseReviewState.RELEASE_BLOCKED
    assert set(decision.incomplete_evidence) == {
        "required evidence not PASS: INDEPENDENT_DATASET_EVALUATION",
        "required evidence not PASS: PROVIDER_BACKED_VALIDATION",
        "required evidence not PASS: SILENT_EVALUATION_PROTOCOL",
    }
    assert "provider/model readiness unresolved or provider unavailable" in decision.blockers
    assert "privacy readiness unresolved: NOT_ASSESSED" in decision.blockers
    assert "security readiness unresolved: NOT_ASSESSED" in decision.blockers
    assert "monitoring plan missing or incomplete" in decision.blockers
    assert "rollback plan missing or incomplete" in decision.blockers
    assert "incident response plan missing or incomplete" in decision.blockers
    assert "release candidate version is not frozen" in decision.blockers
    assert decision.governance_status == "PENDING"


def test_current_production_clinical_use_is_blocked_and_never_auto_approved():
    decision = assess("PRODUCTION_CLINICAL_USE")
    assert decision.state == ReleaseReviewState.RELEASE_BLOCKED
    assert decision.governance_status == "PENDING"
    assert any("INTERVENTIONAL_EVALUATION_ACTUAL" in item for item in decision.blockers)
    assert decision.state.value != "PRODUCTION READY"


def test_offline_stage_can_only_be_ready_after_provider_and_external_governance():
    review = current_baseline_review("OFFLINE_DATASET_EVALUATION")
    resolved_provider(review)
    external_approval(review)
    decision = ReleaseReviewHarness().assess(review)
    assert decision.state == ReleaseReviewState.READY_FOR_NEXT_GOVERNED_STAGE
    assert decision.governance_status == "APPROVED"


def test_live_stage_stays_blocked_without_monitoring_rollback_and_incident_response():
    review = current_baseline_review("SILENT_EVALUATION")
    resolved_provider(review)
    review["security"].update(status="RESOLVED", reference="SYNTHETIC-SECURITY")
    review["privacy"].update(status="RESOLVED", reference="SYNTHETIC-PRIVACY")
    for category in ("PROVIDER_BACKED_VALIDATION", "INDEPENDENT_DATASET_EVALUATION", "SILENT_EVALUATION_PROTOCOL"):
        mark_category_pass(review, category)
    external_approval(review)
    decision = ReleaseReviewHarness().assess(review)
    assert decision.state == ReleaseReviewState.RELEASE_BLOCKED
    assert "monitoring plan missing or incomplete" in decision.blockers


def test_pending_governance_prevents_auto_transition_even_when_all_other_requirements_pass():
    review = current_baseline_review("SILENT_EVALUATION")
    resolved_provider(review)
    review["security"].update(status="RESOLVED", reference="SYNTHETIC-SECURITY")
    review["privacy"].update(status="RESOLVED", reference="SYNTHETIC-PRIVACY")
    for category in ("PROVIDER_BACKED_VALIDATION", "INDEPENDENT_DATASET_EVALUATION", "SILENT_EVALUATION_PROTOCOL"):
        mark_category_pass(review, category)
    live_plans(review)
    decision = ReleaseReviewHarness().assess(review)
    assert decision.state == ReleaseReviewState.CONDITIONAL_REVIEW_REQUIRED
    assert decision.conditions == ("external governance approval required for stage transition",)


def test_critical_security_status_blocks_even_with_governance_approval():
    review = current_baseline_review("SILENT_EVALUATION")
    resolved_provider(review)
    review["security"].update(status="BLOCKING_ISSUE", reference="SYNTHETIC-SECURITY-BLOCK")
    review["privacy"].update(status="RESOLVED", reference="SYNTHETIC-PRIVACY")
    for category in ("PROVIDER_BACKED_VALIDATION", "INDEPENDENT_DATASET_EVALUATION", "SILENT_EVALUATION_PROTOCOL"):
        mark_category_pass(review, category)
    live_plans(review)
    external_approval(review)
    decision = ReleaseReviewHarness().assess(review)
    assert decision.state == ReleaseReviewState.RELEASE_BLOCKED
    assert "security readiness unresolved: BLOCKING_ISSUE" in decision.blockers


def test_governance_approval_scope_must_match_target_stage():
    review = current_baseline_review("INTERNAL_RESEARCH")
    external_approval(review)
    review["governance_approval"]["scope"] = "PRODUCTION_CLINICAL_USE"
    decision = ReleaseReviewHarness().assess(review)
    assert decision.state == ReleaseReviewState.RELEASE_BLOCKED
    assert "scope does not match" in decision.blockers[0]


def test_unresolved_critical_risk_blocks_transition():
    review = current_baseline_review("INTERNAL_RESEARCH")
    review["risk_register"][0]["residual_risk"] = "CRITICAL"
    external_approval(review)
    decision = ReleaseReviewHarness().assess(review)
    assert decision.state == ReleaseReviewState.RELEASE_BLOCKED
    assert any("unresolved CRITICAL risk" in item for item in decision.blockers)
