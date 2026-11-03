# references.md — Human-AI Reader Study / Clinician Evaluation v1

## S1 — DECIDE-AI (2022)

Vasey B, Nagendran M, Campbell B, et al.  
**Reporting guideline for the early-stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI.**  
Nature Medicine. 2022;28:924-933.  
DOI: 10.1038/s41591-022-01772-9

Source:
https://www.nature.com/articles/s41591-022-01772-9

### Used for
- Human-AI interaction is part of the intervention being evaluated.
- Early-stage evaluation should report users, environment, workflow, system version, errors, and modifications.
- Clinical value cannot be inferred from in-silico model performance alone.
- Safety and human factors must be evaluated alongside performance.

---

## S2 — Multireader Diagnostic Accuracy Imaging Studies: Fundamentals of Design and Analysis (Radiology, 2022)

Obuchowski NA, Bullen JA, et al.  
**Multireader Diagnostic Accuracy Imaging Studies: Fundamentals of Design and Analysis.**  
Radiology. 2022.

Source:
https://pubs.rsna.org/doi/10.1148/radiol.211593

### Used for
- Multireader multicase (MRMC) studies require sampling from both reader and case populations.
- Paired/fully crossed designs are generally preferred when feasible for comparing aided versus unaided interpretation.
- Reader and case correlations must be accounted for statistically.
- Reader training, case randomization, blinding, washout, and reference-standard quality are important design considerations.
- Reader experience should represent the intended user population.

### Important note
The paper discusses a practical minimum of five readers for MRMC diagnostic-accuracy studies, but MedVision must not treat five readers as universally sufficient. Final reader/case sample size must be justified for the selected endpoints and study design.

---

## S3 — FDA Clinical Performance Assessment for Computer-Assisted Detection Devices (2022)

U.S. Food and Drug Administration.  
**Clinical Performance Assessment: Considerations for Computer-Assisted Detection Devices Applied to Radiology Images and Radiology Device Data in Premarket Notification (510(k)) Submissions.**  
Final Guidance. September 2022.

Source:
https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-performance-assessment-considerations-computer-assisted-detection-devices-applied-radiology

### Used for
- Reader-performance studies can be appropriate for evaluating computer-assisted imaging systems.
- Clinical performance assessment should match the intended mode of use.
- Study design and reference standards should be appropriate to the radiology task.

### Scope note
MedVision is not being classified here as CADe or any particular FDA device type. The source is used for reader-study design principles only.

---

## S4 — FDA Applying Human Factors and Usability Engineering to Medical Devices (August 2026)

U.S. Food and Drug Administration.  
**Applying Human Factors and Usability Engineering to Medical Devices.**  
Final Guidance. August 2026.

Source:
https://www.fda.gov/regulatory-information/search-fda-guidance-documents/applying-human-factors-and-usability-engineering-medical-devices

### Used for
- Evaluation should consider intended users, uses, use environments, and user-interface interactions.
- Use errors that could cause harm or degrade care should be identified and reduced.
- Human-factors testing should evaluate the interface and workflow, not only algorithm correctness.

### Scope note
This is used as a human-factors design reference, not as a regulatory-compliance claim.

---

## S5 — FDA / Health Canada / MHRA Transparency for ML-Enabled Medical Devices

Official FDA source:
https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/transparency-machine-learning-enabled-medical-devices-guiding-principles

### Used for
- Human-AI team performance is a design concern.
- Intended users need clear information about intended use, performance, limitations, and known gaps.
- Transparency should be evaluated in the real workflow context.
- Human-centered design should consider where and when information is presented.

---

## S6 — CONSORT-AI and SPIRIT-AI (2020)

Liu X, Cruz Rivera S, Moher D, et al.  
**CONSORT-AI Extension.** BMJ. 2020;370:m3164.  
https://www.bmj.com/content/370/bmj.m3164

Cruz Rivera S, Liu X, Chan A-W, et al.  
**SPIRIT-AI Extension.** BMJ. 2020;370:m3210.  
https://www.bmj.com/content/370/bmj.m3210

### Used for
- Future prospective/interventional protocol and reporting design.
- Explicit description of AI intervention, users, inputs/outputs, errors, and interaction with clinical workflow.

### Scope note
Human-AI Reader Study v1 is designed as an offline/retrospective reader-study scaffold, not a randomized clinical trial.

---

## S7 — Existing MedVision frozen baseline

Current baseline before this phase:

```text
Clinical Dataset Evaluation Harness: IMPLEMENTED
Clinical Dataset Evaluation: NOT RUN
Reason: independent evaluation dataset not configured

Evaluation unit tests: 39 passed
Provider-backed/E2E/runtime/readiness regression: 90 passed
Full regression: 921 passed, 365 skipped

Discovery: 17
Hard validation: 17/17
Schema validation: 17/17

Hermes: v0.21.4
Commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
Python: 3.11.15
```

Human-AI Reader Study v1 must not change the frozen clinical semantics.
