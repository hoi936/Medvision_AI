"""Pinned-runtime provider readiness gate for all real clinical suites."""

import os

import pytest

from hermes_real_runtime import ProviderPreflightError, run_provider_preflight


RUN_REAL = os.environ.get("RUN_HERMES_REAL") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_REAL,
    reason="real Hermes tests disabled; set RUN_HERMES_REAL=1 to use the configured provider",
)


def test_provider_preflight_before_clinical_real_suites():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")

    assert metadata["minimal_inference"] == "PASS"
    assert metadata["skill_count"] == 17
    assert metadata["write_approval"] is True
