# references.md — Cross-Disease Differential Arbitration v1

## S1 — National Academies: Improving Diagnosis in Health Care (2015)

National Academies of Sciences, Engineering, and Medicine.  
**Improving Diagnosis in Health Care.**  
Washington, DC: The National Academies Press; 2015.  
DOI: 10.17226/21794  
URL: https://nap.nationalacademies.org/catalog/21794/improving-diagnosis-in-health-care

### Used for
- Diagnosis is an iterative information-integration process rather than a single isolated classification step.
- Diagnostic reasoning must account for uncertainty, evolving evidence, and communication of diagnostic uncertainty.
- New information can revise a diagnostic assessment without erasing the provenance of earlier evidence.

### Scope constraint
MedVision does not implement a human diagnostic-performance score or autonomous final diagnosis.

---

## S2 — Existing MedVision Disease Analysis v2 modules

Frozen modules are authoritative for disease-specific semantics:

1. Pneumonia / CAP
2. Heart Failure / Cardiogenic Congestion
3. Pulmonary Malignancy Concern
4. Acute Aortic Syndrome Concern
5. ILD / Fibrotic ILD / IPF / PPF
6. Pleural Disease / Pleural Malignancy
7. TB / Chronic Mycobacterial Infection
8. Longitudinal / Temporal Reasoning

### Used for
- Disease-specific support/confirmation boundaries.
- Modality-specific evidence hierarchy.
- Temporal/progression semantics.
- Pathology/microbiology confirmation rules.
- Safety escalation.
- Missing-data and provenance rules.

The arbitration layer MUST NOT override a frozen module's disease-specific rule.

---

## S3 — Existing MedVision Knowledge Track v1

Authoritative upstream rules:

- radiographic finding != disease diagnosis;
- AI score != patient-level disease probability;
- missing stays missing;
- conflicts are preserved;
- `AI_RESULT`, `DOCTOR_REVIEW`, `FINAL_REPORT` remain separate;
- no autonomous treatment/procedure;
- doctor review required.

### Used for
- Evidence attribution.
- De-duplication.
- No Finding semantics.
- Provenance preservation.
- Action boundaries.

---

# MedVision internal arbitration labels

These are system-policy labels, not formal guideline terminology.

```text
HYPOTHESIS_SUPPORTED
HYPOTHESIS_POSSIBLE
HYPOTHESIS_INDETERMINATE
HYPOTHESIS_CONFLICTED
HYPOTHESIS_NOT_ESTABLISHED

COMPETING_HYPOTHESES_PRESENT
COEXISTING_PROCESSES_POSSIBLE
COEXISTING_PROCESSES_SUPPORTED
MUTUAL_EXCLUSIVITY_NOT_ESTABLISHED

SHARED_EVIDENCE_PRESENT
DISTINCT_EVIDENCE_PRESENT
EVIDENCE_ATTRIBUTION_UNRESOLVED
DUPLICATE_EVIDENCE_DEDUPLICATED

REVIEW_PRIORITY_ROUTINE
REVIEW_PRIORITY_ELEVATED
REVIEW_PRIORITY_HIGH
```

`REVIEW_PRIORITY_*` is a review/safety workflow state. It MUST NOT be interpreted as disease probability or diagnostic ranking.
