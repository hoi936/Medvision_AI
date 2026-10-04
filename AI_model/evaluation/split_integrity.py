"""Patient-level split and duplicate integrity checks."""

from __future__ import annotations

from collections import defaultdict


PROTECTED_SPLITS = {"development", "validation", "evaluation", "test", "external"}
INTERNAL_CASE_PREFIXES = ("E2E", "PB")


class SplitIntegrityError(ValueError):
    def __init__(self, violations):
        self.violations = list(violations)
        super().__init__("; ".join(item["code"] for item in self.violations))


def inspect_split_integrity(manifest, cases):
    violations = []
    case_ids = defaultdict(list)
    patients = defaultdict(set)
    studies = defaultdict(set)
    hashes = defaultdict(set)
    for case in cases:
        split = case["split"]
        case_ids[case["case_id"]].append(split)
        patients[case["patient_group_id"]].add(split)
        for study in case["studies"]:
            studies[study["study_id"]].add(split)
            for key in ("content_hash", "image_hash", "report_hash"):
                if study.get(key):
                    hashes[f"{key}:{study[key]}"].add(split)
        for key in ("content_hash", "image_hash", "report_hash"):
            if case.get(key):
                hashes[f"{key}:{case[key]}"].add(split)
        origin = str(case.get("metadata", {}).get("origin", "")).lower()
        if case["case_id"].startswith(INTERNAL_CASE_PREFIXES) or origin in {
            "golden_case", "e2e_fixture", "provider_backed_fixture",
        }:
            violations.append({"code": "GOLDEN_CASE_REUSE", "case_id": case["case_id"]})
    for case_id, splits in case_ids.items():
        if len(splits) > 1:
            violations.append({"code": "DUPLICATE_CASE", "case_id": case_id, "splits": sorted(splits)})
    for patient_id, splits in patients.items():
        if len(splits) > 1:
            violations.append({"code": "PATIENT_OVERLAP", "patient_group_id": patient_id, "splits": sorted(splits)})
            violations.append({"code": "LONGITUDINAL_PATIENT_LEAKAGE", "patient_group_id": patient_id, "splits": sorted(splits)})
    for study_id, splits in studies.items():
        if len(splits) > 1:
            violations.append({"code": "STUDY_OVERLAP", "study_id": study_id, "splits": sorted(splits)})
    for digest, splits in hashes.items():
        protected = sorted(set(splits) & PROTECTED_SPLITS)
        if len(protected) > 1:
            violations.append({"code": "PROTECTED_SPLIT_HASH_DUPLICATE", "hash_ref": digest, "splits": protected})

    declared = {
        case_id: split for split, ids in manifest.get("splits", {}).items() for case_id in ids
    }
    for case in cases:
        if declared.get(case["case_id"]) != case["split"]:
            violations.append({
                "code": "SPLIT_DECLARATION_MISMATCH",
                "case_id": case["case_id"],
                "declared": declared.get(case["case_id"]),
                "observed": case["split"],
            })
    return {"valid": not violations, "violations": violations}


def validate_split_integrity(manifest, cases):
    result = inspect_split_integrity(manifest, cases)
    if not result["valid"]:
        raise SplitIntegrityError(result["violations"])
    return result
