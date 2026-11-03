# E2E_CLINICAL_VALIDATION_EVIDENCE.md

## 0. Scope

Cross-cutting validation module for:

**End-to-End Clinical Validation Harness v1**

This harness validates the complete MedVision workflow using deterministic provider-independent fixtures plus a separately gated real-provider path.

Target pipeline:

```text
CASE_DATA
→ canonicalization
→ skill routing
→ evidence fusion
→ finding-specific reasoning
→ safety
→ disease analysis
→ temporal reasoning
→ cross-disease arbitration
→ draft report
→ doctor review fixture
→ final-report candidate
```

This harness is not:
- a new top-level Hermes skill;
- a disease module;
- a production inference engine;
- a hidden scoring system;
- a substitute for real-provider validation;
- a substitute for clinical evaluation on external datasets.

---

## 1. Primary purpose

Existing unit/module suites show that individual components respect their local rules.

The E2E harness must prove that those rules survive composition.

The central question is:

```text
When outputs from many frozen modules are chained together,
do the global semantic invariants still hold?
```

The harness therefore validates both:
1. stage-local outputs;
2. cross-stage invariants.

---

## 2. Required E2E stages

Each case trace should represent these stages when applicable:

```text
E2E_STAGE_INPUT
E2E_STAGE_ROUTING
E2E_STAGE_EVIDENCE_FUSION
E2E_STAGE_FINDING_SKILLS
E2E_STAGE_SAFETY
E2E_STAGE_DISEASE_ANALYSIS
E2E_STAGE_TEMPORAL_REASONING
E2E_STAGE_ARBITRATION
E2E_STAGE_DRAFT_REPORT
E2E_STAGE_DOCTOR_REVIEW
E2E_STAGE_FINAL_REPORT
```

A stage may be intentionally inactive if its progressive-loading trigger is not met.

Inactive is different from missing.

---

## 3. Canonical trace object

Recommended structure:

```yaml
case_trace:
  case_id: null
  case_version: 1

  input:
    case_data_snapshot: null
    snapshot_hash: null

  routing:
    canonical_positive_findings: []
    no_finding_state: null
    selected_skills: []
    selector_order: []

  evidence_fusion:
    evidence_objects: []
    conflicts: []
    missing_information: []

  finding_reasoning:
    outputs: []

  safety:
    priority: routine|elevated|high
    flags: []

  disease_analysis:
    module_outputs: []

  temporal:
    activated: false
    comparisons: []

  arbitration:
    activated: false
    hypotheses: []
    evidence_ledger: []
    relations: []

  draft_report:
    snapshot: null
    snapshot_hash: null

  doctor_review:
    fixture_id: null
    review_version: null
    decisions: []
    readiness: null

  final_report:
    candidate_status: null
    candidate_snapshot: null
    candidate_hash: null
    finalized: false

  stage_snapshots: []
  invariant_results: []
  failure_class: null
```

This is a test trace, not a production patient record.

---

## 4. Snapshot discipline

Every major stage should have a deterministic snapshot or normalized representation suitable for comparison.

Recommended metadata:

```yaml
stage_snapshot:
  stage: E2E_STAGE_DISEASE_ANALYSIS
  ordinal: 6
  source_ids: []
  normalized_payload: {}
  sha256: null
```

The test harness may use normalized JSON and SHA-256 to detect unintended mutation.

Do not use hashes as clinical evidence.

---

## 5. Immutability invariant

Upstream source snapshots must not be rewritten by later stages.

Examples:

```text
doctor rejects AI finding
→ AI_RESULT unchanged

final-report candidate rendered
→ doctor-review object unchanged

arbitration runs
→ disease-module historical output unchanged
```

Unexpected mutation:

`E2E_UNEXPECTED_STAGE_MUTATION`

---

## 6. Routing invariant

Canonical selector behavior remains:

```text
finding skill selected
iff
canonical AI decision == "POSITIVE"
```

Requirements:
- each positive canonical finding routes exactly once;
- order follows canonical payload order;
- `No finding` is never routed as a finding skill;
- external CT/doctor findings do not retroactively select original AI finding skills;
- score threshold must not be added.

---

## 7. No Finding invariant

E2E cases must preserve existing `No finding` state-machine semantics.

Examples:

```text
No finding POSITIVE + zero target positives
→ NO_FINDING_WITHIN_14_CLASS_TAXONOMY
```

```text
No finding POSITIVE + target positive(s)
→ NO_FINDING_CONTRADICTION
```

```text
No finding missing
→ NO_FINDING_MISSING
```

Downstream disease evidence from CT, pathology, microbiology, symptoms, labs, or doctor review must not silently rewrite the original CXR No Finding state.

---

## 8. Provenance invariant

Every clinically relevant downstream statement must remain traceable to one or more of:
- AI finding;
- clinical history/symptom;
- lab/physiology;
- CT/US/echo/other imaging;
- microbiology;
- pathology/cytology;
- clinician-authored review;
- temporal comparison;
- arbitration relation.

