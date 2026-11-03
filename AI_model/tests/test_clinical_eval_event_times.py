import pytest

from clinical_evaluation.silent_ingestion import SilentIngestionError, normalize_silent_payload
from clinical_eval_fixtures import DATA_SOURCE_CONTRACT, SYNTHETIC_PAYLOAD, clone


def test_every_event_time_is_preserved_and_temporal_reasoning_uses_acquisition_time():
    payload = clone(SYNTHETIC_PAYLOAD)
    normalized = normalize_silent_payload(clone(DATA_SOURCE_CONTRACT), payload)["normalized"]
    for field in (
        "acquisition_time", "sample_time", "result_time", "report_final_time",
        "ingestion_time", "hermes_run_time",
    ):
        assert normalized[field] == payload[field]
    assert normalized["temporal_reasoning_time"] == payload["acquisition_time"]
    assert normalized["temporal_reasoning_time"] != payload["ingestion_time"]


def test_ingestion_before_clinical_event_time_fails_closed():
    payload = clone(SYNTHETIC_PAYLOAD)
    payload["ingestion_time"] = "2025-12-31T23:00:00+00:00"
    with pytest.raises(SilentIngestionError, match="precedes"):
        normalize_silent_payload(clone(DATA_SOURCE_CONTRACT), payload)


def test_identical_ingestion_and_clinical_event_time_is_not_substitution():
    payload = clone(SYNTHETIC_PAYLOAD)
    payload["ingestion_time"] = payload["acquisition_time"]
    with pytest.raises(SilentIngestionError, match="must not be substituted"):
        normalize_silent_payload(clone(DATA_SOURCE_CONTRACT), payload)
