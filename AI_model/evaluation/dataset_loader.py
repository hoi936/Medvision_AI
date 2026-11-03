"""Explicit-only dataset loading; no implicit golden or internet fallback."""

from __future__ import annotations

import json
from pathlib import Path

from .dataset_schema import validate_case, validate_manifest


class IndependentDatasetRequiredError(FileNotFoundError):
    pass


def _reject_internal_test_path(path):
    lowered = "/".join(part.lower() for part in path.parts)
    if "golden_cases" in lowered or "/tests/fixtures" in lowered:
        raise IndependentDatasetRequiredError(
            "golden/test fixtures cannot be used as an independent evaluation dataset"
        )


def load_dataset(manifest_path):
    if manifest_path is None:
        raise IndependentDatasetRequiredError("independent evaluation dataset not configured")
    path = Path(manifest_path).expanduser().resolve()
    if not path.is_file():
        raise IndependentDatasetRequiredError("independent evaluation dataset not configured")
    _reject_internal_test_path(path)
    manifest = validate_manifest(json.loads(path.read_text(encoding="utf-8")))
    raw_cases = manifest.get("cases")
    if raw_cases is None:
        cases_path_value = manifest.get("cases_file")
        if not cases_path_value:
            raise IndependentDatasetRequiredError("dataset manifest does not specify cases or cases_file")
        cases_path = (path.parent / cases_path_value).resolve()
        _reject_internal_test_path(cases_path)
        raw_cases = json.loads(cases_path.read_text(encoding="utf-8"))
    if not isinstance(raw_cases, list):
        raise IndependentDatasetRequiredError("dataset cases must be a list")
    return manifest, [validate_case(case) for case in raw_cases]
