"""Secret-safe version snapshot for a clinical dataset evaluation run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from .metrics import METRIC_SPECIFICATION_VERSION


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PINNED_HERMES_COMMIT = "2552fb543bd12a326d23449f41a9c13c48eb4e9a"


def _sha256_files(paths, *, relative_to):
    digest = hashlib.sha256()
    found = False
    for path in sorted(paths):
        if not path.is_file():
            continue
        found = True
        digest.update(str(path.relative_to(relative_to)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest() if found else None


def _repo_commit():
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
        capture_output=True, text=True, check=False, shell=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def _hermes_version():
    executable = PROJECT_ROOT / ".runtime" / "hermes-venv" / "bin" / "hermes"
    if not executable.is_file():
        return None
    completed = subprocess.run(
        [str(executable), "--version"], cwd=PROJECT_ROOT,
        capture_output=True, text=True, check=False, shell=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _hermes_python_version():
    executable = PROJECT_ROOT / ".runtime" / "hermes-venv" / "bin" / "python"
    if not executable.is_file():
        return None
    completed = subprocess.run(
        [str(executable), "--version"], cwd=PROJECT_ROOT,
        capture_output=True, text=True, check=False, shell=False,
    )
    if completed.returncode != 0:
        return None
    text = (completed.stdout or completed.stderr).strip()
    return text.removeprefix("Python ") or None


def _provider_identity():
    try:
        from hermes_real_runtime import provider_identity
        identity = provider_identity()
        return identity.get("provider") or None, identity.get("model") or None
    except Exception:
        return None, None


def capture_system_snapshot(dataset_version, *, provider=None, model=None):
    if provider is None and model is None:
        provider, model = _provider_identity()
    config_root = PROJECT_ROOT / ".runtime" / "hermes-home"
    config_candidates = [
        config_root / "config.yaml", config_root / "config.yml", config_root / "config.json",
    ]
    config_hash = _sha256_files(config_candidates, relative_to=PROJECT_ROOT)
    skills_root = PROJECT_ROOT / ".hermes" / "skills"
    skill_tree_hash = _sha256_files(skills_root.rglob("*"), relative_to=PROJECT_ROOT)
    snapshot = {
        "repo_commit": _repo_commit(),
        "hermes_version": _hermes_version(),
        "hermes_commit": PINNED_HERMES_COMMIT,
        "python_version": _hermes_python_version(),
        "provider": provider,
        "model": model,
        "config_hash": config_hash,
        "skill_tree_hash": skill_tree_hash,
        "dataset_version": dataset_version,
        "metric_specification_version": METRIC_SPECIFICATION_VERSION,
    }
    snapshot["unknown_fields"] = sorted(
        key for key, value in snapshot.items() if value is None
    )
    snapshot["snapshot_hash"] = hashlib.sha256(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return snapshot
