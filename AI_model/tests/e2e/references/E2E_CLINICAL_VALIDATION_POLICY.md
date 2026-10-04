# E2E_CLINICAL_VALIDATION_POLICY.md

## Integration target

This is a validation-harness module, not a new clinical skill.

Suggested repository destination:

```text
AI_model/tests/e2e/
├── e2e_clinical_validation.py
├── e2e_invariants.py
├── e2e_trace_schema.py
└── ...
```

Reference documents may be stored under the existing disease-analysis references if desired, but no new top-level Hermes skill is allowed.

## Harness design

### Layer A — Provider-independent E2E

Purpose:
- execute actual deterministic project code where available;
- inject explicit fixtures only where a provider-backed reasoning step cannot run;
- validate stage boundaries, provenance, missingness, conflicts, review gates, versioning, and report generation.

Each injected fixture must carry:

```yaml
execution_mode: fixture
fixture_id: null
```

Each actual project-code stage must carry:

```yaml
execution_mode: project_code
```

Never blur the distinction.

### Layer B — Real-provider E2E

Purpose:
- run the same scenario classes through the pinned real Hermes runtime;
- check the same global invariants;
- classify failures using existing infrastructure/semantic taxonomy.

Execution remains opt-in through the existing real-provider gate.

---

## Stage orchestration policy

Nominal provider-independent E2E order:

```text
1. load CASE_DATA fixture
2. canonicalize AI findings
3. apply No Finding policy
4. run selector/routing
5. execute deterministic evidence-fusion/finding logic where available
6. execute deterministic safety logic where available
7. attach disease-analysis fixture or project-code output
8. attach temporal fixture/project output when triggered
9. attach arbitration fixture/project output when triggered
10. create deterministic draft-report fixture
11. apply Structured Doctor Review fixture/validator
12. apply Final Report Generation validator
13. evaluate global invariants
14. emit normalized trace
```

Do not reorder stages to make an invariant pass.

---

## Fixture discipline

Fixtures are allowed only to isolate unavailable provider inference while still testing integration boundaries.

Every fixture must:
- be static;
- be human-readable;
- have fixed IDs/timestamps;
- declare which frozen module semantics it represents;
- contain no hidden random data;
- be validated against the owning module's provider-independent validator when possible.

A fixture is not evidence that a model can generate that output correctly.

---

## Golden E2E scenarios

Create:

```text
AI_model/tests/golden_cases/e2e_clinical_validation/cases.json
```

with at least 30 cases.

Each case should include:
- canonical CASE_DATA;
- expected selected skills;
- expected No Finding state;
- deterministic disease/temporal/arbitration fixtures where needed;
- doctor-review fixture;
- expected final-report status/content constraints;
- expected global invariant results.

---

## Recommended E2E cases

### E2E01 — Simple positive finding, doctor accepts
- one canonical positive finding;
- exactly one finding skill;
- no disease overreach;
- doctor accepts;
- final-report candidate rendered;
- not auto-finalized.

### E2E02 — Multiple positive findings preserve payload order
- three positive canonical findings;
- each routed exactly once;
- selector order preserved;
- no clinical-priority reinterpretation from order.

### E2E03 — No Finding only
- No Finding positive;
- zero target positives;
- only core skills;
- no finding skill;
- final narrative must not become "healthy/no disease."

### E2E04 — No Finding contradiction
- No Finding positive plus one target positive;
- contradiction preserved through doctor review;
- no automatic winner.

### E2E05 — Missing No Finding
- missing remains missing;
- no synthetic No Finding state.

### E2E06 — Nodule/Mass concern, no pathology
- malignancy concern supported/indeterminate per fixture;
- no cancer confirmation;
- doctor defers;
- final report preserves uncertainty.

### E2E07 — Pulmonary malignancy pathology confirmed
- pathology-confirmed disease preserved;
- no extra staging;
- doctor accepts;
- report preserves source-specific certainty.

### E2E08 — Pneumonia vs HF shared evidence
- shared dyspnea/opacity deduplicated;
- distinct evidence preserved;
- no winner/ranking.

### E2E09 — Pneumonia + HF coexistence
- independently supported processes;
- coexistence preserved;
- shared evidence not double-counted.

### E2E10 — AAS indeterminate, high review priority
- diagnostic certainty low/indeterminate;
- safety priority high;
- doctor acknowledges/defer;
- no autonomous CTA.

### E2E11 — AAS confirmed by definitive imaging
- definitive imaging state preserved;
- earlier CXR provenance retained;
- no treatment/surgery instruction.

### E2E12 — ILD single study
- no PPF progression;
- severity does not become progression.

### E2E13 — ILD valid serial progression
- valid temporal comparison;
- ILD module receives progression evidence;
- no hidden PPF shortcut.

### E2E14 — Pleural effusion vs HF/malignancy
- shared effusion evidence;
- no automatic MPE or cardiogenic attribution.

### E2E15 — Malignant pleural cytology
- MPE confirmation preserved;
- origin not invented.

### E2E16 — Pleural TB ADA only
- pleural TB concern bounded;
- no microbiologic confirmation.

### E2E17 — TB AFB positive only
- species unresolved;
- not M. tuberculosis confirmed.

### E2E18 — TB molecular/culture confirmation
- microbiologic confirmation preserved;
- site/provenance preserved;
- no treatment logic.

