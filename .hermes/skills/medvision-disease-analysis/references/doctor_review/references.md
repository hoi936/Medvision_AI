# references.md — Structured Doctor Review v1

## S1 — FDA Clinical Decision Support Software Guidance (January 2026)

U.S. Food and Drug Administration.  
**Clinical Decision Support Software: Guidance for Industry and Food and Drug Administration Staff.**  
Final Guidance. January 2026.  
URL: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software

### Used for
- The health-care professional should be able to independently review the basis for a CDS recommendation rather than rely primarily on the recommendation itself.
- Relevant patient-specific information, knowns/unknowns, required inputs, intended use, logic/methods, validation information and limitations should be available to support independent professional judgment.
- The clinician remains the decision-maker for the individual patient.

### Important scope note
MedVision analyzes chest radiographs, so whether any specific software function is or is not a regulated medical device cannot be inferred from the non-device CDS discussion alone. This source is used here for human-review and transparency design principles, not for a regulatory classification claim.

---

## S2 — FDA / Health Canada / MHRA Transparency for Machine Learning-Enabled Medical Devices

U.S. Food and Drug Administration.  
**Transparency for Machine Learning-Enabled Medical Devices: Guiding Principles.**  
URL: https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/transparency-machine-learning-enabled-medical-devices-guiding-principles

### Used for
- Human-AI workflow design should make intended use, limitations, relevant inputs, performance information, logic/basis and known gaps understandable to intended users.
- Transparency should support informed decisions, error detection, appropriate risk management and safe use.
- The human-AI team and workflow context are central design considerations.

---

## S3 — IMDRF Good Machine Learning Practice (GMLP) Guiding Principles (2025)

International Medical Device Regulators Forum.  
**Good Machine Learning Practice for Medical Device Development: Guiding Principles.**  
Final document, January 2025.  
FDA resource: https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/good-machine-learning-practice-medical-device-development-guiding-principles

### Used for
- Human-AI team performance is a design concern.
- Users should receive clear and essential information.
- Safe lifecycle design includes human factors, transparency and monitoring.

### Scope note
These are guiding principles, not a claim that MedVision is compliant with any specific regulatory pathway.

---

## S4 — IMDRF SaMD Clinical Evaluation (N41, 2017)

International Medical Device Regulators Forum.  
**Software as a Medical Device (SaMD): Clinical Evaluation.**  
IMDRF/SaMD WG/N41FINAL:2017.  
Published 21 September 2017.  
URL: https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation

### Used for
- Clinical use of software outputs depends on validated clinical association, analytical/technical performance and clinical performance.
- Human interpretation and intended clinical context remain important to safe software use.
- Clinical evaluation is distinct from merely producing an algorithmic output.

---

## S5 — Existing MedVision frozen architecture

Authoritative internal system rules:

```text
AI_RESULT
→ Hermes assessment
→ DRAFT_REPORT
→ DOCTOR_REVIEW
→ FINAL_REPORT
```

Frozen principles:
- `AI_RESULT`, `DOCTOR_REVIEW`, and `FINAL_REPORT` are separate.
- AI-result provenance is immutable.
- Missing stays missing.
- Conflicts are preserved.
- Doctor review is required.
- No autonomous treatment/procedure/disposition.
- Hermes cannot self-promote a draft into a final report.

These internal rules are authoritative for this module.

---

# MedVision internal review labels

```text
DOCTOR_REVIEW_PENDING
DOCTOR_REVIEW_IN_PROGRESS
DOCTOR_REVIEW_COMPLETED
DOCTOR_REVIEW_REOPENED

FINDING_ACCEPTED
FINDING_MODIFIED
FINDING_REJECTED
FINDING_DEFERRED
FINDING_UNREVIEWED

HYPOTHESIS_ACCEPTED
HYPOTHESIS_MODIFIED
HYPOTHESIS_REJECTED
HYPOTHESIS_DEFERRED
HYPOTHESIS_UNREVIEWED

REPORT_NOT_FINAL
REPORT_READY_FOR_FINALIZATION
REPORT_FINALIZED_BY_DOCTOR

REVIEW_ACKNOWLEDGED_HIGH_PRIORITY_ITEM
REVIEW_UNRESOLVED_ITEM
REVIEW_CONFLICT_PRESERVED
REVIEW_NEW_EVIDENCE_AFTER_FINALIZATION
```

These are MedVision workflow states, not formal regulatory terminology.
