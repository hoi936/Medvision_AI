"""Deterministic helpers for the provider-independent E2E harness."""

from copy import deepcopy
import hashlib
import json


STAGE_ORDER = [
    "E2E_STAGE_INPUT",
    "E2E_STAGE_ROUTING",
    "E2E_STAGE_EVIDENCE_FUSION",
    "E2E_STAGE_FINDING_SKILLS",
    "E2E_STAGE_SAFETY",
    "E2E_STAGE_DISEASE_ANALYSIS",
    "E2E_STAGE_TEMPORAL_REASONING",
    "E2E_STAGE_ARBITRATION",
    "E2E_STAGE_DRAFT_REPORT",
    "E2E_STAGE_DOCTOR_REVIEW",
    "E2E_STAGE_FINAL_REPORT",
]


def normalized_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def snapshot_hash(value):
    return hashlib.sha256(normalized_json(value).encode("utf-8")).hexdigest()


def stage_snapshot(stage, ordinal, payload, execution_mode, *, source_ids=None, fixture_id=None, active=True):
    normalized = deepcopy(payload)
    item = {
        "stage": stage,
        "ordinal": ordinal,
        "active": active,
        "execution_mode": execution_mode,
        "fixture_id": fixture_id,
        "source_ids": list(source_ids or []),
        "normalized_payload": normalized,
        "sha256": snapshot_hash(normalized),
    }
    if execution_mode == "fixture":
        item["owning_module"] = {
            "E2E_STAGE_EVIDENCE_FUSION": "medvision-evidence-fusion",
            "E2E_STAGE_FINDING_SKILLS": "finding-specific skills",
            "E2E_STAGE_SAFETY": "medvision-safety-check",
            "E2E_STAGE_DISEASE_ANALYSIS": "frozen Disease Analysis v2 fixtures",
            "E2E_STAGE_TEMPORAL_REASONING": "Longitudinal / Temporal Reasoning v1",
            "E2E_STAGE_ARBITRATION": "Cross-Disease Differential Arbitration v1",
            "E2E_STAGE_DRAFT_REPORT": "medvision-disease-analysis draft contract",
        }[stage]
        item["fixed_timestamp"] = "2026-09-29T09:00:00+07:00"
    return item
