---
name: medvision-pulmonary-fibrosis
description: Evidence-grounded reasoning procedure for the VinBigData Pulmonary fibrosis radiographic finding in MedVision Hermes. Treats the CXR output as local fibrotic/scarring evidence, separates CXR from HRCT fibrosis characterization, prevents automatic UIP/IPF/PPF inference, deduplicates overlap with ILD and broad opacity labels, and produces a bounded assessment for clinician review.
---

# MedVision Pulmonary Fibrosis Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: pulmonary_fibrosis
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Pulmonary fibrosis`

This skill does not establish IPF, UIP, PPF, a specific ILD subtype, or a specific fibrosis etiology.

## Progressive disclosure

Before applying detailed evidence rules, load:

`skill_view("medvision-pulmonary-fibrosis", "references/references.md")`

When detailed HRCT morphology, UIP/IPF, PPF, overlap, or etiology boundaries are required, load:

`skill_view("medvision-pulmonary-fibrosis", "references/PULMONARY_FIBROSIS_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Pulmonary fibrosis` from CXR AI is **local radiographic evidence compatible with chronic fibrotic/scarring change**.

It is NOT automatically:
- IPF;
- UIP;
- PPF;
- CTD-ILD;
- hypersensitivity pneumonitis;
- occupational fibrosis;
- post-infectious fibrosis;
- another specific cause.

## Procedure

### Step 1 — Preserve CXR provenance

Record:
- canonical finding `Pulmonary fibrosis`;
- model score;
- localization/distribution if supplied;
- radiologist/manual interpretation if supplied;
- model/version.

Do not convert the model score into disease probability.

### Step 2 — Separate finding from diagnosis

`Pulmonary fibrosis` is a local VinDr-CXR label [S2].

Keep it separate from:
- IPF;
- disease subtype;
- etiology.

### Step 3 — Check ILD overlap

If `ILD` is also positive:
- preserve both upstream results;
- fibrosis can refine fibrosis status in the broader ILD context;
- emit `OVERLAPPING_FINDING_EVIDENCE` when appropriate;
- do not count the two labels as independent confirmation of IPF.

### Step 4 — Separate CXR from HRCT

If no HRCT exists:
- do not invent honeycombing;
- do not invent traction bronchiectasis;
- do not invent traction bronchiolectasis;
- do not invent UIP;
- do not invent fibrosis extent.

If fibrotic ILD context genuinely requires characterization:

`HRCT_CHARACTERIZATION_RELEVANT`

may be a clinician-facing consideration.

Do not autonomously order HRCT.

### Step 5 — Preserve actual HRCT fibrotic morphology

If explicitly supplied, record:
- reticulation;
- traction bronchiectasis;
- traction bronchiolectasis;
- honeycombing;
- architectural distortion;
- volume loss;
- GGO;
- distribution;
- reported pattern.

These are CT morphology, not CXR inferences [S1][S4][S5].

### Step 6 — UIP / IPF guardrail

If HRCT explicitly reports UIP/probable-UIP:
- preserve the imaging pattern;
- do not automatically diagnose IPF [S3].

Keep:
- HRCT pattern;
- clinical diagnosis;
- diagnostic confidence

as separate fields.

### Step 7 — Etiology guardrail

Use cause-related evidence only if supplied:
- CTD/autoimmune;
- exposure;
- medication/radiation;
- infection history;
- family/genetic;
- pathology/MDD.

Otherwise:

`etiology: unknown`

Do not infer cause from fibrosis alone.

### Step 8 — PPF evaluability

PPF is evaluated only in the proper non-IPF ILD context with radiological fibrosis and >=2 of:
- worsening respiratory symptoms;
- physiological progression;
- radiological progression

within one year and with no alternative explanation [S3].

If longitudinal evidence is insufficient:

`ppf_evaluable: false`

Do not infer progression from one study.

### Step 9 — Other overlap handling

If coexisting:
- Lung Opacity;
- Infiltration;
- ILD;

preserve all upstream results.

When they plausibly reflect the same process:
- emit `OVERLAPPING_FINDING_EVIDENCE`;
- avoid double/triple counting;
- use fibrosis as the more-specific chronic fibrotic descriptor where appropriate.

### Step 10 — Consolidation relationship

If Consolidation coexists:
- preserve both;
- do not infer acute exacerbation automatically.

### Step 11 — Pleural thickening relationship

If Pleural thickening coexists:
- preserve both;
- do not infer asbestos exposure/asbestosis/occupational etiology without independent evidence.

### Step 12 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing evidence is not negative evidence.

### Step 13 — Conflict detection

If AI conflicts with trusted human CXR review or high-quality HRCT:

emit:

`EVIDENCE_CONFLICT`

Preserve both.

Treat HRCT as more specific for fibrosis characterization but do not erase the original AI result.

### Step 14 — Safety

Pulmonary fibrosis alone is not automatically an emergency.

If independent evidence shows:
- severe/new respiratory distress;
- major hypoxemia;
- rapid physiological deterioration;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous imaging/procedure/treatment orders.

### Step 15 — Produce bounded assessment

Separate:
1. CXR fibrosis finding;
2. ILD overlap;
3. HRCT morphology;
4. reported fibrotic pattern;
5. UIP/IPF status;
6. etiology hypothesis;
7. PPF evaluability;
8. other overlap/de-duplication flags;
9. supporting/contradicting evidence;
10. missing evidence;
11. conflicts;
12. safety;
13. uncertainty;
14. clinician review;
15. citations.

## Evidence rules

### [S2] Dataset rule
Pulmonary fibrosis and ILD are distinct local VinDr-CXR finding labels.

### [S4][S5] HRCT morphology rule
Reticulation, traction bronchiectasis/bronchiolectasis, honeycombing, architectural distortion and volume loss belong to HRCT fibrosis characterization.

### [S3] UIP/IPF rule
UIP is an imaging/histopathologic pattern in IPF evaluation; fibrosis finding alone is not IPF.

### [S3] PPF rule
PPF requires adequate longitudinal non-IPF ILD context and >=2 of 3 progression domains within one year with no alternative explanation.

### [S6] Classification rule
Interstitial disorders include fibrotic and non-fibrotic categories and multiple idiopathic/secondary causes.

## Output schema

```yaml
finding: pulmonary_fibrosis
finding_type: radiographic_fibrotic_finding

cxr_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  radiologist_interpretation: unknown

hrct_characterization:
  available: false
  reticulation: unknown
  traction_bronchiectasis: unknown
  traction_bronchiolectasis: unknown
  honeycombing: unknown
  architectural_distortion: unknown
  volume_loss: unknown
  ground_glass_opacity: unknown
  distribution: unknown
  reported_pattern: unknown

fibrotic_context:
  fibrosis_supported: true
  ild_context: unknown
  uip_pattern: unknown
  ipf_status: unknown
  etiology: unknown
  diagnostic_confidence: unknown

progression:
  ppf_evaluable: false
  worsening_symptoms: unknown
  physiological_progression: unknown
  radiological_progression: unknown
  alternative_explanation_assessed: unknown

overlap:
  detected: false
  flags: []
  notes: []

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

1. Never equate Pulmonary fibrosis with IPF.
2. Never equate Pulmonary fibrosis with UIP.
3. Never equate Pulmonary fibrosis with PPF.
4. Never infer a specific ILD subtype from the CXR fibrosis label.
5. Never infer a specific fibrosis etiology from the CXR label.
6. Never infer honeycombing from CXR fibrosis.
7. Never infer traction bronchiectasis/bronchiolectasis from CXR fibrosis.
8. Never infer a specific HRCT pattern from the CXR class.
9. Never equate UIP imaging pattern with IPF automatically.
10. Never diagnose PPF from one study.
11. Never diagnose PPF without adequate longitudinal criteria.
12. Never double count ILD + Pulmonary fibrosis as independent disease confirmation.
13. Never triple count fibrosis with Lung Opacity/Infiltration.
14. Never infer acute exacerbation from fibrosis + Consolidation alone.
15. Never infer occupational disease from fibrosis + Pleural thickening alone.
16. Never invent exposure, CTD, PFT, pathology or family-history evidence.
17. Never convert AI score into IPF/fibrotic-ILD probability.
18. Never treat missing evidence as negative evidence.
19. Never issue autonomous imaging/procedure/treatment orders.
20. Always require clinician review.
21. Every medical rule must be traceable to references.
22. Preserve evidence conflicts and modality discordance.

## Not encoded in v1

Do not invent detailed rules for:
- IPF treatment;
- CTD-ILD;
- hypersensitivity pneumonitis;
- occupational/asbestos disease;
- post-infectious fibrosis;
- drug/radiation fibrosis;
- sarcoidosis;
- familial/genetic fibrosis;
- acute exacerbation;
- treatment selection.

These require separate evidence/skills.
