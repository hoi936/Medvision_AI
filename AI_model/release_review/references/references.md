# references.md — Release-Readiness & Safety Review v1

## S1 — NIST AI Risk Management Framework (AI RMF 1.0)

National Institute of Standards and Technology.  
**Artificial Intelligence Risk Management Framework (AI RMF 1.0).**  
Released January 2023; revision work ongoing as of 2026.

Official source:
https://www.nist.gov/itl/ai-risk-management-framework

### Used for
- Organizing AI risk management into Govern, Map, Measure, and Manage.
- Requiring explicit risk ownership, documentation, measurement, and response planning.
- Treating AI risk as socio-technical rather than only a model-performance issue.

### Scope note
The NIST AI RMF is voluntary guidance and is not a medical-device approval standard.

---

## S2 — NIST AI RMF Playbook

National Institute of Standards and Technology.  
**NIST AI RMF Playbook.**

Official source:
https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook

### Used for
- Translating Govern / Map / Measure / Manage outcomes into practical release-readiness checks.
- Structuring ownership, monitoring, escalation, documentation, and residual-risk review.

---

## S3 — IMDRF Good Machine Learning Practice for Medical Device Development (2025)

International Medical Device Regulators Forum.  
**Good machine learning practice for medical device development: Guiding principles.**  
IMDRF/AIML WG/N88 FINAL:2025.  
Published 29 January 2025.

Official source:
https://www.imdrf.org/documents/good-machine-learning-practice-medical-device-development-guiding-principles

### Used for
- Total-product-lifecycle thinking.
- Human-AI team performance.
- Fit-for-purpose datasets/evaluation.
- Monitoring of deployed model performance and retraining/change risks.
- Clear information about limitations and intended use.

---

## S4 — IMDRF Characterization Considerations for Medical Device Software and Software-Specific Risk (2025)

International Medical Device Regulators Forum.  
**Characterization Considerations for Medical Device Software and Software-Specific Risk.**  
IMDRF/SaMD WG/N81 FINAL:2025.  
Published 29 January 2025.

Official source:
https://www.imdrf.org/documents/characterization-considerations-medical-device-software-and-software-specific-risk

### Used for
- Intended-use characterization.
- Software-specific risk characterization.
- Linking product characterization to risk management and lifecycle activities.

---

## S5 — FDA Cybersecurity in Medical Devices (February 2026)

U.S. Food and Drug Administration.  
**Cybersecurity in Medical Devices: Quality Management System Considerations and Content of Premarket Submissions.**  
Final Guidance. February 2026.

Official source:
https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-quality-management-system-considerations-and-content-premarket

### Used for
- Cybersecurity risk management as a lifecycle concern.
- Threat modeling, vulnerability management, and resilience.
- Release-readiness consideration for systems that connect to networks or external services.

### Scope note
Used as a safety/security design reference only; this is not a claim that MedVision is subject to a specific FDA pathway.

---

## S6 — FDA AI-Enabled Device Software Functions: Lifecycle Management Draft Guidance (2025)

U.S. Food and Drug Administration.  
**Artificial Intelligence-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations.**  
Draft Guidance. January 2025.

Official source:
https://www.fda.gov/regulatory-information/search-fda-guidance-documents/artificial-intelligence-enabled-device-software-functions-lifecycle-management-and-marketing

### Used for
- Total-product-lifecycle management concepts.
- Documentation of model/system changes.
- Evaluation, transparency, bias, maintenance, and risk-management considerations.

### Scope note
This source is draft guidance and is not used as a binding requirement.

---

## S7 — Existing MedVision frozen baseline

Current project baseline before this phase:

```text
SILENT / PROSPECTIVE CLINICAL EVALUATION HARNESS: IMPLEMENTED
SILENT CLINICAL EVALUATION: NOT RUN
PROSPECTIVE INTERVENTIONAL EVALUATION: NOT RUN

Clinical-evaluation tests: 43 passed
Cross-layer deterministic tests: 190 passed
Runtime integration + provider-readiness: 15 passed
Full regression: 997 passed, 365 skipped

Discovery: 17
Hard validation: 17/17
Schema validation: 17/17

Hermes: v0.21.4
Commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
Python: 3.11.15
```

Current real-world blockers:
- actual silent protocol not configured;
- approved clinical data source absent;
- provider or frozen Hermes output set absent;
- ethics/privacy determination absent;
- security determination absent;
- prospective protocol/governance approval absent.

Release-Readiness & Safety Review v1 must preserve all frozen clinical semantics.
