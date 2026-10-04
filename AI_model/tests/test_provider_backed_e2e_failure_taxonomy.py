"""Failure taxonomy, result schema, and reporting checks."""

import pytest

from real_validation.provider_backed_reporting import summarize_results
from real_validation.provider_backed_result import (
    FAILURE_CLASSES,
    build_result,
    validate_result_schema,
)
from real_validation.provider_backed_trial import TrialPolicy


RUNTIME = {"hermes_version": "0.21.4", "hermes_commit": "abc", "python_version": "3.11.15"}
PROVIDER = {"name": "provider", "model": "model", "model_version": None, "request_id": None}


def _result(failure_class="PASS"):
    return build_result(
        case_id="PB01", trial_id="PB01-T01", mode="REAL_GATE",
        runtime=RUNTIME, provider=PROVIDER, started_at="2026-10-03T00:00:00+00:00",
        duration_ms=1, failure_class=failure_class,
    )


def test_failure_taxonomy_is_exact_and_result_schema_is_stable():
    assert FAILURE_CLASSES == {
        "INFRASTRUCTURE_CONFIGURATION", "INFRASTRUCTURE_TRANSIENT",
        "CLINICAL_SEMANTIC_FAILURE", "PASS",
    }
    document = validate_result_schema(_result())
    root = document["provider_backed_result"]
    assert root["report"]["finalized"] is False
    assert root["provider"]["model_version"] is None
    assert root["provider"]["request_id"] is None


def test_invalid_failure_class_fails_closed():
    with pytest.raises(ValueError, match="unsupported failure class"):
        _result("SKIPPED")


def test_skipped_is_reported_separately_and_never_counted_as_pass():
    summary = summarize_results([_result("PASS")], skipped=2)
    assert summary["cases_attempted"] == 1
    assert summary["skipped"] == 2
    assert summary["outcomes"]["PASS"] == 1


def test_retry_policy_only_allows_bounded_transient_failures():
    policy = TrialPolicy(transient_retries=1)
    assert policy.may_retry("INFRASTRUCTURE_TRANSIENT", 1) is True
    assert policy.may_retry("INFRASTRUCTURE_TRANSIENT", 2) is False
    assert policy.may_retry("CLINICAL_SEMANTIC_FAILURE", 1) is False
    assert policy.may_retry("INFRASTRUCTURE_CONFIGURATION", 1) is False
