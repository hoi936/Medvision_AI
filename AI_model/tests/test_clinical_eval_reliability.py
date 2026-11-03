import json
from pathlib import Path

from clinical_evaluation.distribution_shift import missingness_distribution, positive_finding_frequency, stratify_metadata
from clinical_evaluation.reliability_metrics import reliability_metrics
from clinical_evaluation.semantic_monitoring import evaluate_silent_trace
from e2e.e2e_clinical_validation import run_e2e_case


def test_reliability_metrics_remain_separate_and_deterministic():
    records = [
        {
            "ingestion_success": True, "normalization_success": True,
            "invocation_success": True, "parse_success": True, "trace_complete": True,
            "provider_transient_failure": False, "provider_configuration_failure": False,
            "final_candidate_generated": True, "end_to_end_available": True, "latency_ms": 100,
        },
        {
            "ingestion_success": True, "normalization_success": False,
            "invocation_success": False, "parse_success": False, "trace_complete": False,
            "provider_transient_failure": True, "provider_configuration_failure": False,
            "final_candidate_generated": False, "end_to_end_available": False, "latency_ms": 300,
        },
    ]
    metrics = reliability_metrics(records)
    assert metrics["ingestion_success"]["estimate"] == 1.0
    assert metrics["normalization_success"]["estimate"] == 0.5
    assert metrics["provider_transient_failure"]["estimate"] == 0.5
    assert metrics["latency_ms"]["p50"] == 200
    assert "overall_score" not in metrics and "composite" not in metrics


def test_distribution_monitoring_is_descriptive_without_adaptation_output():
    records = [
        {"site": "A", "modality": "CXR", "projection": "PA", "time_period": "T1", "protocol": "P1", "positive_findings": ["Atelectasis"]},
        {"site": "B", "modality": "CXR", "projection": None, "time_period": "T1", "protocol": "P1", "positive_findings": []},
    ]
    result = {
        "strata": stratify_metadata(records),
        "missingness": missingness_distribution(records, ["projection"]),
        "findings": positive_finding_frequency(records),
    }
    assert result["missingness"]["projection"]["missing"] == 1
    assert result["findings"]["Atelectasis"]["case_fraction"] == 0.5
    assert "adapt" not in json.dumps(result).lower()


def test_silent_semantic_monitor_reuses_all_sixteen_frozen_invariants():
    cases = json.loads((Path(__file__).parent / "golden_cases/e2e_clinical_validation/cases.json").read_text())
    trace, _ = run_e2e_case(cases[0])
    result = evaluate_silent_trace(trace)
    assert len(result["invariant_results"]) == 16
    assert result["semantic_safety_incident_required"] is False


def test_semantic_invariant_failure_requires_incident():
    cases = json.loads((Path(__file__).parent / "golden_cases/e2e_clinical_validation/cases.json").read_text())
    trace, _ = run_e2e_case(cases[0])
    trace["violations"]["autonomous_action"] = True
    result = evaluate_silent_trace(trace)
    assert "NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE" in result["failed"]
    assert result["semantic_safety_incident_required"] is True
