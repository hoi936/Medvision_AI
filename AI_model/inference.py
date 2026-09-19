"""Inference and Grad-CAM utilities for the MedVision Streamlit demo."""

from __future__ import annotations

import io
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pydicom
import torch
import torch.nn as nn
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from torchvision.models import densenet121


LOGGER = logging.getLogger("medvision.inference")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pth"
CLASS_PATH = BASE_DIR / "class_names.json"
THRESHOLD_PATH = BASE_DIR / "thresholds.json"
PREPROCESSING_PATH = BASE_DIR / "preprocessing.json"

NUM_CLASSES = 14
IMAGE_SIZE = 384
NORMAL_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
DICOM_EXTENSIONS = {".dcm", ".dicom"}

CACHE_IMAGE_MODE = "Preprocessed PNG/JPG from VinBigData cache"
RAW_DICOM_MODE = "Raw DICOM"
EXTERNAL_IMAGE_MODE = "External PNG/JPG"
INPUT_MODES = (CACHE_IMAGE_MODE, RAW_DICOM_MODE, EXTERNAL_IMAGE_MODE)

EXPECTED_CLASS_NAMES = [
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
]


class MedVisionError(RuntimeError):
    """A clear, user-facing error raised by the inference pipeline."""


def _read_json(path: Path, label: str) -> Any:
    if not path.is_file():
        raise MedVisionError(f"Không tìm thấy {label}: {path.name}")
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise MedVisionError(f"{path.name} không phải JSON hợp lệ.") from exc
    except OSError as exc:
        raise MedVisionError(f"Không thể đọc {path.name}: {exc}") from exc


@lru_cache(maxsize=1)
def load_configuration() -> tuple[list[str], dict[str, float], dict[str, Any]]:
    """Load and validate the immutable metadata shipped with the model."""
    class_names = _read_json(CLASS_PATH, "class_names.json")
    thresholds_raw = _read_json(THRESHOLD_PATH, "thresholds.json")
    preprocessing = _read_json(PREPROCESSING_PATH, "preprocessing.json")

    if class_names != EXPECTED_CLASS_NAMES:
        raise MedVisionError(
            "class_names.json phải chứa đúng 14 finding theo đúng thứ tự đã train."
        )
    if not isinstance(thresholds_raw, dict):
        raise MedVisionError("thresholds.json phải là một JSON object.")

    thresholds: dict[str, float] = {}
    for name in class_names:
        if name not in thresholds_raw:
            raise MedVisionError(f"thresholds.json thiếu finding: {name}")
        try:
            value = float(thresholds_raw[name])
        except (TypeError, ValueError) as exc:
            raise MedVisionError(f"Threshold của '{name}' không hợp lệ.") from exc
        if not 0.0 <= value <= 1.0:
            raise MedVisionError(f"Threshold của '{name}' phải nằm trong [0, 1].")
        thresholds[name] = value
    if len(thresholds_raw) != NUM_CLASSES:
        raise MedVisionError("thresholds.json phải chứa đúng 14 threshold.")

    required = {"image_size", "channels", "imagenet_mean", "imagenet_std"}
    missing = required.difference(preprocessing)
    if missing:
        raise MedVisionError(
            "preprocessing.json thiếu cấu hình: " + ", ".join(sorted(missing))
        )
    if int(preprocessing["image_size"]) != IMAGE_SIZE:
        raise MedVisionError(f"Model yêu cầu image_size = {IMAGE_SIZE}.")
    if int(preprocessing["channels"]) != 3:
        raise MedVisionError("Model yêu cầu ảnh đầu vào có 3 channels.")
    if len(preprocessing["imagenet_mean"]) != 3 or len(
        preprocessing["imagenet_std"]
    ) != 3:
        raise MedVisionError("ImageNet mean/std phải có đúng 3 giá trị.")

    return class_names, thresholds, preprocessing


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _extract_state_dict(checkpoint: Any) -> dict[str, torch.Tensor]:
    if not isinstance(checkpoint, dict):
        raise MedVisionError("Checkpoint model.pth không chứa state_dict hợp lệ.")
    for key in ("model_state_dict", "state_dict"):
        candidate = checkpoint.get(key)
        if isinstance(candidate, dict):
            checkpoint = candidate
            break
    if not checkpoint or not all(isinstance(key, str) for key in checkpoint):
        raise MedVisionError("Không nhận diện được state_dict trong model.pth.")
    if all(key.startswith("module.") for key in checkpoint):
        checkpoint = {key[7:]: value for key, value in checkpoint.items()}
    return checkpoint


