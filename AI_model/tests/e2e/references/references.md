# references.md — End-to-End Clinical Validation Harness v1

## S1 — Existing MedVision frozen architecture

Authoritative internal workflow:

```text
image + clinical + labs
→ Hermes
→ assessment
→ draft report
→ doctor review
→ final
```

Frozen clinical reasoning order:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
```

Frozen invariants:
- AI finding = radiographic evidence, not disease diagnosis.
- Missing stays missing.
- Conflicts are preserved.
- AI score is not disease probability.
- `AI_RESULT`, `DOCTOR_REVIEW`, `FINAL_REPORT` remain separate.
- Doctor review is mandatory.
- No autonomous treatment/procedure/imaging/disposition.
- Finding skill selection occurs iff canonical AI `decision == "POSITIVE"`.
- Multiple positive findings route exactly once each, in payload order.
- `No finding` is a global 14-class taxonomy state, not a 15th finding skill.

These rules are the primary source of truth for this validation harness.

---

## S2 — Frozen Disease Analysis v2 modules

Provider-independent disease modules currently frozen:

1. Pneumonia / CAP
2. Heart Failure / Cardiogenic Congestion
3. Pulmonary Malignancy Concern
4. Acute Aortic Syndrome Concern
5. ILD / Fibrotic ILD / IPF / PPF
6. Pleural Disease / Pleural Malignancy
7. TB / Chronic Mycobacterial Thoracic Infection

Cross-cutting frozen modules:
8. Longitudinal / Temporal Reasoning
9. Cross-Disease Differential Arbitration
10. Structured Doctor Review
11. Final Report Generation

The end-to-end harness MUST validate integration without rewriting module semantics.

---

## S3 — Existing MedVision real-provider validation contract

Required real-provider invariants:

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
```

Failure classes:

```text
INFRASTRUCTURE_CONFIGURATION
INFRASTRUCTURE_TRANSIENT
CLINICAL_SEMANTIC_FAILURE
PASS
```

Rules:
- semantic failures are not retried merely until they pass;
- provider-unavailable cases are infrastructure failures, not clinical PASS/FAIL;
- the real suite remains gated by `RUN_HERMES_REAL=1`.

---

## S4 — Existing provider/runtime pin

Hermes under test remains:

```text
Hermes version: v0.21.4
Pinned commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
Runtime: .runtime/hermes-venv
HERMES_HOME: .runtime/hermes-home
```

The harness must fail closed if:
- the runtime is missing;
- the Hermes binary is outside the pinned runtime;
- provider configuration is required but absent.

---

## S5 — Existing final-report and doctor-review contracts

Final workflow:

```text
AI_RESULT
→ Hermes assessment
→ DRAFT_REPORT
→ DOCTOR_REVIEW
→ FINAL_REPORT
```

Key constraints:
- doctor review cannot mutate AI history;
- Hermes cannot self-finalize;
- report candidate must bind to the exact reviewed snapshot/version;
- new evidence after finalization requires amendment/new version rather than silent mutation;
- recommendations may only be doctor-authored or externally clinician-approved under host policy.

---

# MedVision internal E2E validation labels

```text
E2E_CASE_VALID
E2E_CASE_INVALID

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

E2E_INVARIANT_PASS
E2E_INVARIANT_FAIL

E2E_TRACE_COMPLETE
E2E_TRACE_INCOMPLETE
E2E_SNAPSHOT_MISMATCH
E2E_UNEXPECTED_STAGE_MUTATION
```

These are MedVision test-harness states, not clinical terminology.