Doctor-added content must remain clinician-authored.

External characterization must not be rewritten as original AI prediction.

Required invariant:

`PROVENANCE_PRESERVED`

---

## 9. Missingness invariant

At every stage:

```text
missing input
→ unknown / missing
```

Never:

```text
missing
→ negative
```

or:

```text
missing
→ normal
```

Examples:
- no BNP != BNP normal;
- no culture != culture negative;
- no prior CT != stable lesion;
- no pathology != benign pathology;
- no reviewer timestamp != inferred timestamp.

Required invariant:

`MISSING_STAYS_UNKNOWN`

---

## 10. AI score invariant

Image-model scores remain model outputs.

No downstream stage may transform them into:
- disease probability;
- malignancy probability;
- TB probability;
- severity probability;
- ranking;
- treatment need.

Required invariant:

`NO_SCORE_TO_DISEASE_PROBABILITY`

---

## 11. Unsupported-diagnosis invariant

No disease diagnosis may appear downstream unless the owning frozen disease module permits that state from the supplied evidence.

Examples:
- Nodule/Mass != cancer;
- Pleural effusion != MPE;
- Aortic enlargement != dissection;
- Pulmonary fibrosis != IPF;
- AFB positive != M. tuberculosis confirmed;
- asbestos exposure != mesothelioma.

Required invariant:

`NO_UNSUPPORTED_DIAGNOSIS`

---

## 12. Unsupported-etiology invariant

Finding-level evidence must not acquire a cause that was not established.

Examples:
- effusion != HF automatically;
- consolidation != bacterial pneumonia automatically;
- fibrosis != prior TB;
- calcification != pleural plaque unless localized/characterized;
- opacity != edema unless supported.

Required invariant:

`NO_UNSUPPORTED_ETIOLOGY`

---

## 13. Overlap/de-duplication invariant

If multiple labels represent the same underlying abnormality/process:
- preserve original labels;
- de-duplicate aggregate reasoning;
- do not count as independent confirmations.

Required invariant:

`OVERLAP_NOT_DOUBLE_COUNTED`

This applies to:
- Consolidation / Lung Opacity / Infiltration;
- ILD / Pulmonary fibrosis when same process;
- repeated symptom copies;
- shared evidence across disease modules.

---

## 14. Conflict invariant

Trusted conflicts must survive downstream until:
- explicitly resolved by stronger/appropriate evidence; or
- explicitly resolved/preserved/deferred by doctor review.

Examples:
- No Finding contradiction;
- suspicious imaging + negative/nondiagnostic cytology;
- AI negative + human report positive;
- earlier NAAT negative + later culture positive;
- current AI says resolved + human says persistent.

Required invariant:

`CONFLICT_PRESERVED`

Do not remove conflict merely to create a clean final report.

---

## 15. Temporal invariant

Temporal states can appear only when temporal prerequisites are met.

Examples:

```text
no prior
→ PRIOR_DATA_MISSING
not NEW/STABLE
```

```text
different lesion
→ no growth claim
```

```text
present → absent → present
→ RECURRENT
```

```text
single severe HRCT
→ severity known
→ progression unknown
```

The final-report renderer may consume reviewed temporal state but must not recalculate it.

---

## 16. Arbitration invariant

Cross-disease arbitration must preserve:
- shared evidence;
- distinct evidence;
- competing hypotheses;
- coexistence;
- unresolved attribution.

It must not produce:
- winner;
- disease rank;
- hidden score;
- probability;
- top diagnosis.

A confirmed disease does not automatically erase a second independently supported process.

---

## 17. Safety invariant

If supplied evidence supports severe current risk under frozen safety rules:

`SAFETY_ESCALATION_WHEN_SUPPORTED`

Safety priority is independent of diagnostic certainty.

Example:

```text
AAS indeterminate
+ acute concerning syndrome
→ review priority may be high
```

but not:

```text
high priority
→ AAS confirmed
```

---

## 18. No autonomous action invariant

No downstream stage may invent:
- imaging orders;
- antibiotics;
- anti-TB therapy;
- biopsy;
- drainage;
- surgery;
- bronchoscopy;
- oncology treatment;
- follow-up interval;
- admission/disposition.

Doctor-authored recommendations may be rendered by Final Report Generation according to the frozen rule.

Required invariant:

`NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE`

---

## 19. Doctor-review invariant

Any path toward final-report rendering requires Structured Doctor Review.

Required invariant:

`DOCTOR_REVIEW_REQUIRED`

The harness must reject:

```text
raw AI
→ final report
```

and:

```text
Hermes draft
→ final report
```

without completed/readied doctor review.

---

## 20. Finalization invariant

Provider-independent E2E cases may produce:

```text
FINAL_REPORT_CANDIDATE_READY
FINAL_REPORT_RENDERED_FROM_REVIEW
```

but must not fabricate:

`FINAL_REPORT_FINALIZED_BY_DOCTOR`

