from release_review.safety_case import evaluate_claim
from release_review_fixtures import SAFETY_CLAIMS, current_baseline_review


def test_unit_level_safety_claim_is_supported_only_with_declared_limitations():
    review = current_baseline_review()
    evidence = {item["evidence_id"]: item for item in review["evidence_inventory"]}
    result = evaluate_claim(SAFETY_CLAIMS[0], evidence)
    assert result["status"] == "SUPPORTED_WITH_LIMITATIONS"
    assert result["limitations"]


def test_not_run_evidence_keeps_claim_incomplete():
    claim = dict(SAFETY_CLAIMS[0])
    claim["claim_id"] = "CLAIM-REAL-PROVIDER"
    claim["evidence_ids"] = ["EV-PROVIDER"]
    claim["required_maturity"] = "LEVEL_3_EXTERNAL_OR_INDEPENDENT_RETROSPECTIVE"
    evidence = {item["evidence_id"]: item for item in current_baseline_review()["evidence_inventory"]}
    assert evaluate_claim(claim, evidence)["status"] == "INCOMPLETE"


def test_missing_evidence_is_reported_not_assumed():
    claim = dict(SAFETY_CLAIMS[0])
    claim["evidence_ids"] = ["EV-DOES-NOT-EXIST"]
    result = evaluate_claim(claim, {})
    assert result["status"] == "INCOMPLETE"
    assert result["missing_evidence_ids"] == ["EV-DOES-NOT-EXIST"]
