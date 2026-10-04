---
name: medvision-pleural-effusion
description: Evidence-grounded reasoning for the VinBigData Pleural Effusion radiographic finding in MedVision Hermes.
---

# MedVision Pleural Effusion Skill

## Purpose

Use this skill when MedVision receives the canonical VinBigData finding `Pleural effusion`.

This skill does not make a final etiologic diagnosis and does not prescribe treatment.

## MedVision Metadata

- Version: `1.0.0`
- Domain: `thoracic-radiology`
- Finding: `pleural_effusion`
- Doctor review required: `true`

## Progressive disclosure

Before applying detailed medical rules, load:

`skill_view("medvision-pleural-effusion", "references/references.md")`

When detailed thresholds, limitations, or provenance are needed, load:

`skill_view("medvision-pleural-effusion", "references/PLEURAL_EFFUSION_EVIDENCE.md")`

Do not invent medical facts outside these references.

## Core semantic rule

`Pleural effusion` from the image AI is a **radiographic finding**.

It is NOT automatically:
- heart failure;
- pleural infection;
- malignancy;
- tuberculosis;
- transudate/exudate;
- an indication for a procedure.

## Procedure

### 1. Preserve image evidence

Record finding name, model score, laterality/extent only if supplied, and model version when available.

Never reinterpret model score as patient disease probability without validated calibration.

### 2. Evaluate clinical context

Look for respiratory symptoms/physiology, cardiac context, infection context, malignancy history, TB context/risk, and other relevant history.

Missing information remains missing.

### 3. Evaluate laboratory evidence

If available, identify serum protein, serum LDH, serum NT-proBNP, pleural-fluid protein, LDH, pH, glucose, cytology, microbiology, and context-appropriate ADA/IFN-gamma.

Do not invent missing values.

### 4. Light criteria

Only calculate with required paired data.

`EXUDATIVE_BY_LIGHT_CRITERIA` if any of:
- PF protein / serum protein > 0.5
- PF LDH / serum LDH > 0.6
- PF LDH > 2/3 laboratory upper limit of normal serum LDH

Otherwise use `TRANSUDATIVE_BY_LIGHT_CRITERIA`.

This is a biochemical classification, not a final diagnosis [S4]. Preserve the known false-exudate limitation.

### 5. Build etiologic hypotheses

#### Heart failure
Use compatible clinical context and supportive serum NT-proBNP when available. NT-proBNP alone must not confirm the cause [S2].

#### Pleural infection
Use infection context plus pleural-fluid/imaging evidence. In suspected pleural infection, apply the BTS pH risk framework from S2. High-risk evidence may trigger `PLEURAL_INFECTION_HIGH_RISK`, but never an autonomous treatment order.

#### Malignancy
Use malignancy context and cytology/pathology if available. Negative cytology alone does not exclude malignancy [S2].

#### Tuberculosis
Use prevalence/context-appropriate evidence. Do not apply ADA as a universal standalone diagnostic rule [S2].

#### Other
If evidence is insufficient, `etiology: undetermined` is valid.

### 6. Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Absence of dyspnea or fever alone does not negate the radiographic finding.

### 7. Conflict detection

If AI evidence conflicts with trusted human review or later definitive imaging, emit `EVIDENCE_CONFLICT` and preserve both sources.

### 8. Safety

If the case reports significant respiratory compromise or physiological instability, emit `HIGH_PRIORITY_CLINICAL_REVIEW` (`MEDVISION_SYSTEM_POLICY`).

If suspected pleural infection has high-risk pleural-fluid evidence, emit `PLEURAL_INFECTION_HIGH_RISK` and require prompt clinician review.

Never autonomously order thoracentesis, drainage, antibiotics, IPC, pleurodesis, surgery, or anticancer therapy.

### 9. Bounded assessment

Separate:
1. radiographic finding;
2. biochemical classification if evaluable;
3. etiologic hypotheses;
4. supporting evidence;
5. contradictions/conflicts;
6. missing information;
7. safety flags;
8. uncertainty;
9. doctor review requirement;
10. citations.

## Output schema

```yaml
finding: pleural_effusion
finding_type: radiographic_finding
image_evidence:
  model_score: null
  laterality: unknown
  size_or_extent: unknown
clinical_context:
  symptoms: []
  physiologic_status: unknown
pleural_fluid:
  available: false
  light_criteria:
    evaluable: false
    classification: unknown
  infection_risk:
    evaluable: false
    status: unknown
etiologic_hypotheses:
  heart_failure: {status: unknown, evidence: []}
  infection: {status: unknown, evidence: []}
  malignancy: {status: unknown, evidence: []}
  tuberculosis: {status: unknown, evidence: []}
  other: {status: undetermined}
supporting_evidence: []
contradicting_evidence: []
missing_evidence: []
conflicts: []
safety:
  priority: routine
  flags: []
assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true
citations: []
```

## Hard constraints

1. Never turn the AI finding directly into an etiologic diagnosis.
2. Never equate pleural effusion with heart failure, infection, malignancy, or TB.
3. Never use NT-proBNP alone to confirm etiology.
4. Never compute Light criteria with incomplete paired data.
5. Never treat Light classification as a final disease diagnosis.
6. Never treat negative cytology as definitive exclusion of malignancy.
7. Never convert model score to patient disease probability without validated calibration.
8. Never treat missing data as negative evidence.
9. Never issue autonomous treatment/procedure orders.
10. Always require clinician review.
11. Every medical rule must be traceable to `references.md`.
12. If evidence is insufficient, say so.

## Not encoded in v1

Do not invent detailed rules for pediatric effusion, chylothorax, hemothorax, hepatic hydrothorax, renal-failure effusion, PE-associated effusion, detailed ultrasound phenotypes, or radiographic mimics.
