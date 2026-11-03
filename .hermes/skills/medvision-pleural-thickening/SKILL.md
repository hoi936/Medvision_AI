---
name: medvision-pleural-thickening
description: Evidence-grounded reasoning procedure for the VinBigData Pleural thickening radiographic finding in MedVision Hermes. Treats the CXR output as a local pleural abnormality, separates CXR from cross-sectional pleural morphology, prevents automatic asbestos/TB/malignancy inference, integrates pleural effusion and pulmonary fibrosis conservatively, and produces a bounded assessment for clinician review.
---

# MedVision Pleural Thickening Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: pleural_thickening
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Pleural thickening`

This skill does not establish asbestos exposure, pleural plaque, asbestosis, mesothelioma, metastasis, tuberculosis, empyema, or another specific etiology.

## Progressive disclosure

Before applying detailed evidence rules, load:

`skill_view("medvision-pleural-thickening", "references/references.md")`

When detailed pleural morphology, asbestos, plaque, malignancy, or overlap boundaries are required, load:

`skill_view("medvision-pleural-thickening", "references/PLEURAL_THICKENING_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Pleural thickening` from CXR AI is **radiographic evidence of a pleural abnormality/thickening**.

It is NOT automatically:
- asbestos exposure;
- pleural plaque;
- asbestosis;
- mesothelioma;
- pleural metastasis;
- tuberculosis;
- empyema.

## Procedure

### Step 1 — Preserve CXR evidence

Record:
- canonical finding;
- model score;
- side/distribution if supplied;
- radiologist/manual interpretation if supplied;
- model/version.

Do not infer cross-sectional morphology from the class.

Do not convert model score into disease probability.

### Step 2 — Characterize only what is supplied

If available, record:
- unilateral/bilateral;
- focal/multifocal/diffuse;
- smooth/irregular/nodular;
- circumferential involvement;
- mediastinal pleural involvement;
- calcification;
- associated effusion;
- prior imaging change.

Do not invent any of these.

### Step 3 — Separate CXR from CT/MRI/PET

If cross-sectional imaging is absent:
- morphology remains incompletely characterized;
- pleural plaque status remains unknown;
- malignant pleural morphology remains unknown.

When clinically appropriate:

`PLEURAL_CROSS_SECTIONAL_CHARACTERIZATION_RELEVANT`

may be a clinician-facing consideration.

Do not autonomously order imaging.

### Step 4 — Pleural plaque guardrail

Pleural plaques and diffuse pleural thickening are not interchangeable [S5][S6].

Never infer:

`Pleural thickening -> pleural plaque`

If CT explicitly reports plaque:
- record it separately;
- retain the CXR finding.

### Step 5 — Asbestos guardrail

Do not infer asbestos exposure from pleural thickening.

If documented exposure exists:
- asbestos-related pleural disease may become a hypothesis;
- do not automatically diagnose asbestosis.

Keep:
- exposure evidence;
- pleural imaging;
- parenchymal fibrosis

as separate evidence objects.

### Step 6 — Malignancy guardrail

If CT/MRI provides suspicious pleural morphology:
- malignant pleural disease concern may increase [S3][S4].

Do not automatically diagnose:
- mesothelioma;
- pleural metastasis.

Pathology/clinical diagnosis remains separate.

No numeric malignancy score is encoded.

### Step 7 — Pleural effusion relationship

If `Pleural effusion` is also positive:
- preserve both;
- use the Pleural Effusion skill for fluid-specific reasoning;
- do not infer malignancy/TB/empyema from co-occurrence alone.

### Step 8 — Pulmonary fibrosis relationship

If `Pulmonary fibrosis` is also positive:
- preserve both;
- do not infer asbestosis or occupational exposure.

Only documented exposure and appropriate broader evidence may support an asbestos-related hypothesis.

### Step 9 — Calcification relationship

If a generic `Calcification` finding later coexists:
- preserve both;
- do not infer pleural localization.

Only explicit CT/radiology localization can connect calcification to pleura or plaque morphology.

### Step 10 — Infection/TB guardrail

Pleural thickening is nonspecific.

Use infection/TB evidence only if supplied:
- symptoms;
- microbiology;
- fluid studies;
- history;
- cross-sectional morphology.

Do not diagnose TB/empyema from thickening alone.

### Step 11 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing evidence is not negative evidence.

### Step 12 — Conflict detection

If AI conflicts with trusted human review or CT:

emit:

`EVIDENCE_CONFLICT`

Preserve both.

Use CT as more-specific morphology evidence without erasing the upstream AI result.

### Step 13 — Safety

Pleural thickening alone is not automatically an emergency.

If independent evidence shows severe respiratory compromise, major instability, or another acute high-risk pleural syndrome:

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous imaging/procedure/treatment orders.

### Step 14 — Produce bounded assessment

Separate:
1. CXR pleural-thickening evidence;
2. cross-sectional morphology;
3. plaque status;
4. asbestos exposure/context;
5. malignant pleural disease concern;
6. infection/TB context;
7. pleural-effusion relationship;
8. pulmonary-fibrosis relationship;
9. calcification localization;
10. supporting/contradicting evidence;
11. missing evidence;
12. conflicts;
13. safety;
14. uncertainty;
15. clinician review;
16. citations.

## Evidence rules

### [S3] Morphology rule
Pleural thickening can be unilateral/bilateral and focal/multifocal/diffuse; the differential is broad.

### [S5][S6] Plaque rule
Pleural plaques and diffuse pleural thickening are distinct; focal thickening has multiple mimics.

### [S6] Asbestos rule
Asbestos-related diffuse pleural thickening requires an asbestos-exposure context; pleural thickening alone does not establish exposure.

### [S3][S4] Malignancy rule
Suspicious pleural morphology may raise concern but does not replace pathology/clinical diagnosis.

### [S2] Dataset rule
The upstream result remains an imaging finding, not an etiologic diagnosis.

## Output schema

```yaml
finding: pleural_thickening
finding_type: radiographic_pleural_finding

cxr_evidence:
  model_score: null
  side: unknown
  distribution: unknown
  radiologist_interpretation: unknown

cross_sectional_characterization:
  available: false
  modality: unknown
  focality: unknown
  surface: unknown
  nodularity: unknown
  circumferential_involvement: unknown
  mediastinal_pleural_involvement: unknown
  calcification: unknown
  plaque_morphology: unknown
  associated_effusion: unknown

etiology_context:
  asbestos_exposure: unknown
  tuberculosis_or_infection_context: unknown
  malignancy_context: unknown
  other: []

pleural_disease_hypotheses:
  asbestos_related_pleural_disease:
    status: unknown
    evidence: []
  malignant_pleural_disease:
    status: unknown
    evidence: []
  infectious_inflammatory_pleural_disease:
    status: unknown
    evidence: []

overlap:
  pleural_effusion: unknown
  pulmonary_fibrosis: unknown
  calcification: unknown
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

1. Never equate Pleural thickening with asbestos exposure.
2. Never equate Pleural thickening with pleural plaque.
3. Never equate Pleural thickening with asbestosis.
4. Never equate Pleural thickening with mesothelioma.
5. Never equate Pleural thickening with pleural metastasis.
6. Never equate Pleural thickening with tuberculosis.
7. Never equate Pleural thickening with empyema.
8. Never infer CT morphology from CXR thickening alone.
9. Never infer pleural calcification from an unlocalized Calcification finding.
10. Never infer asbestosis from Pleural thickening + Pulmonary fibrosis alone.
11. Never infer malignancy from Pleural thickening + Pleural effusion alone.
12. Never treat suspicious imaging morphology as pathology confirmation.
13. Never invent a numeric pleural-malignancy probability.
14. Never convert AI score into disease probability.
15. Never treat missing data as negative evidence.
16. Never issue autonomous imaging/procedure/treatment orders.
17. Always require clinician review.
18. Every medical rule must be traceable to references.
19. Preserve direct evidence conflicts and modality discordance.

## Not encoded in v1

Do not invent detailed rules for:
- mesothelioma diagnosis/staging;
- asbestos exposure reconstruction;
- pleural-plaque disease classification;
- TB pleuritis;
- chronic empyema;
- PET interpretation;
- biopsy/thoracoscopy selection;
- treatment.

These require separate evidence.
