# references.md — Silent / Prospective Clinical Evaluation v1

## S1 — DECIDE-AI (2022)

Vasey B, Nagendran M, Campbell B, et al.  
**Reporting guideline for the early-stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI.**  
Nature Medicine. 2022;28:924-933.  
DOI: 10.1038/s41591-022-01772-9

Source:
https://www.nature.com/articles/s41591-022-01772-9

### Used for
- Early-stage clinical evaluation should assess actual clinical performance at small scale, safety, human factors, and workflow.
- Users, setting, system version, errors, and modifications should be documented.
- In-silico performance alone is insufficient to demonstrate clinical benefit.

---

## S2 — SPIRIT-AI (2020)

Cruz Rivera S, Liu X, Chan A-W, et al.  
**Guidelines for clinical trial protocols for interventions involving artificial intelligence: the SPIRIT-AI Extension.**  
BMJ. 2020;370:m3210.  
DOI: 10.1136/bmj.m3210

Source:
https://www.bmj.com/content/370/bmj.m3210

### Used for
- Prospective protocols should explicitly describe intended use, intended users, integration into the clinical pathway, algorithm version, inputs/outputs, human-AI interaction, and error handling.
- Protocols should pre-specify how recommendations are acted upon and how input-data exclusions/failures are handled.
- AI system version must be frozen/documented for evaluation.

---

## S3 — CONSORT-AI (2020)

Liu X, Cruz Rivera S, Moher D, et al.  
**Reporting guidelines for clinical trial reports for interventions involving artificial intelligence: the CONSORT-AI Extension.**  
BMJ. 2020;370:m3164.  
DOI: 10.1136/bmj.m3164

Source:
https://www.bmj.com/content/370/bmj.m3164

### Used for
- Future interventional evaluation should report AI-specific trial details transparently.
- Results should distinguish intervention failures, user interaction, errors, and workflow integration.

---

## S4 — FDA Applying Human Factors and Usability Engineering to Medical Devices (August 2026)

U.S. Food and Drug Administration.  
**Applying Human Factors and Usability Engineering to Medical Devices.**  
Final Guidance. August 2026.

Source:
https://www.fda.gov/regulatory-information/search-fda-guidance-documents/applying-human-factors-and-usability-engineering-medical-devices

### Used for
- Evaluation should consider intended users, uses, use environments, and use-related hazards.
- User-interface design should reduce use errors that could contribute to harm.
- Live workflow evaluation must consider actual use context, not only software correctness.

### Scope note
Used as human-factors design guidance only; this is not a regulatory-classification or compliance claim.

---

## S5 — FDA / Health Canada / MHRA Transparency Principles for ML-Enabled Medical Devices

Source:
https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/transparency-machine-learning-enabled-medical-devices-guiding-principles

### Used for
- Human-AI team performance and workflow context are central.
- Intended users should receive clear information on intended use, performance, limitations, and logic/basis where appropriate.
- Transparency must be evaluated in the context of when and how information is presented.

---

## S6 — IMDRF Good Machine Learning Practice Guiding Principles (2025)

Source:
https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/good-machine-learning-practice-medical-device-development-guiding-principles

### Used for
- Evaluation should consider total-product-lifecycle performance.
- Human-AI team performance is a key concern.
- Real-world monitoring and management of changes should be planned.

---

## S7 — Existing MedVision frozen baseline

Current baseline before this phase:

```text
HUMAN-AI READER STUDY HARNESS: IMPLEMENTED
HUMAN-AI READER STUDY: NOT RUN

Current blockers:
- protocol not configured;
- independent dataset/reference standard missing;
- reader manifest missing;
- ethics/privacy determination unresolved;
- provider/frozen Hermes assistance missing.

Reader-study unit tests: 33 passed
Cross-layer regression: 162 passed
Full regression: 954 passed, 365 skipped

Discovery: 17
Hard validation: 17/17
Schema validation: 17/17

Hermes: v0.21.4
Commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
Python: 3.11.15
```

Silent/Prospective Clinical Evaluation v1 must not change frozen clinical semantics.
