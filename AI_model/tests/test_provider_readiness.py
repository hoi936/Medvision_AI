"""Provider-independent checks for secret-safe readiness diagnostics."""

import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

import hermes_real_runtime as runtime

from hermes_real_runtime import (
    PROJECT_ROOT,
    PINNED_HERMES_COMMIT,
    ProviderPreflightError,
    _expected_hermes_executable,
    _pinned_hermes_executable,
    _require_provider,
    _runtime_python,
    _verify_pinned_runtime,
    classify_runtime_failure,
    provider_identity,
    sanitize_infrastructure_detail,
)


def test_provider_identity_is_sanitized_and_contains_no_secret_value_field():
    identity = provider_identity()

    assert set(identity) == {
        "provider",
        "requested_provider",
        "model",
        "provider_configured",
        "provider_registered",
        "credential_present",
        "auth_available",
        "resolution_error_code",
        "resolution_error_type",
    }
    assert "api_key" not in identity
    assert "token" not in identity
    for key in ("provider", "requested_provider", "model"):
        assert re.fullmatch(r"[A-Za-z0-9._:@/+\-?]*", identity[key])


def test_runtime_failure_classification_separates_configuration_and_transient():
    assert classify_runtime_failure("No LLM provider configured") == (
        "INFRASTRUCTURE_CONFIGURATION"
    )
    assert classify_runtime_failure("HTTP 401 unauthorized") == (
        "INFRASTRUCTURE_CONFIGURATION"
    )
    assert classify_runtime_failure("HTTP 429 rate limit") == (
        "INFRASTRUCTURE_TRANSIENT"
    )
    assert classify_runtime_failure("connection timed out") == (
        "INFRASTRUCTURE_TRANSIENT"
    )


def test_diagnostics_redact_secret_shaped_error_values():
    detail = sanitize_infrastructure_detail(
        "provider failed api_key=secret-value bearer=other-secret"
    )
    assert "secret-value" not in detail
    assert "other-secret" not in detail
    assert "<redacted>" in detail
    assert PINNED_HERMES_COMMIT == "2552fb543bd12a326d23449f41a9c13c48eb4e9a"


def test_project_pytest_runner_is_independent_from_pinned_hermes_python():
    project_test_python = Path(sys.executable).resolve()
    hermes_python = _runtime_python().resolve()

    assert project_test_python != hermes_python
    assert hermes_python == (_expected_hermes_executable().parent / "python").resolve()


def test_pinned_runtime_version_commit_home_and_binary_are_verified():
    executable = _verify_pinned_runtime()

    assert executable == _expected_hermes_executable()
    assert runtime.HERMES_HOME == PROJECT_ROOT / ".runtime" / "hermes-home"


def test_missing_project_runtime_fails_closed(monkeypatch):
    monkeypatch.setattr(runtime, "locate_hermes", lambda: None)

    with pytest.raises(ProviderPreflightError) as exc_info:
        _pinned_hermes_executable()

    assert exc_info.value.classification == "INFRASTRUCTURE_CONFIGURATION"
    assert exc_info.value.reason == "isolated pinned Hermes executable is missing"


def test_global_hermes_is_never_accepted_as_fallback(monkeypatch):
    monkeypatch.setattr(runtime, "locate_hermes", lambda: Path("/usr/local/bin/hermes"))

    with pytest.raises(ProviderPreflightError) as exc_info:
        _pinned_hermes_executable()

    assert exc_info.value.classification == "INFRASTRUCTURE_CONFIGURATION"
    assert exc_info.value.reason == (
        "Hermes executable is not the project-isolated pinned runtime"
    )


def test_absent_provider_is_infrastructure_configuration():
    identity = {
        "provider_configured": False,
        "model": "",
        "provider_registered": False,
        "auth_available": False,
    }

    with pytest.raises(ProviderPreflightError) as exc_info:
        _require_provider(identity, {"provider": "", "model": ""})

    assert exc_info.value.classification == "INFRASTRUCTURE_CONFIGURATION"
    assert exc_info.value.reason == (
        "RUN_HERMES_REAL=1 but no usable provider/model is configured"
    )


def test_real_validation_launcher_stops_after_failed_preflight(tmp_path):
    invocation_log = tmp_path / "invocations.log"
    fake_python = tmp_path / "project-test-python"
    fake_python.write_text(
        "#!/bin/sh\n"
        "printf '%s\\n' \"$*\" >> \"$LAUNCH_LOG\"\n"
        "case \"$*\" in\n"
        "  *test_provider_readiness_real.py*) exit 23 ;;\n"
        "  *) exit 0 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)
    env = os.environ.copy()
    env["PROJECT_TEST_PYTHON"] = str(fake_python)
    env["LAUNCH_LOG"] = str(invocation_log)

    completed = subprocess.run(
        ["bash", str(PROJECT_ROOT / "AI_model" / "scripts" / "run_real_validation.sh")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 23
    assert "stage=provider-preflight" in completed.stdout
    assert "stage=all-real-suites" not in completed.stdout
    invocations = invocation_log.read_text(encoding="utf-8").splitlines()
    assert len(invocations) == 1
    assert "test_provider_readiness_real.py" in invocations[0]
    assert "test_behavior_" not in invocations[0]
