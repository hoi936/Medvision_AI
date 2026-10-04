"""De-identified error review records."""

from __future__ import annotations

from .dataset_schema import DIRECT_IDENTIFIER_KEYS


ERROR_CATEGORIES = {
    "input_data_error", "reference_standard_ambiguity", "finding_error",
    "disease_semantic_error", "temporal_error", "arbitration_error", "safety_error",
    "doctor_review_boundary_error", "report_rendering_error", "provider_formatting_error",
}


def _contains_direct_identifier(value):
    if isinstance(value, dict):
        return any(
            str(key).lower() in DIRECT_IDENTIFIER_KEYS or _contains_direct_identifier(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_direct_identifier(child) for child in value)
    return False


def build_error_case(*, case_id, category, expected, observed, evidence_refs, system_version):
    if category not in ERROR_CATEGORIES:
        raise ValueError(f"unsupported error category: {category}")
    payload = {
        "case_id": case_id,
        "category": category,
        "expected": expected,
        "observed": observed,
        "evidence_refs": list(evidence_refs),
        "system_version": system_version,
    }
    if _contains_direct_identifier(payload):
        raise ValueError("direct identifiers are forbidden in error review records")
    return payload
