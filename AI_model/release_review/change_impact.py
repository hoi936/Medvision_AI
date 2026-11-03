"""Deterministic release-candidate change classification."""

from __future__ import annotations


CHANGE_IMPACT = {
    "NON_CLINICAL_LOW_IMPACT": {"evidence_families": {"schema_unit"}, "retests": {"schema_unit"}},
    "CLINICAL_SEMANTIC_IMPACT": {
        "evidence_families": {"clinical_module", "e2e", "provider_backed", "dataset", "reader", "silent"},
        "retests": {"clinical_modules", "e2e", "provider_backed", "dataset_evaluation", "reader_study", "silent_evaluation"},
    },
    "MODEL_PROVIDER_IMPACT": {
        "evidence_families": {"provider_backed", "dataset_model", "reader_assistance", "silent"},
        "retests": {"provider_preflight", "provider_backed", "dataset_model", "reader_assistance", "silent_evaluation"},
    },
    "DATA_PIPELINE_IMPACT": {
        "evidence_families": {"ingestion", "temporal", "dataset", "silent"},
        "retests": {"ingestion", "temporal_reasoning", "dataset_evaluation", "silent_evaluation"},
    },
    "UI_HUMAN_FACTORS_IMPACT": {
        "evidence_families": {"human_factors", "reader", "warning_visibility", "provenance_comprehension"},
        "retests": {"reader_study", "human_factors", "warning_visibility"},
    },
    "SECURITY_IMPACT": {
        "evidence_families": {"security", "privacy", "provider_operations"},
        "retests": {"security_review", "privacy_review", "incident_response"},
    },
    "WORKFLOW_IMPACT": {
        "evidence_families": {"reader", "silent", "interventional", "human_factors"},
        "retests": {"reader_study", "silent_evaluation", "interventional_protocol", "human_factors"},
    },
}


def classify_change(impact_class):
    if impact_class not in CHANGE_IMPACT:
        raise ValueError("unsupported change impact class")
    return {
        "impact_class": impact_class,
        "evidence_families": sorted(CHANGE_IMPACT[impact_class]["evidence_families"]),
        "required_retests": sorted(CHANGE_IMPACT[impact_class]["retests"]),
    }
