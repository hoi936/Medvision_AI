#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ai_model_dir="$(cd "$script_dir/.." && pwd)"
project_root="$(cd "$ai_model_dir/.." && pwd)"

project_test_python="${PROJECT_TEST_PYTHON:-$ai_model_dir/.venv/bin/python}"
hermes_bin="$project_root/.runtime/hermes-venv/bin/hermes"
export HERMES_HOME="$project_root/.runtime/hermes-home"
export RUN_HERMES_REAL=1

if [[ ! -x "$project_test_python" ]]; then
  printf 'INFRASTRUCTURE_CONFIGURATION: project pytest interpreter is unavailable: %s\n' "$project_test_python" >&2
  exit 2
fi
if [[ ! -x "$hermes_bin" ]]; then
  printf 'INFRASTRUCTURE_CONFIGURATION: pinned Hermes executable is unavailable: %s\n' "$hermes_bin" >&2
  exit 2
fi

cd "$ai_model_dir"

printf 'stage=provider-preflight\n'
"$project_test_python" -m pytest tests/test_provider_readiness_real.py -q

printf 'stage=all-real-suites\n'
"$project_test_python" -m pytest tests/test_behavior_*_real.py -q

printf 'stage=cross-skill-isolated\n'
"$project_test_python" -m pytest tests/test_behavior_cross_skill_real.py -q
