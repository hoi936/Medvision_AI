---
name: medvision-calcification
description: Evidence-grounded reasoning procedure for the VinBigData Calcification radiographic finding in MedVision Hermes. Uses location-first reasoning, separates image-plane localization from anatomical compartment, prevents automatic benign/TB/plaque/asbestos/vascular inference, distinguishes calcification from ossification, and integrates associated findings only when colocalization is supported.
---

# MedVision Calcification Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: calcification
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Calcification`

This skill does not establish benignity, malignancy exclusion, granuloma, tuberculosis, pleural plaque, asbestos exposure, pulmonary ossification, or cardiovascular calcification.

## Progressive disclosure

Before applying detailed evidence rules, load:

`skill_view("medvision-calcification", "references/references.md")`

When detailed localization, pulmonary-vs-pleural-vs-nodal reasoning, calcified-nodule patterns, calcification-vs-ossification, or overlap rules are required, load:

`skill_view("medvision-calcification", "references/CALCIFICATION_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Calcification` from CXR AI is **radiographic evidence of thoracic calcification**.

The first question is:

`WHERE IS IT?`

If anatomical location is unknown, keep it unknown and do not start a location-specific etiologic branch.

## Procedure

### Step 1 — Preserve upstream evidence

Record:
- canonical finding `Calcification`;
- model score;
- bounding box/image-plane localization if supplied;
- radiologist/manual interpretation if supplied;
- model/version.

Do not convert model score into disease probability.

### Step 2 — Separate bounding box from anatomical localization

A VinDr local finding may carry a bounding box [S1].

But:

`2D bbox != definitive anatomic structure`

Maintain:

```yaml
calcification_localization:
  status: unknown
  compartment: unknown
  structure: unknown
```

unless stronger evidence establishes anatomy.

### Step 3 — Localize before etiologic reasoning

Possible compartments include:
- pulmonary;
- pleural;
- nodal/mediastinal;
- chest wall;
- cardiac/vascular;
- other.

These are possibilities, not defaults [S3][S6].

Do not infer a compartment from the class name alone.

### Step 4 — Separate CXR from CT characterization

If CT is absent:
- exact structure may remain unknown;
- calcification pattern may remain unknown;
- intranodular/pleural/nodal status may remain unknown.

If CT explicitly characterizes calcium:
- preserve actual location/pattern.

`CROSS_SECTIONAL_CALCIFICATION_CHARACTERIZATION_RELEVANT` may be used when clinically appropriate.

Do not autonomously order CT.

### Step 5 — Nodule/Mass relationship

If `Nodule/Mass` is also positive:
- preserve both.

Do NOT call it a calcified nodule unless same-lesion relationship is supported.

If CT/radiology explicitly confirms intranodular calcification:
- record the pattern if supplied;
- use it as morphology evidence [S4];
- do not automatically declare the lesion benign;
- do not declare malignancy excluded.

When the two labels explicitly refer to the same lesion:
- `OVERLAPPING_FINDING_EVIDENCE` may prevent double counting.

### Step 6 — Pleural thickening relationship

If `Pleural thickening` is also positive:
- preserve both;
- do not infer pleural localization of calcium.

Only explicit pleural localization can support:
- pleural calcification;
- calcified plaque morphology.

Do not infer asbestos exposure from the two findings alone [S5].

### Step 7 — Pulmonary fibrosis relationship

If `Pulmonary fibrosis` is also positive:
- preserve both;
- do not automatically infer dystrophic pulmonary calcification;
- do not infer pulmonary ossification.

A shared process requires pulmonary localization and supporting context [S2].

### Step 8 — Calcification vs ossification

Pulmonary calcification and ossification are distinct [S2].

Never convert generic Calcification into pulmonary ossification.

### Step 9 — Metastatic vs dystrophic pulmonary calcification

Only consider:
- metastatic pulmonary calcification when pulmonary localization plus metabolic/hypercalcemic context is supplied;
- dystrophic pulmonary calcification when pulmonary localization plus local prior injury/scarring context is supplied.

Do not invent labs/history.

### Step 10 — Nodal/granulomatous branch

If CT explicitly shows calcified hilar/mediastinal nodes:
- record nodal localization.

Prior granulomatous infection may be a hypothesis if supporting history exists [S3].

Do not automatically diagnose:
- active TB;
- healed TB;
- sarcoidosis;
- silicosis.

### Step 11 — Cardiac/vascular guardrail

If Aortic enlargement or Cardiomegaly coexist:
- preserve findings independently;
- do not assign the calcium to aorta/coronaries/valves/pericardium without explicit localization.

### Step 12 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing evidence is not negative evidence.

### Step 13 — Conflict detection

If AI conflicts with trusted human review or CT:

emit:

`EVIDENCE_CONFLICT`

Preserve both.

CT may provide more-specific localization/morphology without erasing AI provenance.

### Step 14 — Safety

Generic Calcification alone is not automatically an emergency.

If an independent high-risk clinical syndrome exists:
- route according to that syndrome;
- emit `HIGH_PRIORITY_CLINICAL_REVIEW` where appropriate.

Do not issue autonomous imaging/procedure/treatment orders.

### Step 15 — Produce bounded assessment

Separate:
1. CXR calcification evidence;
2. image-plane localization;
3. anatomical compartment/structure;
4. CT morphology;
5. Nodule/Mass relationship;
6. Pleural thickening relationship;
7. Pulmonary fibrosis relationship;
8. nodal/granulomatous context;
9. metabolic context;
10. cardiac/vascular localization;
11. supporting/contradicting evidence;
12. missing evidence;
13. conflicts;
14. uncertainty;
15. clinician review;
16. citations.

## Evidence rules

### [S1] Dataset rule
Calcification is a local VinDr-CXR finding with bounding-box annotation; it remains separate from disease diagnoses.

### [S3][S6] Location-first rule
Thoracic calcification spans multiple compartments; location and pattern are essential to differential reasoning.

### [S2] Calcification/ossification rule
Pulmonary calcification and pulmonary ossification are distinct processes.

### [S2] Mechanism rule
Metastatic and dystrophic pulmonary calcification require appropriate pulmonary and clinical context.

### [S4] Calcified-nodule rule
Calcification patterns can help characterize a pulmonary nodule but calcification does not inherently exclude malignancy.

### [S5] Pleural-plaque rule
Pleural plaques may calcify, but generic calcification plus pleural thickening does not prove plaque or asbestos exposure.

## Output schema

```yaml
finding: calcification
finding_type: thoracic_radiographic_calcification

image_evidence:
  model_score: null
  bounding_box: unknown
  radiologist_interpretation: unknown

calcification_localization:
  status: unknown
  compartment: unknown
  structure: unknown
  source_modality: unknown

cross_sectional_characterization:
  available: false
  calcification_pattern: unknown
  intranodular: unknown
  pleural: unknown
  nodal: unknown
  cardiac_vascular: unknown
  associated_fibrosis_or_scarring: unknown
  ossification_reported: unknown

context:
  prior_granulomatous_disease: unknown
  active_infection_context: unknown
  asbestos_exposure: unknown
  metabolic_calcium_context: unknown
  malignancy_context: unknown
  prior_injury_or_therapy: unknown

overlap:
  nodule_mass: unknown
  pleural_thickening: unknown
  pulmonary_fibrosis: unknown
  aortic_enlargement: unknown
  cardiomegaly: unknown
  flags: []

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

1. Never equate Calcification with benignity.
2. Never use calcification to automatically exclude malignancy.
3. Never equate Calcification with tuberculosis.
4. Never equate Calcification with granuloma.
5. Never equate Calcification with hamartoma.
6. Never equate Calcification with pleural plaque.
7. Never equate Calcification with asbestos exposure.
8. Never equate Calcification with pulmonary ossification.
9. Never equate Calcification with cardiovascular calcification.
10. Never infer anatomical compartment from the positive class alone.
11. Never treat a 2D bounding box as definitive structure-of-origin proof.
12. Never infer calcified nodule from Calcification + Nodule/Mass without supported colocalization.
13. Never infer calcified pleural plaque from Calcification + Pleural thickening without pleural localization.
14. Never infer dystrophic pulmonary calcification from Calcification + Pulmonary fibrosis alone.
15. Never infer active TB from nodal calcification.
16. Never infer metastatic pulmonary calcification without pulmonary localization and metabolic context.
17. Never convert AI score into disease probability/calcium burden.
18. Never treat missing data as negative evidence.
19. Never issue autonomous imaging/procedure/treatment orders.
20. Always require clinician review.
21. Every medical rule must be traceable to references.
22. Preserve evidence conflicts and modality discordance.

## Not encoded in v1

Do not invent detailed rules for:
- coronary/aortic/valvular/pericardial calcium scoring;
- calcified-nodule follow-up;
- active TB diagnosis;
- asbestos occupational-disease diagnosis;
- metabolic calcification workup;
- biopsy decisions;
- treatment selection.

These require separate evidence/skills.
