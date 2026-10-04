"""Synthetic code-test fixtures; never an independent evaluation dataset."""

from __future__ import annotations

from copy import deepcopy
import json


def reference(task="finding", label="POSITIVE"):
    return {
        "task": task,
        "source_type": "synthetic_unit_reference",
        "source_ids": ["SYNTHETIC-REF-1"],
        "reviewer_count": 2,
        "adjudicated": True,
        "confidence": "TEST_ONLY",
        "limitations": ["synthetic fixture; not clinical evidence"],
        "label": label,
    }


def evaluation_case(
    case_id="DS001",
    patient_group_id="PAT-GROUP-001",
    study_id="STUDY-001",
    split="evaluation",
    references=None,
    content_hash=None,
):
    study = {"study_id": study_id, "modality": "CXR", "timepoint": "T0"}
    if content_hash:
        study["content_hash"] = content_hash
    return {
        "case_id": case_id,
        "patient_group_id": patient_group_id,
        "split": split,
        "studies": [study],
        "imaging": {"cxr": [study_id], "ct": [], "other": []},
        "clinical": {"symptoms": [], "signs": [], "history": []},
        "labs": [],
        "physiology": [],
        "microbiology": [],
        "pathology": [],
        "longitudinal": {"timepoints": ["T0"]},
        "reference_standards": deepcopy(references if references is not None else [reference()]),
        "adjudication": {
            "reviewers": ["REVIEWER-1", "REVIEWER-2"],
            "method": "synthetic_consensus",
            "disagreement": False,
            "final_reference": "SYNTHETIC-REF-1",
        },
        "metadata": {
            "site": "SYNTHETIC-SITE",
            "time_period": "TEST",
            "subgroup_labels": [],
            "origin": "synthetic_unit_fixture",
        },
        "missingness": {
            "laboratory": "MISSING",
            "microbiology": "UNKNOWN",
            "pathology": "EXPLICIT_NEGATIVE",
            "imaging": "POSITIVE",
        },
    }


def manifest(cases, *, tasks=("finding",)):
    splits = {}
    for case in cases:
        splits.setdefault(case["split"], []).append(case["case_id"])
    return {
        "dataset_id": "SYNTHETIC-CODE-TEST-ONLY",
        "dataset_version": "test-v1",
        "source": "unit-test fixture",
        "institution": "none",
        "date_range": "not applicable",
        "deidentified": True,
        "counts": {
            "patients": len({case["patient_group_id"] for case in cases}),
            "studies": sum(len(case["studies"]) for case in cases),
            "cxr": sum(len(case["imaging"]["cxr"]) for case in cases),
            "ct": 0,
            "longitudinal_cases": sum(len(case["longitudinal"]["timepoints"]) > 1 for case in cases),
        },
        "splits": splits,
        "metric_specification": {task: ["exact_state_agreement"] for task in tasks},
        "cases": deepcopy(cases),
    }


def write_dataset(tmp_path, cases, *, tasks=("finding",), filename="dataset.json"):
    path = tmp_path / filename
    path.write_text(json.dumps(manifest(cases, tasks=tasks), indent=2) + "\n", encoding="utf-8")
    return path
