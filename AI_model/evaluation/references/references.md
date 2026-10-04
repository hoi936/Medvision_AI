# references.md — Clinical Dataset Evaluation v1

## S1 — IMDRF SaMD Clinical Evaluation (N41, 2017)

International Medical Device Regulators Forum.  
**Software as a Medical Device (SaMD): Clinical Evaluation.**  
IMDRF/SaMD WG/N41FINAL:2017.  
Published 21 September 2017.

Official source:
https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation

### Used for
- Distinguishing clinical association, analytical/technical validation, and clinical validation/performance.
- Internal software tests are not equivalent to demonstrated clinical performance.
- Evaluation should be linked to intended clinical use and evidence quality.

---

## S2 — IMDRF Good Machine Learning Practice Guiding Principles (2025)

International Medical Device Regulators Forum.  
**Good Machine Learning Practice for Medical Device Development: Guiding Principles.**  
Final document, January 2025.

FDA resource:
https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/good-machine-learning-practice-medical-device-development-guiding-principles

### Used for
- Fit-for-purpose datasets and evaluation methods.
- Human-AI team performance as an evaluation concern.
- Clear information about limitations and performance.
- Total-product-lifecycle thinking.

---

## S3 — DECIDE-AI (2022)

Vasey B, Nagendran M, Campbell B, et al.  
**Reporting guideline for the early-stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI.**  
Nature Medicine. 2022;28:924-933.  
DOI: 10.1038/s41591-022-01772-9

Source:
https://www.nature.com/articles/s41591-022-01772-9

### Used for
- Evaluation of AI decision-support systems should consider workflow, safety, users, and human-AI interaction, not only model output.
- System version, environment, modifications, errors, and user interaction should be reported.
- Early live clinical evaluation is a later stage than retrospective/in-silico dataset evaluation.

### Scope note
MedVision Dataset Evaluation v1 remains an offline/retrospective evaluation design unless a separate live clinical protocol is later approved.

---

## S4 — CLAIM 2024 Update

Radiological Society of North America.  
**Checklist for Artificial Intelligence in Medical Imaging (CLAIM): 2024 Update.**

RSNA resource:
https://pubs.rsna.org/page/ai/claim

### Used for
- Transparent reporting of imaging-AI datasets, partitions, reference standards, preprocessing, evaluation, and limitations.
- Dataset provenance and independent test-set reporting.
- Imaging-specific reporting discipline.

### Scope note
CLAIM is a reporting guideline, not a validation protocol and not a regulatory approval standard.

---

## S5 — TRIPOD+AI (2024)

Collins GS, Moons KGM, Dhiman P, et al.  
**TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods.**  
BMJ. 2024;385:e078378.

Source:
https://www.bmj.com/content/385/bmj-2023-078378

### Used for
- Transparent reporting of datasets, participants, outcomes, model evaluation, and external validation concepts.
- Pre-specification of analyses and clear separation of development versus evaluation data.

### Scope note
Hermes currently does not output calibrated disease probabilities. TRIPOD+AI is used only where its general evaluation/reporting concepts apply; probability calibration metrics are not automatically applicable.

---

## S6 — Existing MedVision frozen baseline

Current frozen baseline before this phase:

```text
Provider-backed harness: IMPLEMENTED
Real E2E validation: BLOCKED BY PROVIDER CONFIGURATION

Provider-backed unit tests: 19 passed
E2E provider-independent: 56 passed
Runtime integration: 6 passed
Real E2E cases when provider unavailable: 24 skipped

Full regression: 882 passed, 365 skipped
Discovery: 17 enabled local skills
Hard validation: 17/17
Schema validation: 17/17
Hermes: v0.21.4
Commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
Python: 3.11.15
```

This phase must not change the frozen clinical semantics.
