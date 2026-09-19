"""Canonical clinical payload and legacy normalization for Hermes."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
NEAR_THRESHOLD_MARGIN = 0.05
ALLOWED_WORKFLOW_MODES = {"WITH_LABS", "MISSING_LABS"}


class ClinicalSchemaError(ValueError):
    """Raised when a case cannot be normalized safely."""


@dataclass(frozen=True)
class NormalizationResult:
    payload: dict[str, Any]
    warnings: tuple[str, ...]


def _has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _lines(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [line.strip(" -\t") for line in str(value or "").splitlines() if line.strip(" -\t")]


def calculate_confidence_band(
    score: float, threshold: float, near_margin: float = NEAR_THRESHOLD_MARGIN
) -> tuple[str, str, float]:
    score = float(score)
    threshold = float(threshold)
    margin = score - threshold
    decision = "POSITIVE" if margin >= 0 else "NEGATIVE"
    if decision == "POSITIVE":
        band = "NEAR_THRESHOLD_POSITIVE" if margin <= near_margin else "CLEAR_POSITIVE"
    else:
        band = "NEAR_THRESHOLD_NEGATIVE" if margin >= -near_margin else "CLEAR_NEGATIVE"
    return decision, band, margin


def normalize_model_findings(
    results: Iterable[dict[str, Any]],
    *,
    model_name: str | None = "DenseNet121",
    model_version: str | None = "baseline-best-epoch-8",
    input_type: str | None = None,
    near_margin: float = NEAR_THRESHOLD_MARGIN,
) -> dict[str, Any]:
    findings = []
    for item in results:
        score = float(item["score"])
        threshold = float(item["threshold"])
        decision, band, margin = calculate_confidence_band(
            score, threshold, near_margin
        )
        findings.append(
            {
                "name": str(item["finding"]),
                "score": score,
                "threshold": threshold,
                "margin": margin,
                "decision": decision,
                "confidence_band": band,
                "bbox": item.get("bbox"),
                "laterality": item.get("laterality"),
                "anatomic_location": item.get("anatomic_location"),
                "gradcam_available": bool(item.get("gradcam_available", False)),
                "source": "IMAGE_MODEL",
                "provided": True,
                "verified": False,
            }
        )
    if not findings:
        raise ClinicalSchemaError("model_findings phải chứa ít nhất một finding.")
    return {
        "provided": True,
        "verified": False,
        "source": "IMAGE_MODEL",
        "model_name": model_name,
        "model_version": model_version,
        "input_type": input_type,
        "score_calibrated_as_probability": False,
        "near_threshold_margin": near_margin,
        "findings": findings,
    }


def _section(
    value: Any,
    *,
    source: str = "USER_PROVIDED",
    provided: bool | None = None,
    verified: bool = False,
    value_key: str = "value",
) -> dict[str, Any]:
    actual = _has_content(value)
    return {
        "provided": actual if provided is None else bool(provided and actual),
        "verified": bool(verified),
        "source": source,
        value_key: value,
    }


def build_case_payload(
    *,
    workflow_mode: str,
    general_info: dict[str, Any] | None,
    symptoms: list[dict[str, Any]],
    history: list[str],
    risk_factors: list[str],
    vitals: dict[str, Any] | None,
    laboratory_results: list[dict[str, Any]],
    missing_tests: list[str],
    clinician_request: str,
    model_results: Iterable[dict[str, Any]],
    input_type: str | None = None,
) -> dict[str, Any]:
    if workflow_mode not in ALLOWED_WORKFLOW_MODES:
        raise ClinicalSchemaError("workflow_mode không hợp lệ.")
    clean_symptoms = [item for item in symptoms if _has_content(item.get("name"))]
    clean_labs = [item for item in laboratory_results if _has_content(item.get("name"))]
    return {
        "schema_version": SCHEMA_VERSION,
        "workflow_mode": workflow_mode,
        "general_info": _section(general_info or {}),
        "symptoms": _section(clean_symptoms, value_key="items"),
        "history": _section(_lines(history), value_key="items"),
        "risk_factors": _section(_lines(risk_factors), value_key="items"),
        "vitals": _section(vitals or {}, source="VITAL_SIGN", value_key="measurements"),
        "laboratory": _section(clean_labs, source="LAB", value_key="results"),
        "missing_tests": _lines(missing_tests),
        "clinician_request": _section(clinician_request),
        "model_findings": normalize_model_findings(
            model_results, input_type=input_type
        ),
    }


def legacy_case_payload(
    *,
    results: Iterable[dict[str, Any]],
    symptoms: str = "",
    history: str = "",
    laboratory: str = "",
    demographics: str = "",
    workflow_mode: str = "MISSING_LABS",
) -> dict[str, Any]:
    """Convert the old four-text-field contract without losing provenance."""
    return {
        "schema_version": "legacy",
        "workflow_mode": workflow_mode,
        "field_presence": {
            "general_info": _has_content(demographics),
            "symptoms": _has_content(symptoms),
            "history": _has_content(history),
            "laboratory": _has_content(laboratory),
        },
        "general_info": demographics,
        "symptoms": symptoms,
        "history": history,
        "laboratory": laboratory,
        "model_findings": normalize_model_findings(results),
    }


def _normalize_existing_section(
    raw: Any,
    *,
    legacy_present: bool,
    value_key: str,
    source: str,
    warnings: list[str],
    section_name: str,
) -> dict[str, Any]:
    if isinstance(raw, dict) and any(
        key in raw for key in ("provided", value_key, "value", "items", "results", "measurements")
    ):
        value = raw.get(value_key)
        if value is None:
            value = raw.get("value", raw.get("items", raw.get("results", raw.get("measurements"))))
        actual = _has_content(value)
        explicit = raw.get("provided")
        provided = actual if explicit is None else bool(explicit and actual)
        if explicit is True and not actual:
            warnings.append(f"{section_name}.provided=true nhưng nội dung rỗng; đã chuẩn hóa false.")
        return {
            "provided": provided,
            "verified": bool(raw.get("verified", False)),
            "source": str(raw.get("source") or source),
            value_key: deepcopy(value) if value is not None else ([] if value_key != "value" else ""),
        }
    actual = _has_content(raw)
    if legacy_present and actual:
        warnings.append(f"Đã chuyển field_presence.{section_name}=true sang provided=true.")
    if value_key in {"items", "results"}:
        if isinstance(raw, list):
            value = deepcopy(raw)
        elif actual:
            label = "name"
            value = [{label: str(raw).strip(), "legacy_unstructured": True}]
        else:
            value = []
    elif value_key == "measurements":
        value = deepcopy(raw) if isinstance(raw, dict) else {}
    else:
        value = deepcopy(raw) if actual else ""
    return _section(
        value,
        source=source,
        provided=legacy_present or actual,
        value_key=value_key,
    )


def normalize_case_payload(payload: dict[str, Any]) -> NormalizationResult:
    """Normalize canonical and legacy requests into the one reasoning schema."""
    if not isinstance(payload, dict):
        raise ClinicalSchemaError("Payload phải là JSON object.")
    warnings: list[str] = []
    presence = payload.get("field_presence") or {}
    mode = str(payload.get("workflow_mode") or "MISSING_LABS")
    if mode not in ALLOWED_WORKFLOW_MODES:
        raise ClinicalSchemaError("workflow_mode không hợp lệ.")

    normalized: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "workflow_mode": mode,
    }
    specs = {
        "general_info": ("value", "USER_PROVIDED"),
        "symptoms": ("items", "USER_PROVIDED"),
        "history": ("items", "USER_PROVIDED"),
        "risk_factors": ("items", "USER_PROVIDED"),
        "vitals": ("measurements", "VITAL_SIGN"),
        "laboratory": ("results", "LAB"),
        "clinician_request": ("value", "USER_PROVIDED"),
    }
    for name, (value_key, source) in specs.items():
        raw = payload.get(name)
        normalized[name] = _normalize_existing_section(
            raw,
            legacy_present=bool(presence.get(name) or (name == "general_info" and presence.get("demographics"))),
            value_key=value_key,
            source=source,
            warnings=warnings,
            section_name=name,
        )

    normalized["missing_tests"] = _lines(payload.get("missing_tests", []))
    model_raw = payload.get("model_findings")
    if isinstance(model_raw, dict) and model_raw.get("findings"):
        normalized["model_findings"] = deepcopy(model_raw)
        normalized["model_findings"].update(
            {
                "provided": True,
                "verified": bool(model_raw.get("verified", False)),
                "source": "IMAGE_MODEL",
                "score_calibrated_as_probability": False,
            }
        )
        rebuilt = []
        for item in model_raw["findings"]:
            decision, band, margin = calculate_confidence_band(item["score"], item["threshold"])
            clean = deepcopy(item)
            clean.update(
                {
                    "margin": margin,
                    "decision": decision,
                    "confidence_band": band,
                    "source": "IMAGE_MODEL",
                    "provided": True,
                    "verified": bool(item.get("verified", False)),
                }
            )
            clean.setdefault("bbox", None)
            clean.setdefault("laterality", None)
            clean.setdefault("anatomic_location", None)
            clean.setdefault("gradcam_available", False)
            rebuilt.append(clean)
        normalized["model_findings"]["findings"] = rebuilt
    else:
        raise ClinicalSchemaError("Thiếu model_findings hợp lệ.")

    return NormalizationResult(normalized, tuple(warnings))


def validate_reasoning_payload(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not payload.get("model_findings", {}).get("provided"):
        errors.append("Thiếu kết quả mô hình ảnh.")
    if not payload.get("symptoms", {}).get("provided"):
        warnings.append("Chưa có triệu chứng được cung cấp; chỉ có thể đánh giá rất giới hạn.")
    if payload.get("workflow_mode") == "WITH_LABS" and not payload.get("laboratory", {}).get("provided"):
        warnings.append("Chế độ WITH_LABS nhưng chưa có kết quả xét nghiệm.")
    return errors, warnings
