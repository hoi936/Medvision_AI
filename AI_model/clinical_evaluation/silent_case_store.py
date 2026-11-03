"""In-memory study-only case store with no EHR write or clinical finalization API."""

from __future__ import annotations

from copy import deepcopy

from .silent_isolation import validate_silent_isolation


class SilentCaseStore:
    def __init__(self, isolation):
        validate_silent_isolation(isolation)
        self._cases = {}

    def add(self, case):
        required = {
            "silent_case_id", "source_case_id", "deployment_version", "ingested_at",
            "clinical_event_times", "hermes_run_id", "hermes_output_hash",
            "invariant_result", "reference_status", "outcome_linkage", "finalized",
        }
        if not isinstance(case, dict) or not required <= set(case):
            raise ValueError("silent case is incomplete")
        if case["finalized"] is not False:
            raise ValueError("silent case cannot be clinically finalized")
        case_id = case["silent_case_id"]
        if case_id in self._cases:
            raise ValueError("silent case IDs are immutable and unique")
        self._cases[case_id] = deepcopy(case)

    def get_for_offline_evaluation(self, case_id):
        return deepcopy(self._cases[case_id])

    def __len__(self):
        return len(self._cases)