def load_model(device: torch.device | None = None) -> nn.Module:
    """Build DenseNet121 and load the provided weights unchanged."""
    load_configuration()
    if not MODEL_PATH.is_file():
        raise MedVisionError(f"Không tìm thấy model: {MODEL_PATH.name}")

    device = device or get_device()
    model = densenet121(weights=None)
    model.classifier = nn.Linear(model.classifier.in_features, NUM_CLASSES)
    try:
        try:
            checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
        except TypeError:  # Compatibility with older supported PyTorch versions.
            checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        model.load_state_dict(_extract_state_dict(checkpoint), strict=True)
    except MedVisionError:
        raise
    except Exception as exc:
        raise MedVisionError(f"Không thể load model.pth: {exc}") from exc

    model.to(device)
    model.eval()
    return model


def normalize_xray(image: np.ndarray, image_size: int = IMAGE_SIZE) -> np.ndarray:
    """Apply p0.5/p99.5 normalization once to a raw grayscale image."""
    image = np.asarray(image)
    if image.ndim != 2 or image.size == 0:
        raise MedVisionError("Ảnh X-quang phải là ảnh grayscale 2 chiều.")
    image = image.astype(np.float32)
    if not np.isfinite(image).any():
        raise MedVisionError("Ảnh không chứa pixel hợp lệ.")
    image = np.nan_to_num(image, nan=0.0, posinf=0.0, neginf=0.0)

    low, high = np.percentile(image, (0.5, 99.5))
    if high <= low:
        low, high = float(image.min()), float(image.max())
    if high <= low:
        raise MedVisionError("Ảnh không có đủ độ tương phản để phân tích.")

    image = np.clip(image, low, high)
    image = (image - low) / (high - low)
    image = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
    return (image * 255.0).astype(np.uint8)


def validate_gray_image(image: np.ndarray) -> np.ndarray:
    """Validate the exact uint8 384x384 array sent to the tensor transform."""
    if not isinstance(image, np.ndarray):
        raise MedVisionError("Ảnh sau preprocess phải là numpy array.")
    if image.shape != (IMAGE_SIZE, IMAGE_SIZE):
        raise MedVisionError(
            f"Ảnh sau preprocess phải có shape ({IMAGE_SIZE}, {IMAGE_SIZE}), "
            f"nhận được {image.shape}."
        )
    if image.dtype != np.uint8:
        raise MedVisionError(
            f"Ảnh sau preprocess phải có dtype uint8, nhận được {image.dtype}."
        )
    minimum, maximum = int(image.min()), int(image.max())
    if minimum < 0 or maximum > 255:
        raise MedVisionError("Pixel ảnh sau preprocess phải nằm trong [0, 255].")
    return image


def read_dicom(file_bytes: bytes, image_size: int = IMAGE_SIZE) -> np.ndarray:
    """Read and preprocess one raw DICOM exactly once."""
    try:
        dataset = pydicom.dcmread(io.BytesIO(file_bytes))
        image = dataset.pixel_array.astype(np.float32)
    except Exception as exc:
        raise MedVisionError(f"Không thể đọc ảnh DICOM: {exc}") from exc
    if image.ndim != 2:
        raise MedVisionError("Chỉ hỗ trợ DICOM X-quang một frame, grayscale 2 chiều.")
    if getattr(dataset, "PhotometricInterpretation", "") == "MONOCHROME1":
        image = image.max() - image
    return validate_gray_image(normalize_xray(image, image_size))


