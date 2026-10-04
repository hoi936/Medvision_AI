"""Shared, secret-safe preflight for provider-backed MedVision tests."""

from __future__ import annotations

from functools import lru_cache
import json
import os
from pathlib import Path
import re
import subprocess

from hermes_report import (
    CORE_HERMES_SKILLS,
    FINDING_SKILL_MAP,
    HERMES_HOME,
    HERMES_RUNTIME,
    HERMES_SKILLS_TOOLS,
    HERMES_TEXT_TOOLSETS,
    HERMES_VISION_TOOLSETS,
    discover_hermes_skills,
    hermes_environment,
    hermes_skill_write_approval_enabled,
    locate_hermes,
)


PINNED_HERMES_COMMIT = "2552fb543bd12a326d23449f41a9c13c48eb4e9a"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENDOR_SOURCE = PROJECT_ROOT / ".vendor" / "hermes-agent-upstream"


class ProviderPreflightError(RuntimeError):
    def __init__(self, classification: str, reason: str, metadata: dict | None = None):
        super().__init__(reason)
        self.classification = classification
        self.reason = reason
        self.metadata = metadata or {}


def _safe_identity(value) -> str:
    text = str(value or "").strip()
    return re.sub(r"[^A-Za-z0-9._:@/+\-]", "?", text)[:160]


def sanitize_infrastructure_detail(value) -> str:
    text = " ".join(str(value or "").split())
    text = re.sub(
        r"(?i)(api[_-]?key|token|secret|authorization|bearer)\s*[:=]\s*\S+",
        r"\1=<redacted>",
        text,
    )
    return text[-1200:]


def classify_runtime_failure(detail: str) -> str:
    lowered = str(detail or "").lower()
    configuration_markers = (
        "no usable provider/model",
        "no llm provider configured",
        "no_provider_configured",
        "missing_api_key",
        "not connected to any ai provider",
        "authentication",
        "unauthorized",
        "http 401",
        "http 403",
        "invalid api key",
        "model is not set",
    )
    if any(marker in lowered for marker in configuration_markers):
        return "INFRASTRUCTURE_CONFIGURATION"
    return "INFRASTRUCTURE_TRANSIENT"


def _expected_hermes_executable() -> Path:
    relative = Path("Scripts/hermes.exe") if os.name == "nt" else Path("bin/hermes")
    return (HERMES_RUNTIME / relative).resolve()


def _pinned_hermes_executable() -> Path:
    """Return only the project-isolated Hermes binary; never accept a fallback."""
    executable = locate_hermes()
    expected = _expected_hermes_executable()
    if executable is None:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "isolated pinned Hermes executable is missing",
        )
    if executable != expected:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "Hermes executable is not the project-isolated pinned runtime",
        )
    return executable


def _runtime_python() -> Path:
    executable = _pinned_hermes_executable()
    runtime_python = executable.parent / ("python.exe" if os.name == "nt" else "python")
    if not runtime_python.is_file():
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "isolated pinned Hermes Python is missing",
        )
    return runtime_python


