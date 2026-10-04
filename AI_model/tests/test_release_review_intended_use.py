import pytest

from release_review.intended_use import IntendedUseError, validate_intended_use
from release_review_fixtures import INTENDED_USE, current_baseline_review


def test_intended_use_locks_users_workflow_doctor_control_and_prohibited_use():
    intended = validate_intended_use(dict(INTENDED_USE))
    assert intended["intended_users"]
    assert "doctor" in intended["doctor_control_statement"].lower()
    assert any("autonomous" in item for item in intended["prohibited_uses"])


def test_missing_intended_use_blocks_readiness_as_incomplete():
    review = current_baseline_review()
    review["intended_use"].pop("setting")
    decision = __import__("release_review").ReleaseReviewHarness().assess(review)
    assert decision.state.value == "RELEASE_REVIEW_INCOMPLETE"
    assert "INTENDED_USE_NOT_LOCKED" in decision.blockers[0]


def test_implicit_doctor_control_is_rejected():
    intended = dict(INTENDED_USE)
    intended["doctor_control_statement"] = "human oversight"
    with pytest.raises(IntendedUseError, match="doctor control"):
        validate_intended_use(intended)