def read_normal_image(
    file_bytes: bytes,
    image_size: int = IMAGE_SIZE,
    *,
    apply_percentile_normalization: bool = False,
) -> np.ndarray:
    """Read PNG/JPG; cached inputs are only converted/resized, never renormalized."""
    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            image.load()
            gray = np.array(image.convert("L"), dtype=np.uint8)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise MedVisionError(f"Không thể đọc ảnh PNG/JPG: {exc}") from exc

    if apply_percentile_normalization:
        gray = normalize_xray(gray, image_size)
    elif gray.shape != (image_size, image_size):
        gray = cv2.resize(gray, (image_size, image_size), interpolation=cv2.INTER_AREA)
        gray = gray.astype(np.uint8, copy=False)
    return validate_gray_image(gray)


def preprocess_upload(file_bytes: bytes, filename: str, input_mode: str) -> np.ndarray:
    """Route input through the explicitly selected preprocessing pipeline."""
    if not file_bytes:
        raise MedVisionError("File tải lên đang trống.")
    if input_mode not in INPUT_MODES:
        raise MedVisionError("Input type không hợp lệ.")

    extension = Path(filename).suffix.lower()
    _, _, preprocessing = load_configuration()
    image_size = int(preprocessing["image_size"])

    if input_mode == RAW_DICOM_MODE:
        if extension not in DICOM_EXTENSIONS:
            raise MedVisionError("Chế độ Raw DICOM chỉ nhận file .dcm hoặc .dicom.")
        return read_dicom(file_bytes, image_size)
    if extension not in NORMAL_IMAGE_EXTENSIONS:
        raise MedVisionError("Chế độ PNG/JPG chỉ nhận file .png, .jpg hoặc .jpeg.")
    return read_normal_image(
        file_bytes,
        image_size,
        apply_percentile_normalization=input_mode == EXTERNAL_IMAGE_MODE,
    )


def prepare_tensor(gray: np.ndarray) -> torch.Tensor:
    """Stack grayscale to RGB then apply ToTensor and ImageNet normalization."""
    validate_gray_image(gray)
    _, _, preprocessing = load_configuration()
    rgb = np.stack([gray, gray, gray], axis=-1)
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[float(value) for value in preprocessing["imagenet_mean"]],
                std=[float(value) for value in preprocessing["imagenet_std"]],
            ),
        ]
    )
    tensor = transform(rgb)
    if tuple(tensor.shape) != (3, IMAGE_SIZE, IMAGE_SIZE):
        raise MedVisionError(
            f"Tensor phải có shape [3, 384, 384], nhận được {list(tensor.shape)}."
        )
    return tensor