def _run_checked(command, *, timeout=60):
    completed = subprocess.run(
        [str(part) for part in command],
        cwd=PROJECT_ROOT,
        env=hermes_environment(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
        shell=False,
    )
    return completed


def _verify_pinned_runtime() -> Path:
    executable = _pinned_hermes_executable()
    if HERMES_HOME != PROJECT_ROOT / ".runtime" / "hermes-home":
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "HERMES_HOME is not the project-relative runtime home",
        )

    version = _run_checked([executable, "--version"])
    if version.returncode != 0 or "0.21.4" not in version.stdout:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "pinned Hermes 0.21.4 runtime is unavailable",
        )
    commit = subprocess.run(
        ["git", "-C", str(VENDOR_SOURCE), "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )
    if commit.returncode != 0 or commit.stdout.strip() != PINNED_HERMES_COMMIT:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "pinned Hermes source commit does not match the MedVision runtime",
        )
    return executable


@lru_cache(maxsize=1)
def provider_identity() -> dict:
    """Resolve provider/model through pinned Hermes without exposing a secret."""
    probe = r'''
import json
from hermes_cli.auth import PROVIDER_REGISTRY, resolve_provider
from hermes_cli.config import load_config, split_model_config_default
from hermes_cli.main import _has_any_provider_configured
from hermes_cli.providers import get_provider
from hermes_cli.runtime_provider import resolve_requested_provider, resolve_runtime_provider

cfg = load_config()
model_cfg = cfg.get("model")
if isinstance(model_cfg, dict):
    model, nested_provider = split_model_config_default(
        model_cfg.get("default") or model_cfg.get("model") or ""
    )
    configured_provider = str(model_cfg.get("provider") or nested_provider or "").strip()
else:
    model = str(model_cfg or "").strip()
    configured_provider = ""

requested = resolve_requested_provider()
result = {
    "provider": configured_provider,
    "requested_provider": requested,
    "model": model,
    "provider_configured": bool(_has_any_provider_configured()),
    "provider_registered": False,
    "credential_present": False,
    "auth_available": False,
    "resolution_error_code": "",
    "resolution_error_type": "",
}
if result["provider_configured"]:
    try:
        resolved = resolve_provider(requested)
        runtime = resolve_runtime_provider(requested=requested, target_model=model or None)
        effective = str(runtime.get("provider") or resolved or "").strip()
        result["provider"] = effective
        result["provider_registered"] = bool(
            effective in PROVIDER_REGISTRY
            or effective in {"openrouter", "custom"}
            or get_provider(effective)
        )
        raw_key = runtime.get("api_key")
        source = str(runtime.get("source") or "").strip().lower()
        result["credential_present"] = bool(
            raw_key and raw_key not in {"no-key-required", effective}
            and source not in {"process", "local"}
        )
        result["auth_available"] = True
    except Exception as exc:
        result["resolution_error_code"] = str(getattr(exc, "code", "") or "")
        result["resolution_error_type"] = type(exc).__name__
print(json.dumps(result))
'''
    completed = _run_checked([_runtime_python(), "-c", probe])
    if completed.returncode != 0:
        detail = sanitize_infrastructure_detail(completed.stderr or completed.stdout)
        raise ProviderPreflightError(
            classify_runtime_failure(detail),
            f"pinned provider probe failed: {detail}",
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "pinned provider probe returned invalid JSON",
        ) from exc
    for key in ("provider", "requested_provider", "model", "resolution_error_code", "resolution_error_type"):
        result[key] = _safe_identity(result.get(key))
    return result


def _tool_surfaces() -> dict:
    probe = r'''
import json, sys
from model_tools import get_tool_definitions
from toolsets import resolve_toolset
toolsets = list(sys.argv[1:])
selected = sorted(set().union(*(resolve_toolset(name) for name in toolsets)))
effective = sorted(
    item["function"]["name"]
    for item in get_tool_definitions(enabled_toolsets=toolsets, quiet_mode=True)
)
print(json.dumps({"selected": selected, "effective": effective}))
'''

    def resolve(toolsets):
        completed = _run_checked([_runtime_python(), "-c", probe, *toolsets])
        if completed.returncode != 0:
            detail = sanitize_infrastructure_detail(completed.stderr or completed.stdout)
            raise ProviderPreflightError(
                "INFRASTRUCTURE_CONFIGURATION",
                f"tool-surface probe failed: {detail}",
            )
        return json.loads(completed.stdout)

    return {
        "text": resolve(HERMES_TEXT_TOOLSETS),
        "vision": resolve(HERMES_VISION_TOOLSETS),
    }


def _require_provider(identity: dict, metadata: dict) -> None:
    if not identity["provider_configured"]:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "RUN_HERMES_REAL=1 but no usable provider/model is configured",
            metadata,
        )
    if not identity["model"]:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "configured provider has no default model",
            metadata,
        )
    if not identity["provider_registered"]:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "configured provider is not resolvable by the pinned registry/config path",
            metadata,
        )
    if not identity["auth_available"]:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "configured provider authentication is unavailable",
            metadata,
        )


@lru_cache(maxsize=1)
def run_provider_preflight() -> dict:
    executable = _verify_pinned_runtime()

    expected_skills = {*CORE_HERMES_SKILLS, *FINDING_SKILL_MAP.values()}
    if discover_hermes_skills(executable) != expected_skills:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "MedVision skill discovery changed from the expected 17-skill surface",
        )
    if not hermes_skill_write_approval_enabled(executable):
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "Hermes skills.write_approval is not enabled",
        )

    surfaces = _tool_surfaces()
    text_selected = set(surfaces["text"]["selected"])
    text_effective = set(surfaces["text"]["effective"])
    vision_selected = set(surfaces["vision"]["selected"])
    vision_effective = set(surfaces["vision"]["effective"])
    expected_text = {"clarify", *HERMES_SKILLS_TOOLS}
    expected_vision = expected_text | {"vision_analyze"}
    if text_selected != expected_text or text_effective != expected_text:
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "hardened text tool surface changed",
        )
    if vision_selected != expected_vision or vision_effective not in (
        expected_text, expected_vision
    ):
        raise ProviderPreflightError(
            "INFRASTRUCTURE_CONFIGURATION",
            "hardened vision tool surface changed",
        )

    identity = provider_identity()
    metadata = {
        "hermes_commit": PINNED_HERMES_COMMIT,
        "hermes_version": "0.21.4",
        "python": "3.11",
        "provider": identity["provider"],
        "model": identity["model"],
        "credential_present": bool(identity["credential_present"]),
        "auth_available": bool(identity["auth_available"]),
        "skill_count": len(expected_skills),
        "write_approval": True,
        "run_mode": "real",
    }
    _require_provider(identity, metadata)

    smoke = _run_checked(
        [
            executable,
            "--ignore-rules",
            "-t",
            ",".join(HERMES_TEXT_TOOLSETS),
            "-z",
            "Non-medical provider preflight. Reply with exactly: HERMES_SMOKE_OK",
        ],
        timeout=180,
    )
    if smoke.returncode != 0 or "HERMES_SMOKE_OK" not in smoke.stdout:
        detail = sanitize_infrastructure_detail(smoke.stderr or smoke.stdout)
        raise ProviderPreflightError(
            classify_runtime_failure(detail),
            f"minimal non-clinical inference failed: {detail}",
            metadata,
        )
    metadata["minimal_inference"] = "PASS"
    return metadata
