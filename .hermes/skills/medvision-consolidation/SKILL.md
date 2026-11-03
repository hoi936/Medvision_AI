---
name: medvision-consolidation
description: Evidence-grounded clinical reasoning procedure for the VinBigData Consolidation radiographic finding in MedVision Hermes. Treats consolidation as a non-etiologic imaging descriptor, evaluates pneumonia, edema, hemorrhage and other hypotheses separately, checks missing/conflicting evidence and safety, and produces a bounded assessment for clinician review.
---

# MedVision Consolidation Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: consolidation
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Consolidation`

This skill does not establish a final etiologic diagnosis and does not prescribe treatment.

## Progressive disclosure

Before applying detailed medical rules, load:

`skill_view("medvision-consolidation", "references/references.md")`

When detailed differential boundaries, provenance or limitations are required, load:

`skill_view("medvision-consolidation", "references/CONSOLIDATION_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Consolidation` from the image AI is a **radiographic descriptor**.

It is NOT automatically:
- pneumonia;
- bacterial infection;
- pulmonary edema;
- pulmonary hemorrhage;
- malignancy;
- organizing pneumonia;
- indication for treatment.

## Procedure

### Step 1 — Preserve image evidence

Record:
- canonical finding;
- model score;
- localization/distribution if supplied;
- air bronchogram if supplied;
- radiologist/CT correlation if supplied;
- model/version when available.

Do not invent missing distribution or morphology.

Do not convert model score into disease probability without validated calibration.

### Step 2 — Evaluate temporal and clinical context

Look for:
- acute/subacute/chronic duration;
- fever;
- cough/sputum;
- dyspnea;
- hypoxemia;
- hemoptysis;
- cardiac/volume-overload context;
- inflammatory, malignant or other relevant history.

If not supplied, mark unknown/missing.

### Step 3 — Pneumonia branch

Evaluate pneumonia/infection as a separate etiologic hypothesis.

Compatible clinical, laboratory or microbiological evidence can increase support [S3].

Never output:
`Consolidation -> pneumonia confirmed`.

Never select antimicrobial treatment autonomously.

### Step 4 — Pulmonary edema branch

Consider edema only if the case has compatible imaging/clinical evidence [S4].

Do not equate consolidation with cardiogenic edema.

Do not issue autonomous diuretic or ventilatory treatment instructions.

### Step 5 — Pulmonary hemorrhage branch

Consider hemorrhage when compatible clinical/lab context exists [S5].

Absence of hemoptysis does not by itself exclude hemorrhage.

Do not diagnose diffuse pulmonary hemorrhage from imaging alone.

### Step 6 — Other etiologies

S2 supports a broad differential, especially when consolidation is chronic/persistent.

If evidence is insufficient:
`etiology: undetermined`

is valid.

Do not invent a specific inflammatory, neoplastic or other diagnosis without case evidence.

### Step 7 — Air bronchogram semantics

Air bronchogram can support morphology of consolidation [S1].

It does not establish cause.

Do not infer pneumonia solely from an air bronchogram.

### Step 8 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing information is never negative evidence.

### Step 9 — Conflict detection

If AI consolidation conflicts with trusted human review or later definitive imaging:

emit:

`EVIDENCE_CONFLICT`

Preserve both sources.

Do not silently prefer AI.

### Step 10 — Safety

If the case shows:
- significant hypoxemia;
- respiratory distress;
- physiological instability;
- strong concern for major pulmonary hemorrhage or another acute dangerous process;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do not issue autonomous treatment/procedure orders.

### Step 11 — Produce bounded assessment

Separate:
1. radiographic descriptor;
2. timing/distribution;
3. pneumonia/infection hypothesis;
4. pulmonary-edema hypothesis;
5. pulmonary-hemorrhage hypothesis;
6. other etiologic hypotheses;
7. supporting evidence;
8. contradictions/conflicts;
9. missing evidence;
10. safety;
11. uncertainty;
12. clinician review;
13. citations.

## Evidence rules

### [S1] Consolidation semantics
Consolidation is alveolar air replacement by fluid/other material and is a descriptor, not an etiologic diagnosis.

### [S2] Differential rule
Acute and chronic consolidations have broad and differing differential categories.

### [S3] Pneumonia rule
Pneumonia requires appropriate clinical/radiographic context; consolidation alone is insufficient.

### [S4] Edema rule
Pulmonary edema can produce airspace opacification/consolidation but requires compatible context.

### [S5] Hemorrhage rule
Pulmonary hemorrhage imaging is nonspecific and diagnosis requires integration with clinical/lab/pathologic evidence.

## Output schema

```yaml
finding: consolidation
finding_type: radiographic_descriptor

image_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  air_bronchogram: unknown

temporal_context:
  acute_subacute_chronic: unknown

etiologic_hypotheses:
  pneumonia_or_infection:
    status: unknown
    evidence: []
  pulmonary_edema:
    status: unknown
    evidence: []
  pulmonary_hemorrhage:
    status: unknown
    evidence: []
  inflammatory_or_organizing_process:
    status: unknown
    evidence: []
  neoplastic_or_other:
    status: unknown
    evidence: []

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

1. Never equate consolidation with pneumonia.
2. Never equate consolidation with bacterial infection.
3. Never infer pathogen from consolidation alone.
4. Never equate consolidation with cardiogenic pulmonary edema.
5. Never equate consolidation with pulmonary hemorrhage.
6. Never infer malignancy from consolidation alone.
7. Never infer etiology solely from an air bronchogram.
8. Never treat absence of fever/cough as contradiction of consolidation itself.
9. Never treat absence of hemoptysis as definitive exclusion of hemorrhage.
10. Never invent localization/distribution.
11. Never convert AI score into disease probability without validated calibration.
12. Never treat missing data as negative evidence.
13. Never issue autonomous treatment/procedure orders.
14. Always require clinician review.
15. Every medical rule must be traceable to references.
16. Preserve evidence conflicts rather than silently resolving them.

## Not encoded in v1

Do not invent detailed rules for:
- aspiration;
- pulmonary infarction;
- immunocompromised-host differential;
- persistent-consolidation malignancy algorithms;
- organizing-pneumonia treatment;
- pediatric consolidation;
- distribution-specific diagnostic algorithms.

These require additional evidence.