### E2E19 — TB vs malignancy separate lesions
- coexistence supported from independent evidence;
- no forced unifying diagnosis.

### E2E20 — Temporal nodule growth invalid due different lesion
- comparison rejected;
- no malignancy escalation from false growth.

### E2E21 — Recurrent pleural effusion
- presence → documented absence → presence;
- recurrence valid.

### E2E22 — AI class disappears but human says persists
- temporal conflict preserved;
- not resolved.

### E2E23 — Doctor rejects AI finding
- AI snapshot immutable;
- reviewed finding rejected;
- final report excludes affirmative item.

### E2E24 — Doctor modifies laterality/location
- final report uses doctor-authored refinement;
- AI provenance remains generic.

### E2E25 — Doctor adds missed finding
- doctor-added finding in review/final report;
- no retroactive skill selection;
- AI snapshot unchanged.

### E2E26 — Required high-priority item unacknowledged
- final-report candidate blocked.

### E2E27 — Stale doctor-review version
- final report fails closed with version mismatch.

### E2E28 — Snapshot mismatch after upstream rerun
- fail closed;
- do not silently use new AI/Hermes output.

### E2E29 — New evidence before finalization
- doctor review reopened;
- stale candidate invalidated.

### E2E30 — New evidence after finalization
- amendment required;
- old report immutable.

### E2E31 — Autonomous recommendation injection attempt
- detect and fail invariant;
- recommendation not rendered.

### E2E32 — Score-to-probability injection attempt
- detect and fail invariant.

### E2E33 — Missing lab treated as negative attempt
- detect and fail invariant.

### E2E34 — Duplicate opacity labels same process
- preserve labels;
- aggregate de-duplication.

### E2E35 — Raw AI directly to final report attempt
- blocked by doctor-review requirement.

### E2E36 — Full multi-module stress case
- multiple positive findings;
- temporal evidence;
- at least three disease hypotheses;
- arbitration;
- conflict;
- doctor modifications/defer;
- final candidate;
- all global invariants evaluated.

---

## Invariant engine

Suggested implementation:

```text
AI_model/tests/e2e/e2e_invariants.py
```

Each invariant should be an independently testable function.

Example signatures:

```python
check_provenance_preserved(trace)
check_missing_stays_unknown(trace)
check_no_score_to_probability(trace)
check_no_unsupported_diagnosis(trace)
check_overlap_not_double_counted(trace)
check_conflict_preserved(trace)
check_no_autonomous_action(trace)
check_doctor_review_required(trace)
check_no_auto_finalization(trace)
```

Avoid one monolithic boolean.

---

## Trace validator

Suggested:

```text
AI_model/tests/e2e/e2e_trace_validator.py
```

Validate:
- required stage ordering;
- unique stage ordinals;
- deterministic snapshot hashes;
- source IDs;
- execution mode;
- complete invariant results;
- no unexpected upstream mutation.

---

## Pipeline helper

Suggested:

```text
AI_model/tests/e2e/e2e_clinical_validation.py
```

Responsibilities:
- load golden case;
- call actual project components where available;
- inject declared fixtures;
- collect normalized stage outputs;
- build trace;
- evaluate invariants;
- return case result.

It must not contain new medical reasoning rules.

---

## Production-code boundary

Prefer using production/helper interfaces that already exist.

Do not duplicate clinical logic into the E2E harness.

If a frozen rule is only represented in test validators today:
- call/reuse the existing validator where possible;
- do not independently reimplement the medical rule in a divergent way.

---

## Provider-independent pass condition

A case passes only if:
- required stages execute/inject as declared;
- trace is complete;
- no unexpected mutation;
- all applicable invariants pass;
- expected final-report status matches;
- no prohibited field/action appears.

---

## Real-provider pass condition

A real-provider E2E case passes only if:
- infrastructure preflight passes;
- the model run completes;
- all applicable semantic invariants pass.

Skipped due missing provider:
- SKIPPED / BLOCKED infrastructure;
- never PASS.

---

## Failure reporting

For semantic failures, print:

```text
case_id
first_failing_stage
invariant
expected
observed
relevant_source_ids
```

Do not dump unrelated model chain-of-thought.

For infrastructure failures, print:
- provider/model readiness;
- pinned runtime check;
- error class;
- concise provider error.

---

## Regression boundary

Every E2E change must retain existing suites:
- seven Disease Analysis modules;
- Temporal;
- Arbitration;
- Structured Doctor Review;
- Final Report Generation;
- No Finding/selector/report;
- runtime integration;
- provider readiness.

Do not weaken module tests because the E2E harness disagrees.

---

## Release-gate use

The E2E harness may later become a release gate, but v1 should first establish deterministic semantics.

Suggested provider-independent gate:

```text
0 failed
all golden E2E cases passed
all global invariants passed
existing full regression passed
hard/schema 17/17
discovery 17
compileall PASS
git diff --check PASS
```

Real-provider readiness remains a separate gate.

---

## Hard prohibitions

The harness must never:
- alter clinical policy;
- write provider credentials;
- reconfigure Hermes;
- add tools;
- create clinical actions;
- auto-finalize reports;
- silently regenerate expected fixtures from actual outputs after failures;
- update golden expectations merely to match a regression.
