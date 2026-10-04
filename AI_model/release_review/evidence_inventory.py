"""Evidence inventory with explicit status, maturity, and limitations."""

from __future__ import annotations

from copy import deepcopy


EVIDENCE_MATURITY = {
    "LEVEL_0_NOT_AVAILABLE",
    "LEVEL_1_SYNTHETIC_OR_UNIT",
    "LEVEL_2_INTERNAL_RETROSPECTIVE",
    "LEVEL_3_EXTERNAL_OR_INDEPENDENT_RETROSPECTIVE",
    "LEVEL_4_HUMAN_AI_READER_STUDY",
    "LEVEL_5_SILENT_PROSPECTIVE",
    "LEVEL_6_INTERVENTIONAL_PROSPECTIVE",
}
EVIDENCE_STATUSES = {"NOT_AVAILABLE", "PLANNED", "INCOMPLETE", "PASS", "FAIL", "BLOCKED", "INVALIDATED"}


class EvidenceInventoryError(ValueError):
    pass


def validate_evidence_artifact(artifact):
    if not isinstance(artifact, dict):
        raise EvidenceInventoryError("evidence artifact must be an object")
    required = {
        "evidence_id", "category", "artifact_type", "path_or_reference", "version",
        "system_snapshot", "status", "maturity", "summary", "limitations", "owner",
    }
    missing = sorted(required - set(artifact))
    if missing:
        raise EvidenceInventoryError("evidence artifact missing fields: " + ", ".join(missing))
    if artifact["status"] not in EVIDENCE_STATUSES:
        raise EvidenceInventoryError("invalid evidence status")
    if artifact["maturity"] not in EVIDENCE_MATURITY:
        raise EvidenceInventoryError("invalid evidence maturity")
    if artifact["status"] == "PASS" and artifact["maturity"] == "LEVEL_0_NOT_AVAILABLE":
        raise EvidenceInventoryError("PASS evidence cannot use LEVEL_0_NOT_AVAILABLE")
    if not isinstance(artifact["limitations"], list):
        raise EvidenceInventoryError("evidence limitations must be a list")
    if artifact["status"] == "PASS" and not artifact["path_or_reference"]:
        raise EvidenceInventoryError("PASS evidence requires an artifact reference")
    return artifact


class EvidenceInventory:
    def __init__(self, artifacts=()):
        self._artifacts = {}
        for artifact in artifacts:
            self.add(artifact)

    def add(self, artifact):
        validate_evidence_artifact(artifact)
        evidence_id = artifact["evidence_id"]
        if evidence_id in self._artifacts:
            raise EvidenceInventoryError("duplicate evidence_id")
        self._artifacts[evidence_id] = deepcopy(artifact)

    def artifacts(self):
        return deepcopy(list(self._artifacts.values()))

    def by_category(self, category):
        return [item for item in self.artifacts() if item["category"] == category]

    def passed_categories(self):
        return {item["category"] for item in self._artifacts.values() if item["status"] == "PASS"}
