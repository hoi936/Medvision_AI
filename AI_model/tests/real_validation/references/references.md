# references.md — Provider-Backed End-to-End Clinical Validation v1

## S1 — IMDRF Good Machine Learning Practice (GMLP) Guiding Principles (2025)

International Medical Device Regulators Forum.  
**Good Machine Learning Practice for Medical Device Development: Guiding Principles.**  
Final document, January 2025.

FDA resource:
https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/good-machine-learning-practice-medical-device-development-guiding-principles

### Used for
- Validation must consider the total product lifecycle.
- Human-AI team performance is a design concern.
- Test datasets and evaluation methods should be fit for purpose.
- Users need clear information about limitations and performance.

### Scope note
This is used as an evaluation-design reference. It is not a claim that MedVision is a regulated device or is compliant with any regulatory framework.

---

## S2 — IMDRF SaMD Clinical Evaluation (N41, 2017)

International Medical Device Regulators Forum.  
**Software as a Medical Device (SaMD): Clinical Evaluation.**  
IMDRF/SaMD WG/N41FINAL:2017.  
Published 21 September 2017.

Official source:
https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation

### Used for
- Distinguishing technical/analytical validation from clinical validation.
- Clinical evaluation should address valid clinical association, analytical validation, and clinical validation/performance.
- A software output passing internal tests is not equivalent to demonstrated clinical utility.

---

## S3 — DECIDE-AI (2022)

Vasey B, Nagendran M, Campbell B, et al.  
**Reporting guideline for the early-stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI.**  
Nature Medicine. 2022;28:924-933.  
DOI: 10.1038/s41591-022-01772-9

Nature:
https://www.nature.com/articles/s41591-022-01772-9

BMJ companion publication:
https://www.bmj.com/content/377/bmj-2022-070904

### Used for
- AI clinical decision-support evaluation should assess not only model outputs but also safety, human factors, workflow, and interaction with clinical users.
- Early-stage evaluation should be explicit about users, environment, system version, errors, workflow integration, and modifications.
- Human-AI interaction is part of the intervention being evaluated.

### Scope note
DECIDE-AI is a reporting guideline for early live clinical evaluation; it does not by itself define a pass/fail test harness. MedVision uses its principles to shape future evaluation stages.

---

## S4 — FDA Clinical Decision Support Software Guidance (January 2026)

U.S. Food and Drug Administration.  
**Clinical Decision Support Software: Guidance for Industry and Food and Drug Administration Staff.**  
Final Guidance. January 2026.

Official source:
https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software

### Used for
- Clinicians should be able to independently review the basis of software recommendations.
- Patient-specific inputs, knowns/unknowns, logic/method basis, validation information, and limitations should support independent professional judgment.
- Provider-backed validation must not weaken MedVision's doctor-review boundary.

### Scope note
Because MedVision analyzes chest radiographs, this source is not used to make any regulatory-classification claim.

---

## S5 — FDA/Health Canada/MHRA Transparency Principles for ML-Enabled Medical Devices

Official FDA resource:
https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/transparency-machine-learning-enabled-medical-devices-guiding-principles

### Used for
- Evaluation should consider the human-AI team and the workflow context.
- Limitations and performance characteristics should be transparent to intended users.
- The evaluation record should preserve enough information to understand how the system behaved.

---

## S6 — Existing MedVision frozen provider/runtime contract

Hermes under test remains:

```text
Hermes version: v0.21.4
Pinned commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
Python: 3.11.15
HERMES_HOME: .runtime/hermes-home
Hermes binary: .runtime/hermes-venv/bin/hermes
```

Existing failure classes:

```text
INFRASTRUCTURE_CONFIGURATION
INFRASTRUCTURE_TRANSIENT
CLINICAL_SEMANTIC_FAILURE
PASS
```

Existing real-provider rule:

```text
RUN_HERMES_REAL=1
```

Real-provider tests must fail closed before inference when provider/model/credentials are not usable.

---

## S7 — Existing MedVision provider-independent E2E harness

Frozen E2E baseline:

```text
36 golden E2E cases
56 provider-independent E2E tests passed
12 deliberate-violation detections
E2E36 stress case: 16/16 invariants passed
Full regression: 863 passed, 355 skipped
Discovery: 17 enabled local skills
Hard validation: 17/17
Schema validation: 17/17
```

The provider-backed suite must reuse the same semantic invariants rather than define a second clinical policy.
