"""Provider-independent execution tests for the REAL_GATE runner."""

import json
from pathlib import Path

import pytest

from hermes_real_runtime import PINNED_HERMES_COMMIT, ProviderPreflightError
from hermes_report import HermesReportError
import real_validation.provider_backed_e2e_runner as runner_module
from real_validation.provider_backed_e2e_runner import ProviderBackedE2ERunner
from real_validation.provider_backed_trial import TrialPolicy


PREFLIGHT = {
    "hermes_version": "0.21.4",
    "hermes_commit": PINNED_HERMES_COMMIT,
    "python": "3.11.15",
    "provider": "sanitized-provider",
    "model": "sanitized-model",
    "minimal_inference": "PASS",
}
SAFE_REPORT = """## 2. Findings từ mô hình ảnh
Pneumothorax evidence retained.
## 4. Tích hợp bằng chứng
NO_FINDING_CONTRADICTION is preserved.
## 5. Chẩn đoán phân biệt
No disease ranking is produced.
## 8. Safety flags
Doctor review remains required.
## 9. Giới hạn
review_status: PENDING_CLINICIAN_REVIEW
requires_doctor_review: true
"""


def _runner(inference, *, preflight=lambda: PREFLIGHT, enabled=lambda: True, retries=1):
    return ProviderBackedE2ERunner(
        preflight_fn=preflight,
        inference_fn=inference,
        run_enabled_fn=enabled,
        policy=TrialPolicy(transient_retries=retries),
    )


def test_preflight_configuration_block_prevents_model_call(tmp_path):
    calls = []

    def blocked():
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "RUN_HERMES_REAL=1 but no usable provider/model is configured",
        )

    result = _runner(lambda *_: calls.append(True), preflight=blocked).run_case("PB01", artifact_dir=tmp_path)
    root = result["provider_backed_result"]
    assert root["failure"]["class"] == "INFRASTRUCTURE_CONFIGURATION"
    assert root["failure"]["message"] == "RUN_HERMES_REAL=1 but no usable provider/model is configured"
    assert root["execution"]["attempts"] == []
    assert calls == []


def test_run_flag_is_checked_before_provider_preflight_or_inference(tmp_path):
    calls = []
    result = _runner(
        lambda *_: calls.append("inference"),
        preflight=lambda: calls.append("preflight"),
        enabled=lambda: False,
    ).run_case("PB01", artifact_dir=tmp_path)
    assert result["provider_backed_result"]["failure"]["class"] == "INFRASTRUCTURE_CONFIGURATION"
    assert calls == []


def test_real_gate_runs_one_trial_then_applies_doctor_fixture_and_persists_trace(tmp_path):
    calls = []

    def inference(*_):
        calls.append("real_reasoning")
        return SAFE_REPORT

    result = _runner(inference).run_case("PB01", artifact_dir=tmp_path)
    root = result["provider_backed_result"]
    trace = json.loads(Path(root["normalized_trace_ref"]).read_text(encoding="utf-8"))
    assert calls == ["real_reasoning"]
    assert root["failure"]["class"] == "PASS"
    assert len(root["invariants"]["passed"]) == 16
    assert root["invariants"]["failed"] == []
    assert trace["provider_backed"]["execution_boundary"] == [
        "real_reasoning", "doctor_review_fixture", "final_report_validator",
    ]
    assert trace["doctor_review"]["fixture_id"] == "FIXTURE-REVIEW-E2E04"
    assert root["report"]["finalized"] is False
    assert Path(root["raw_output_ref"]).read_text(encoding="utf-8") == SAFE_REPORT
    assert Path(root["normalized_trace_ref"]).with_name("result.json").is_file()


def test_semantic_failure_is_not_retried(tmp_path):
    calls = []

    def inference(*_):
        calls.append(1)
        return SAFE_REPORT + "The score means 91% probability of disease.\n"

    result = _runner(inference).run_case("PB01", artifact_dir=tmp_path)
    root = result["provider_backed_result"]
    assert len(calls) == 1
    assert len(root["execution"]["attempts"]) == 1
    assert root["failure"]["class"] == "CLINICAL_SEMANTIC_FAILURE"
    assert root["failure"]["first_invariant"] == "NO_SCORE_TO_DISEASE_PROBABILITY"