def predict_findings(
    file_bytes: bytes,
    filename: str,
    input_mode: str = CACHE_IMAGE_MODE,
    model: nn.Module | None = None,
    device: torch.device | None = None,
) -> tuple[np.ndarray, list[dict[str, Any]], dict[str, Any], torch.Tensor]:
    """Run multi-label inference and return the exact batched tensor for Grad-CAM."""
    class_names, thresholds, _ = load_configuration()
    device = device or get_device()
    model = model or load_model(device)
    gray = preprocess_upload(file_bytes, filename, input_mode)
    input_tensor = prepare_tensor(gray).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        logits = model(input_tensor)
        if tuple(logits.shape) != (1, NUM_CLASSES):
            raise MedVisionError(
                f"Model output phải có shape [1, 14], nhận được {list(logits.shape)}."
            )
        probabilities = torch.sigmoid(logits)[0]

    scores = probabilities.detach().cpu().numpy()
    if len(scores) != NUM_CLASSES:
        raise MedVisionError(f"Model phải trả 14 score, nhận được {len(scores)}.")
    if not np.all(np.isfinite(scores)) or np.any(scores < 0) or np.any(scores > 1):
        raise MedVisionError("Sigmoid score của model phải nằm trong [0, 1].")

    results = []
    for class_id, name in enumerate(class_names):
        score = float(scores[class_id])
        threshold = thresholds[name]
        results.append(
            {
                "class_id": class_id,
                "finding": name,
                "score": score,
                "threshold": threshold,
                "positive": score >= threshold,
            }
        )
    if len(results) != NUM_CLASSES:
        raise MedVisionError("Kết quả inference không đủ 14 findings.")
    results.sort(key=lambda item: item["score"], reverse=True)

    debug_info = {
        "filename": filename,
        "input_mode": input_mode,
        "image_shape": tuple(gray.shape),
        "image_dtype": str(gray.dtype),
        "image_min": int(gray.min()),
        "image_max": int(gray.max()),
        "tensor_shape": tuple(input_tensor.shape),
        "tensor_min": float(input_tensor.min().detach().cpu()),
        "tensor_max": float(input_tensor.max().detach().cpu()),
        "model_device": str(next(model.parameters()).device),
        "logits_shape": tuple(logits.shape),
        "raw_scores": {name: float(scores[index]) for index, name in enumerate(class_names)},
        "thresholds": {name: thresholds[name] for name in class_names},
    }

    extreme_count = int(np.sum(scores > 0.95))
    if extreme_count >= 7:
        LOGGER.warning(
            "Suspicious output: %d/14 scores > 0.95; input=%s; scores=%s; thresholds=%s",
            extreme_count,
            {
                key: debug_info[key]
                for key in (
                    "filename",
                    "input_mode",
                    "image_shape",
                    "image_dtype",
                    "image_min",
                    "image_max",
                    "tensor_shape",
                    "tensor_min",
                    "tensor_max",
                )
            },
            debug_info["raw_scores"],
            debug_info["thresholds"],
        )
    debug_info["scores_above_95_percent"] = extreme_count
    return gray, results, debug_info, input_tensor.detach()


def generate_gradcam_for_class(
    model: nn.Module,
    input_tensor: torch.Tensor,
    class_index: int,
) -> np.ndarray:
    """Return one normalized Grad-CAM map for exactly one class."""
    if not 0 <= class_index < NUM_CLASSES:
        raise MedVisionError("Class được chọn cho Grad-CAM không hợp lệ.")
    if tuple(input_tensor.shape) != (1, 3, IMAGE_SIZE, IMAGE_SIZE):
        raise MedVisionError(
            "Grad-CAM yêu cầu đúng tensor inference có shape [1, 3, 384, 384]."
        )

    model_device = next(model.parameters()).device
    tensor = input_tensor.detach().to(model_device)
    captured: dict[str, torch.Tensor] = {}

    def forward_hook(_module: nn.Module, _inputs: Any, output: torch.Tensor) -> None:
        captured["activations"] = output
        output.register_hook(lambda gradient: captured.__setitem__("gradients", gradient))

    handle = model.features.norm5.register_forward_hook(forward_hook)
    try:
        model.eval()
        model.zero_grad(set_to_none=True)
        with torch.enable_grad():
            logits = model(tensor)
            if tuple(logits.shape) != (1, NUM_CLASSES):
                raise MedVisionError("Model output không đúng [1, 14] khi tạo Grad-CAM.")
            logits[0, class_index].backward()

        activations = captured.get("activations")
        gradients = captured.get("gradients")
        if activations is None or gradients is None:
            raise MedVisionError("Không thu được feature map để tạo Grad-CAM.")
        weights = gradients.mean(dim=(2, 3), keepdim=True)
        cam = torch.relu((weights * activations).sum(dim=1, keepdim=True))
        cam = torch.nn.functional.interpolate(
            cam, size=(IMAGE_SIZE, IMAGE_SIZE), mode="bilinear", align_corners=False
        )[0, 0]
        cam = cam.detach().cpu().numpy()
    finally:
        handle.remove()
        model.zero_grad(set_to_none=True)

    cam_min, cam_max = float(cam.min()), float(cam.max())
    if cam_max > cam_min:
        cam = (cam - cam_min) / (cam_max - cam_min)
    else:
        cam = np.zeros_like(cam, dtype=np.float32)

    return cam.astype(np.float32, copy=False)


