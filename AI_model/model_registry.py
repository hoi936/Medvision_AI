"""Validated registry for the MedVision model versions and V4 experiments."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parent

EXPECTED_CLASS_NAMES = (
    "Aortic enlargement",
    "Atelectasis",
    "Calcification",
    "Cardiomegaly",
    "Consolidation",
    "ILD",
    "Infiltration",
    "Lung Opacity",
    "Nodule/Mass",
    "Other lesion",
    "Pleural effusion",
    "Pleural thickening",
    "Pneumothorax",
    "Pulmonary fibrosis",
)


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    display_name: str
    model_name: str
    model_version: str
    architecture: str
    pipeline: str
    checkpoint_path: Path
    thresholds_path: Path
    thresholds_format: str
    macro_pr_auc: str
    macro_roc_auc: str
    macro_f1: str
    thresholds_key: str | None = None
    recommended: bool = False

    @property
    def select_label(self) -> str:
        return self.display_name + (" (khuyến nghị)" if self.recommended else "")


MODEL_SPECS: dict[str, ModelSpec] = {
    "v1": ModelSpec(
        model_id="v1",
        display_name="V1 — DenseNet121 Baseline",
        model_name="DenseNet121",
        model_version="v1-baseline-best-epoch-8",
        architecture="densenet121",
        pipeline="ImageNet → VinBigData",
        checkpoint_path=APP_DIR / "model.pth",
        thresholds_path=APP_DIR / "thresholds.json",
        thresholds_format="mapping_json",
        macro_pr_auc="53.68%",
        macro_roc_auc="95.98%",
        macro_f1="55.34%",
    ),
    "v2": ModelSpec(
        model_id="v2",
        display_name="V2 — DenseNet121 + CBAM",
        model_name="DenseNet121 + CBAM",
        model_version="v2-cbam-best-epoch-7",
        architecture="densenet121_cbam",
        pipeline="ImageNet → CBAM → VinBigData",
        checkpoint_path=APP_DIR / "models" / "model_v2_cbam.pth",
        thresholds_path=APP_DIR / "models" / "thresholds_v2.json",
        thresholds_format="mapping_json",
        macro_pr_auc="52.07%",
        macro_roc_auc="96.03%",
        macro_f1="54.07%",
    ),
    "v3": ModelSpec(
        model_id="v3",
        display_name="V3 — DenseNet121 + CheXpert Transfer",
        model_name="DenseNet121",
        model_version="v3-chexpert-transfer-best-epoch-7",
        architecture="densenet121",
        pipeline="ImageNet → CheXpert → VinBigData",
        checkpoint_path=APP_DIR / "models" / "model_v3_transfer.pth",
        thresholds_path=APP_DIR / "models" / "thresholds_v3.json",
        thresholds_format="mapping_json",
        macro_pr_auc="57.56%",
        macro_roc_auc="96.68%",
        macro_f1="57.71%",
    ),
    "e0": ModelSpec(
        model_id="e0",
        display_name="V4 E0 — Control",
        model_name="DenseNet121",
        model_version="v4-e0-control-best-epoch-9",
        architecture="densenet121",
        pipeline="CheXpert init → VinBigData → Asymmetric Loss",
        checkpoint_path=APP_DIR / "models" / "model_v4_e0_control.pth",
        thresholds_path=APP_DIR / "models" / "thresholds_v4.json",
        thresholds_format="v4_validation_json",
        thresholds_key="E0",
        macro_pr_auc="58.91%",
        macro_roc_auc="96.87%",
        macro_f1="59.28%",
    ),
    "e1": ModelSpec(
        model_id="e1",
        display_name="V4 E1 — Sqrt Weight",
        model_name="DenseNet121",
        model_version="v4-e1-sqrt-weight-best-epoch-9",
        architecture="densenet121",
        pipeline="CheXpert init → VinBigData → Sqrt-weighted ASL",
        checkpoint_path=APP_DIR / "models" / "model_v4_e1_sqrt_weight.pth",
        thresholds_path=APP_DIR / "models" / "thresholds_v4.json",
        thresholds_format="v4_validation_json",
        thresholds_key="E1",
        macro_pr_auc="60.48%",
        macro_roc_auc="96.91%",
        macro_f1="60.27%",
    ),
    "e2": ModelSpec(
        model_id="e2",
        display_name="V4 E2 — Effective Number β=0.99",
        model_name="DenseNet121",
        model_version="v4-e2-effective-number-beta099-best-epoch-11",
        architecture="densenet121",
        pipeline="CheXpert init → VinBigData → Effective-number ASL",
        checkpoint_path=APP_DIR / "models" / "model_v4_e2_beta099.pth",
        thresholds_path=APP_DIR / "models" / "thresholds_v4.json",
        thresholds_format="v4_validation_json",
        thresholds_key="E2",
        macro_pr_auc="60.62%",
        macro_roc_auc="96.87%",
        macro_f1="61.30%",
        recommended=True,
    ),
}

DEFAULT_MODEL_ID = "e2"
MODEL_IDS = tuple(MODEL_SPECS)


class ModelRegistryError(RuntimeError):
    """Raised when a versioned model package is absent or inconsistent."""


def get_model_spec(model_id: str) -> ModelSpec:
    try:
        return MODEL_SPECS[model_id]
    except KeyError as exc:
        raise ModelRegistryError(f"Model không hợp lệ: {model_id}") from exc


def get_model_options() -> dict[str, str]:
    return {model_id: spec.select_label for model_id, spec in MODEL_SPECS.items()}


def _read_json(path: Path, label: str) -> Any:
    if not path.is_file():
        raise ModelRegistryError(f"Không tìm thấy {label}: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelRegistryError(f"Không đọc được {label}: {exc}") from exc


def _validate_thresholds(rows: list[tuple[int, str, float]]) -> dict[str, float]:
    if len(rows) != len(EXPECTED_CLASS_NAMES):
        raise ModelRegistryError("Bảng threshold phải chứa đúng 14 findings.")
    rows.sort(key=lambda row: row[0])
    names = tuple(row[1] for row in rows)
    if names != EXPECTED_CLASS_NAMES:
        raise ModelRegistryError("Thứ tự class trong bảng threshold không khớp lúc train.")
    thresholds = {name: value for _class_id, name, value in rows}
    if any(not 0.0 <= value <= 1.0 for value in thresholds.values()):
        raise ModelRegistryError("Mọi threshold phải nằm trong [0, 1].")
    return thresholds


def _load_thresholds(spec: ModelSpec) -> dict[str, float]:
    if spec.thresholds_format == "metrics_csv":
        try:
            with spec.thresholds_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                rows = [
                    (int(row["class_id"]), row["finding"].strip(), float(row["threshold"]))
                    for row in reader
                ]
        except (OSError, KeyError, TypeError, ValueError) as exc:
            raise ModelRegistryError(
                f"Không đọc được threshold của {spec.display_name}: {exc}"
            ) from exc
        return _validate_thresholds(rows)

    raw = _read_json(spec.thresholds_path, "thresholds.json")
    if spec.thresholds_format == "v4_validation_json":
        try:
            values = [
                float(value)
                for value in raw["thresholds"][spec.thresholds_key]["optimized"]
            ]
        except (KeyError, TypeError, ValueError) as exc:
            raise ModelRegistryError(
                f"Threshold V4 của {spec.display_name} không đúng schema."
            ) from exc
        if len(values) != len(EXPECTED_CLASS_NAMES):
            raise ModelRegistryError(
                f"Threshold V4 của {spec.display_name} phải có đúng 14 giá trị."
            )
        return _validate_thresholds(
            [
                (index, name, values[index])
                for index, name in enumerate(EXPECTED_CLASS_NAMES)
            ]
        )

    if spec.thresholds_format == "mapping_json":
        if not isinstance(raw, dict):
            raise ModelRegistryError("thresholds.json phải là object theo tên finding.")
        try:
            return _validate_thresholds(
                [
                    (index, name, float(raw[name]))
                    for index, name in enumerate(EXPECTED_CLASS_NAMES)
                ]
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ModelRegistryError(
                f"thresholds.json của {spec.display_name} không đúng schema."
            ) from exc
    try:
        names = tuple(str(name) for name in raw["class_names"])
        values = [float(value) for value in raw["thresholds"]]
    except (KeyError, TypeError, ValueError) as exc:
        raise ModelRegistryError(
            f"thresholds.json của {spec.display_name} không đúng schema."
        ) from exc
    return _validate_thresholds(
        [(index, name, values[index]) for index, name in enumerate(names)]
    )


@lru_cache(maxsize=len(MODEL_SPECS))
def load_model_package(model_id: str) -> tuple[ModelSpec, list[str], dict[str, float], dict[str, Any]]:
    """Validate paths, thresholds and deployment metadata for one version."""
    spec = get_model_spec(model_id)
    if not spec.checkpoint_path.is_file():
        raise ModelRegistryError(
            f"Thiếu checkpoint của {spec.display_name}: {spec.checkpoint_path}"
        )
    thresholds = _load_thresholds(spec)
    preprocessing = {
        "image_size": 384,
        "channels": 3,
        "imagenet_mean": [0.485, 0.456, 0.406],
        "imagenet_std": [0.229, 0.224, 0.225],
        "dicom_normalization": "percentile_0.5_99.5",
        "monochrome1_inversion": True,
    }
    return spec, list(EXPECTED_CLASS_NAMES), thresholds, preprocessing


def model_summary(model_id: str) -> dict[str, str]:
    spec = get_model_spec(model_id)
    return {
        "Phiên bản": spec.display_name,
        "Kiến trúc": spec.model_name,
        "Pipeline": spec.pipeline,
        "Macro PR-AUC": spec.macro_pr_auc,
        "Macro ROC-AUC": spec.macro_roc_auc,
        "Macro F1": spec.macro_f1,
    }