def test_safety_contract_failure_is_semantic_and_not_retried(tmp_path):
    calls = []

    def inference(*_):
        calls.append(1)
        raise HermesReportError("Hermes trả về báo cáo không đúng contract an toàn; thiếu: review marker")

    result = _runner(inference).run_case("PB01", artifact_dir=tmp_path)
    root = result["provider_backed_result"]
    assert calls == [1]
    assert root["failure"]["class"] == "CLINICAL_SEMANTIC_FAILURE"
    assert root["failure"]["first_invariant"] == "PROVENANCE_PRESERVED"
    assert len(root["execution"]["attempts"]) == 1


def test_omitted_frozen_case_state_is_a_provenance_failure(tmp_path):
    report = SAFE_REPORT.replace("NO_FINDING_CONTRADICTION is preserved.\n", "")
    result = _runner(lambda *_: report).run_case("PB01", artifact_dir=tmp_path)
    root = result["provider_backed_result"]
    trace = json.loads(Path(root["normalized_trace_ref"]).read_text(encoding="utf-8"))
    assert root["failure"]["class"] == "CLINICAL_SEMANTIC_FAILURE"
    assert root["failure"]["first_invariant"] == "PROVENANCE_PRESERVED"
    assert trace["provider_backed"]["missing_source_markers"] == ["NO_FINDING_CONTRADICTION"]


def test_unexpected_canonical_confirmation_uses_frozen_diagnosis_invariant(tmp_path):
    report = SAFE_REPORT + "PATHOLOGY_CONFIRMED_MALIGNANCY\n"
    result = _runner(lambda *_: report).run_case("PB01", artifact_dir=tmp_path)
    root = result["provider_backed_result"]
    assert root["failure"]["class"] == "CLINICAL_SEMANTIC_FAILURE"
    assert "NO_UNSUPPORTED_DIAGNOSIS" in root["invariants"]["failed"]


def test_transient_failure_has_one_bounded_retry_and_logs_every_attempt(tmp_path):
    calls = []

    def inference(*_):
        calls.append(1)
        if len(calls) == 1:
            raise TimeoutError("temporary provider timeout")
        return SAFE_REPORT

    result = _runner(inference).run_case("PB01", artifact_dir=tmp_path)
    attempts = result["provider_backed_result"]["execution"]["attempts"]
    assert len(calls) == 2
    assert [item["outcome"] for item in attempts] == ["failed", "completed"]
    assert attempts[0]["failure_class"] == "INFRASTRUCTURE_TRANSIENT"
    assert result["provider_backed_result"]["failure"]["class"] == "PASS"


def test_transient_retry_limit_fails_without_cherry_picking(tmp_path):
    calls = []

    def inference(*_):
        calls.append(1)
        raise ConnectionError("network temporarily unavailable")

    result = _runner(inference).run_case("PB01", artifact_dir=tmp_path)
    root = result["provider_backed_result"]
    assert len(calls) == 2
    assert len(root["execution"]["attempts"]) == 2
    assert root["failure"]["class"] == "INFRASTRUCTURE_TRANSIENT"


def test_existing_invariant_engine_is_called_after_real_reasoning(monkeypatch, tmp_path):
    original = runner_module.evaluate_invariants
    calls = []

    def wrapped(trace):
        calls.append(trace["provider_backed"]["execution_boundary"][0])
        return original(trace)

    monkeypatch.setattr(runner_module, "evaluate_invariants", wrapped)
    result = _runner(lambda *_: SAFE_REPORT).run_case("PB01", artifact_dir=tmp_path)
    assert calls == ["real_reasoning"]
    assert result["provider_backed_result"]["failure"]["class"] == "PASS"
