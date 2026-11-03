"""Claim-evidence safety-case linkage without inferring clinical validity."""

from __future__ import annotations


CLAIM_STATUSES = {"INCOMPLETE", "SUPPORTED_WITH_LIMITATIONS", "NOT_SUPPORTED"}
MATURITY_ORDER = {
    "LEVEL_0_NOT_AVAILABLE": 0,
    "LEVEL_1_SYNTHETIC_OR_UNIT": 1,
    "LEVEL_2_INTERNAL_RETROSPECTIVE": 2,
    "LEVEL_3_EXTERNAL_OR_INDEPENDENT_RETROSPECTIVE": 3,
    "LEVEL_4_HUMAN_AI_READER_STUDY": 4,
    "LEVEL_5_SILENT_PROSPECTIVE": 5,
    "LEVEL_6_INTERVENTIONAL_PROSPECTIVE": 6,
}


class SafetyCaseError(ValueError):
    pass


def evaluate_claim(claim, evidence_by_id):
    required = {
        "claim_id", "statement", "evidence_ids", "assumptions", "limitations",
        "residual_risks", "owner", "required_maturity",
    }
    if not isinstance(claim, dict) or not required <= set(claim):
        raise SafetyCaseError("safety claim is incomplete")
    if not claim["evidence_ids"]:
        status = "INCOMPLETE"
        missing = []
    else:
        missing = [item for item in claim["evidence_ids"] if item not in evidence_by_id]
        linked = [evidence_by_id[item] for item in claim["evidence_ids"] if item in evidence_by_id]
        if missing or any(item["status"] in {"NOT_AVAILABLE", "PLANNED", "INCOMPLETE", "BLOCKED", "INVALIDATED"} for item in linked):
            status = "INCOMPLETE"
        elif any(item["status"] == "FAIL" for item in linked):
            status = "NOT_SUPPORTED"
        else:
            required_level = MATURITY_ORDER.get(claim["required_maturity"])
            if required_level is None:
                raise SafetyCaseError("unknown required maturity")
            maturity_ok = all(MATURITY_ORDER[item["maturity"]] >= required_level for item in linked)
            status = "SUPPORTED_WITH_LIMITATIONS" if maturity_ok else "INCOMPLETE"
    return {
        **claim,
        "status": status,
        "missing_evidence_ids": missing,
    }