def create_heatmap(cam: np.ndarray) -> np.ndarray:
    """Convert a normalized CAM to an RGB JET heatmap."""
    if cam.shape != (IMAGE_SIZE, IMAGE_SIZE):
        raise MedVisionError("Grad-CAM map phải có shape [384, 384].")
    if not np.all(np.isfinite(cam)) or float(cam.min()) < 0 or float(cam.max()) > 1:
        raise MedVisionError("Grad-CAM map phải hữu hạn và nằm trong [0, 1].")
    heatmap_bgr = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    return cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)


def create_overlay(
    original_image: np.ndarray,
    cam: np.ndarray,
    original_weight: float = 0.6,
) -> np.ndarray:
    """Overlay one class-specific CAM on the original grayscale X-ray."""
    validate_gray_image(original_image)
    if not 0.0 <= original_weight <= 1.0:
        raise MedVisionError("original_weight phải nằm trong [0, 1].")
    heatmap_rgb = create_heatmap(cam)
    original_rgb = np.stack([original_image, original_image, original_image], axis=-1)
    return cv2.addWeighted(
        original_rgb,
        original_weight,
        heatmap_rgb,
        1.0 - original_weight,
        0,
    )


def extract_pseudo_bboxes_from_cam(
    cam: np.ndarray,
    cam_threshold: float = 0.5,
    min_area_ratio: float = 0.01,
) -> list[dict[str, float | int]]:
    """Extract independent connected-component boxes from one normalized CAM."""
    if cam.shape != (IMAGE_SIZE, IMAGE_SIZE):
        raise MedVisionError("Grad-CAM map phải có shape [384, 384].")
    if not 0.0 <= cam_threshold <= 1.0:
        raise MedVisionError("CAM threshold phải nằm trong [0, 1].")
    if not 0.0 <= min_area_ratio <= 1.0:
        raise MedVisionError("Min area ratio phải nằm trong [0, 1].")

    binary_mask = (cam >= cam_threshold).astype(np.uint8)
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
        binary_mask, connectivity=8
    )
    image_area = float(IMAGE_SIZE * IMAGE_SIZE)
    minimum_area = image_area * min_area_ratio
    boxes: list[dict[str, float | int]] = []

    for component_id in range(1, count):
        x = int(stats[component_id, cv2.CC_STAT_LEFT])
        y = int(stats[component_id, cv2.CC_STAT_TOP])
        width = int(stats[component_id, cv2.CC_STAT_WIDTH])
        height = int(stats[component_id, cv2.CC_STAT_HEIGHT])
        area = int(stats[component_id, cv2.CC_STAT_AREA])
        if area < minimum_area:
            continue
        boxes.append(
            {
                "x1": x,
                "y1": y,
                "x2": min(x + width - 1, IMAGE_SIZE - 1),
                "y2": min(y + height - 1, IMAGE_SIZE - 1),
                "area": area,
                "area_ratio": area / image_area,
            }
        )

    boxes.sort(key=lambda box: int(box["area"]), reverse=True)
    return boxes


def draw_bboxes_on_image(
    original_image: np.ndarray,
    pseudo_boxes: list[dict[str, float | int]],
) -> np.ndarray:
    """Draw green pseudo boxes without modifying the source image."""
    validate_gray_image(original_image)
    boxed_image = np.stack(
        [original_image, original_image, original_image], axis=-1
    ).copy()
    for box in pseudo_boxes:
        start = (int(box["x1"]), int(box["y1"]))
        end = (int(box["x2"]), int(box["y2"]))
        cv2.rectangle(boxed_image, start, end, (0, 255, 0), 2)
    return boxed_image


def generate_gradcam(
    model: nn.Module,
    gray: np.ndarray,
    input_tensor: torch.Tensor,
    class_index: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Backward-compatible helper returning heatmap and overlay for one class."""
    validate_gray_image(gray)
    cam = generate_gradcam_for_class(model, input_tensor, class_index)
    return create_heatmap(cam), create_overlay(gray, cam)


# Preserve the original public name for callers created before the refactor.
predict = predict_findings
