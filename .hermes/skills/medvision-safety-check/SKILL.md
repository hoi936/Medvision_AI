---
name: medvision-safety-check
description: Check clinical urgency without autonomous disposition.
license: MIT
metadata:
  version: 0.1.0
  author: Phan Dinh Hoi (hoi936), Hermes Agent
  platforms: [linux, macos, windows]
  hermes:
    tags: [healthcare, safety, triage, human-oversight]
    related_skills: [medvision-evidence-fusion, medvision-disease-analysis]
---

# MedVision Safety Check Skill

Identify possible safety flags from supplied clinical state while keeping all
urgent assessment and disposition decisions with qualified professionals.

## When to Use

- Every MedVision clinical reasoning case before report generation.
- Cases containing symptoms, vital signs, or potentially urgent image findings.
- Do not use as an emergency alarm, triage service, or discharge tool.

## Procedure

1. Check supplied clinical evidence for severe or rapidly worsening dyspnea,
   severe hypoxemia, hemodynamic instability, altered consciousness, severe
   chest pain, or other explicit emergency features.
2. Evaluate image findings only in combination with clinical state. A high model
   score, conspicuous attention map, or pseudo box alone never creates an
   emergency alert.
3. Set safety status to `POSSIBLE_FLAG`, `NO_FLAG_IN_SUPPLIED_DATA`, or
   `CANNOT_ASSESS`. Name the exact evidence and missing data behind the status.
4. For `POSSIBLE_FLAG`, advise prompt direct assessment through an appropriate
   clinician/local emergency pathway without diagnosing the emergency or issuing
   autonomous treatment/disposition instructions.

## Pitfalls

- `No flag in supplied data` is not reassurance that no emergency exists.
- Do not invent thresholds, symptoms, examination findings, or vital signs.
- Do not make urgency depend solely on classification score or Grad-CAM.
- Do not prescribe medication, dose, treatment initiation, or discharge.

## Verification

- The safety status cites clinical evidence or explicitly says it cannot assess.
- Model evidence is contextual rather than the sole trigger.
- No autonomous diagnosis, order, treatment, or disposition appears.
