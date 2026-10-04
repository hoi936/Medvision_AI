"""Reader manifest validation without unnecessary personal identifiers."""

from __future__ import annotations

from .study_schema import validate_reader


def validate_reader_manifest(readers, *, planned_count=None):
    if not isinstance(readers, list) or not readers:
        raise ValueError("reader manifest is missing")
    validated = [validate_reader(reader) for reader in readers]
    ids = [reader["reader_id"] for reader in validated]
    if len(ids) != len(set(ids)):
        raise ValueError("reader IDs must be unique")
    if planned_count is not None and len(validated) != planned_count:
        raise ValueError("reader manifest count differs from pre-specified plan")
    return validated
