# Hermes Provider Activation and Real Validation

The pytest runner and the Hermes runtime are intentionally separate:

```text
pytest runner:       AI_model/.venv/bin/python
Hermes under test:   .runtime/hermes-venv/bin/hermes
Hermes home:         .runtime/hermes-home
Hermes version:      0.21.4
Hermes source commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
```

Do not install pytest or other test dependencies into `.runtime/hermes-venv`.

## Select the established project test environment

From the repository root:

```bash
PROJECT_ROOT="$PWD"
PROJECT_TEST_PYTHON="$PROJECT_ROOT/AI_model/.venv/bin/python"
HERMES_BIN="$PROJECT_ROOT/.runtime/hermes-venv/bin/hermes"
export PROJECT_TEST_PYTHON
export HERMES_HOME="$PROJECT_ROOT/.runtime/hermes-home"

test -x "$PROJECT_TEST_PYTHON"
test -x "$HERMES_BIN"
```

`PROJECT_TEST_PYTHON` is the existing interpreter that runs the deterministic
MedVision test suite. All Hermes probes and inference still execute through
`$HERMES_BIN` or its sibling runtime Python. The preflight rejects a missing or
different Hermes binary rather than searching globally.

## Configure a provider

Use only a provider and model supported by the pinned runtime:

```bash
HERMES_HOME="$HERMES_HOME" "$HERMES_BIN" model
```

Follow Hermes 0.21.4 authentication without printing or committing credentials.

## Run real validation

The repository launcher runs preflight first and stops before every clinical
suite if preflight fails:

```bash
PROJECT_TEST_PYTHON="$PROJECT_TEST_PYTHON" \
  bash AI_model/scripts/run_real_validation.sh
```

The equivalent manual preflight is:

```bash
cd "$PROJECT_ROOT/AI_model"
RUN_HERMES_REAL=1 HERMES_HOME="$HERMES_HOME" \
  "$PROJECT_TEST_PYTHON" -m pytest tests/test_provider_readiness_real.py -q
```

Before provider activation, the expected result is:

```text
INFRASTRUCTURE_CONFIGURATION:
RUN_HERMES_REAL=1 but no usable provider/model is configured
```

Only after preflight passes, run:

```bash
RUN_HERMES_REAL=1 HERMES_HOME="$HERMES_HOME" \
  "$PROJECT_TEST_PYTHON" -m pytest tests/test_behavior_*_real.py -q

RUN_HERMES_REAL=1 HERMES_HOME="$HERMES_HOME" \
  "$PROJECT_TEST_PYTHON" -m pytest tests/test_behavior_cross_skill_real.py -q
```

## Deterministic regression

From `AI_model`:

```bash
"$PROJECT_TEST_PYTHON" -m pytest -q
cd "$PROJECT_ROOT"
git diff --check
```

Provider validation is complete only when preflight passes, all intended real
cases execute without infrastructure or clinical semantic failures, discovery
remains at 17 enabled local skills, and runtime/write/tool hardening remains
unchanged.