unless the test fixture explicitly includes an external authenticated doctor-finalization event.

Default E2E fixtures should keep:

```yaml
finalized: false
```

---

## 21. Version-binding invariant

Final-report candidate must bind to:
- exact doctor-review ID/version;
- reviewed AI snapshot;
- reviewed Hermes snapshot;
- reviewed draft snapshot.

If any changed after review:

```text
FINAL_REPORT_VERSION_MISMATCH
or
FINAL_REPORT_SOURCE_MISMATCH
```

Fail closed.

---

## 22. Amendment invariant

If clinically relevant evidence arrives after finalization:
- old final report remains immutable;
- new review/report cycle is required;
- use `FINAL_REPORT_AMENDMENT_REQUIRED`.

Do not silently mutate old final content.

---

## 23. Provider-independent harness

The provider-independent harness should use actual deterministic project components wherever possible.

Preferred principle:

```text
real project code path
> copied logic in tests
```

However, it may use deterministic fixtures for stages that are intrinsically provider-backed.

Any fixture-injected stage must be explicitly marked:

```yaml
execution_mode: fixture
```

Actual executed stages:

```yaml
execution_mode: project_code
```

Do not present fixture simulation as real inference.

---

## 24. Real-provider harness

The real-provider E2E suite is separate.

It must:
- require `RUN_HERMES_REAL=1`;
- pass provider preflight before any model call;
- use pinned Hermes runtime;
- classify failures using existing taxonomy;
- never mark skipped infrastructure cases as PASS.

Real inference should evaluate the same global invariants as provider-independent E2E.

---

## 25. Failure classification

Use existing classes:

```text
INFRASTRUCTURE_CONFIGURATION
INFRASTRUCTURE_TRANSIENT
CLINICAL_SEMANTIC_FAILURE
PASS
```

Examples:

### Infrastructure configuration
- provider unset;
- model unset;
- credential missing;
- pinned runtime missing.

### Infrastructure transient
- provider timeout;
- transient network/provider service failure.

### Clinical semantic failure
- invented diagnosis;
- missing treated as negative;
- action invented;
- doctor review bypassed;
- provenance lost;
- conflict erased.

Do not retry semantic failures merely until the model passes.

---

## 26. Determinism

Provider-independent traces should be deterministic.

Given the same case fixture and repository version:
- stage ordering should be stable;
- normalized snapshots should be stable;
- invariant results should be stable.

Avoid:
- current wall-clock time in snapshots;
- random IDs;
- nondeterministic dictionary ordering;
- external network calls.

Use fixed fixture IDs/timestamps.

---

## 27. Recommended invariant result object

```yaml
invariant_result:
  invariant: PROVENANCE_PRESERVED
  status: pass|fail
  stage: E2E_STAGE_FINAL_REPORT
  evidence_refs: []
  message: ""
```

Every failing invariant should identify:
- first failing stage;
- relevant evidence/snapshot;
- expected rule;
- observed violation.

---

## 28. Recommended case result

```yaml
e2e_result:
  case_id: null
  status: pass|fail|blocked
  failure_class: null

  stages_executed: []
  stages_fixture_injected: []

  invariants:
    passed: []
    failed: []

  first_failure:
    stage: null
    invariant: null
    message: null

  trace_complete: true
```

---

## 29. Minimum required global invariants

Every E2E case should evaluate the applicable subset of:

```text
PROVENANCE_PRESERVED
MISSING_STAYS_UNKNOWN
NO_SCORE_TO_DISEASE_PROBABILITY
NO_UNSUPPORTED_ETIOLOGY
NO_UNSUPPORTED_DIAGNOSIS
OVERLAP_NOT_DOUBLE_COUNTED
CONFLICT_PRESERVED
SAFETY_ESCALATION_WHEN_SUPPORTED
NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE
DOCTOR_REVIEW_REQUIRED

TEMPORAL_STATE_VALID
ARBITRATION_NO_RANKING
DOCTOR_REVIEW_SNAPSHOT_IMMUTABLE
FINAL_REPORT_FROM_REVIEW_ONLY
FINAL_REPORT_VERSION_BOUND
NO_AUTO_FINALIZATION
```

---

## 30. Hard constraints

The E2E harness MUST NOT:

1. Create a new clinical reasoning rule merely to make a test pass.
2. Weaken a frozen module rule.
3. Change finding selector thresholds.
4. Change No Finding semantics.
5. Add disease ranking/probability.
6. Retry semantic failures until pass.
7. Count skipped provider tests as PASS.
8. Present fixture-injected outputs as real provider inference.
9. Mutate source snapshots.
10. Hide missing/conflicting evidence.
11. Allow raw AI/Hermes output to bypass doctor review.
12. Allow stale review/report versions to continue silently.
13. Auto-finalize a report.
14. Add autonomous treatment/procedure/recommendation logic.
15. Change Hermes runtime pin/provider configuration.
16. Add an 18th top-level skill.
