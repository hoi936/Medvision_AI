from release_review.change_impact import classify_change
from release_review.evidence_invalidation import invalidate_evidence
from release_review_fixtures import current_baseline_review


def test_provider_change_invalidates_provider_dependent_evidence_not_schema_unit():
    evidence = current_baseline_review()["evidence_inventory"]
    result = invalidate_evidence(evidence, "MODEL_PROVIDER_IMPACT")
    assert "EV-PROVIDER" in result["invalidated_evidence_ids"]
    by_id = {item["evidence_id"]: item for item in result["artifacts"]}
    assert by_id["EV-PROVIDER"]["status"] == "INVALIDATED"
    assert by_id["EV-REGRESSION"]["status"] == "PASS"


def test_clinical_skill_change_invalidates_downstream_semantic_families():
    impact = classify_change("CLINICAL_SEMANTIC_IMPACT")
    assert {"clinical_modules", "e2e", "provider_backed", "dataset_evaluation", "reader_study", "silent_evaluation"} <= set(impact["required_retests"])


def test_ui_change_targets_human_factors_without_invalidating_disease_semantics():
    impact = classify_change("UI_HUMAN_FACTORS_IMPACT")
    assert "human_factors" in impact["evidence_families"]
    assert "clinical_module" not in impact["evidence_families"]


def test_ingestion_change_invalidates_temporal_and_silent_evidence_families():
    impact = classify_change("DATA_PIPELINE_IMPACT")
    assert {"ingestion", "temporal", "silent"} <= set(impact["evidence_families"])
