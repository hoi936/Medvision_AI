---
name: medvision-lung-opacity
description: Evidence-grounded reasoning procedure for the VinBigData Lung Opacity radiographic finding in MedVision Hermes. Treats opacity as a broad nonspecific descriptor, keeps disease hypotheses separate, identifies overlap with more-specific findings to prevent double counting, preserves CXR-vs-CT terminology boundaries, and produces a bounded assessment for clinician review.
---

# MedVision Lung Opacity Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: lung_opacity
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Lung Opacity`

This skill intentionally remains broad. It does not diagnose pneumonia, cancer, edema, hemorrhage, ILD, tuberculosis, or another etiology.

## Progressive disclosure

Before applying detailed terminology/evidence rules, load:

`skill_view("medvision-lung-opacity", "references/references.md")`

When detailed overlap, dataset-semantics, CXR-vs-CT boundaries, or evidence limitations are needed, load:

`skill_view("medvision-lung-opacity", "references/LUNG_OPACITY_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Lung Opacity` from image AI is a **nonspecific radiographic descriptor** [S1].

It is NOT automatically:
- pneumonia;
- consolidation;
- atelectasis;
- lung cancer/tumor;
- pulmonary edema;
- pulmonary hemorrhage;
- tuberculosis;
- ILD;
- ground-glass opacity.

## Procedure

### Step 1 — Preserve image evidence

Record:
- canonical finding;
- model score;
- localization/bounding-box context if supplied;
- focal/diffuse distribution if supplied;
- radiologist/manual interpretation if supplied;
- model/version.

Do not invent distribution or etiology.

Do not convert model score into disease probability.

### Step 2 — Preserve finding-vs-diagnosis separation

`Lung opacity` is a local radiographic finding in VinDr-CXR; disease-level labels are represented separately [S2].

Do not map Lung Opacity directly to:
- Pneumonia;
- Lung tumor;
- Tuberculosis;
- another disease.

### Step 3 — Look for more-specific positive findings

Check for available:
- Consolidation;
- Atelectasis;
- Nodule/Mass;
- Infiltration;
- ILD;
- Pulmonary fibrosis;
- other more-specific image findings.

Preserve every upstream result.

### Step 4 — Prevent double counting

If Lung Opacity and a more-specific finding plausibly describe the same image process:

emit:

`OVERLAPPING_FINDING_EVIDENCE`

This is `MEDVISION_SYSTEM_POLICY`.

Use the more-specific finding to refine pattern characterization, but:
- do not delete the Lung Opacity result;
- do not count both as independent disease-confirming evidence.

If spatial correspondence is unknown:
- retain uncertainty;
- do not assume overlap with certainty.

### Step 5 — Consolidation relationship

Consolidation is more specific than generic opacity [S1].

If both are positive:
- preserve both;
- do not infer pneumonia;
- avoid double counting when they plausibly represent the same process.

### Step 6 — Infiltration relationship

Fleischner regards `infiltrate` as obsolete/nonrecommended terminology historically used in relation to opacity [S1].

VinDr-CXR nevertheless exposes `Infiltration` and `Lung opacity` as separate local labels [S2].

Therefore:
- preserve both canonical upstream labels;
- do not rewrite dataset semantics;
- identify semantic overlap where appropriate.

### Step 7 — Ground-glass guardrail

Ground-glass is specifically defined for CT and should be applied in CT context [S1].

Do not turn CXR Lung Opacity into `ground-glass opacity`.

If CT explicitly reports GGO:
- record it as CT characterization;
- keep etiology separate.

### Step 8 — Characterize focality/distribution

If supplied, record:
- focal;
- multifocal;
- diffuse;
- unilateral/bilateral;
- lobe/zone.

Distribution alone does not establish disease.

### Step 9 — Use contextual imaging guidance only when scope matches

If diffuse lung disease is genuinely suspected:
- S3 may support additional characterization reasoning.

If an acute respiratory illness scenario is genuinely present:
- S4 may inform imaging-context reasoning.

Do not create universal:
`Lung Opacity -> CT`
or
`Lung Opacity -> pneumonia`.

Do not autonomously order imaging.

### Step 10 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing information is not negative evidence.

### Step 11 — Conflict detection

If AI conflicts with trusted human review or later definitive imaging:

emit:

`EVIDENCE_CONFLICT`

Preserve both.

Do not silently prefer AI.

Reader/reference-standard uncertainty is relevant for broad CXR findings [S5].

### Step 12 — Safety

Lung Opacity alone is not automatically an emergency.

If independent clinical evidence shows:
- severe respiratory distress;
- significant hypoxemia;
- physiologic instability;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous treatment/procedure orders.

### Step 13 — Produce bounded assessment

Separate:
1. broad radiographic opacity;
2. localization/distribution;
3. more-specific co-findings;
4. overlap/de-duplication flags;
5. CT characterization if available;
6. disease hypotheses from other reasoning layers;
7. supporting/contradicting evidence;
8. missing evidence;
9. conflicts;
10. safety;
11. uncertainty;
12. clinician review;
13. citations.

## Evidence rules

### [S1] Opacity semantics
Opacity is a focal/diffuse nonspecific area of increased attenuation and does not define etiology.

### [S1] Terminology boundaries
Consolidation is more specific; ground-glass terminology belongs to CT context; `infiltrate` is obsolete/nonrecommended terminology.

### [S2] Dataset semantics
Lung opacity is a local finding, while suspected disease labels are represented separately.

### [S3][S4] Scope-limited imaging context
Diffuse-lung-disease and acute-respiratory-illness guidance applies only when the case matches those scenarios.

### [S5] Reference-standard caution
AI/reference reads can disagree; adjudication/reference-standard construction affects reproducibility.

## Output schema

```yaml
finding: lung_opacity
finding_type: nonspecific_radiographic_descriptor

image_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  focality: unknown
  radiologist_interpretation: unknown

specific_pattern_context:
  consolidation: unknown
  atelectasis: unknown
  nodule_mass: unknown
  infiltration: unknown
  ild_or_fibrosis: unknown
  other: []

overlap:
  detected: false
  flags: []
  notes: []

ct_characterization:
  available: false
  morphology: unknown
  distribution: unknown

clinical_context:
  acute_respiratory_illness: unknown
  diffuse_lung_disease_context: unknown

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

1. Never equate Lung Opacity with pneumonia.
2. Never equate Lung Opacity with lung tumor/cancer.
3. Never automatically equate Lung Opacity with Consolidation.
4. Never automatically equate Lung Opacity with Atelectasis.
5. Never convert CXR Lung Opacity into ground-glass opacity without CT evidence.
6. Never double count overlapping Lung Opacity + more-specific finding as independent disease evidence.
7. Never silently collapse the canonical `Infiltration` label into Lung Opacity.
8. Never infer disease from distribution alone.
9. Never automatically recommend CT for every Lung Opacity.
10. Never convert AI score into underlying-disease probability.
11. Never treat missing evidence as negative evidence.
12. Never issue autonomous imaging/treatment/procedure orders.
13. Always require clinician review.
14. Every medical/terminology rule must be traceable to references.
15. Preserve AI/human and CXR/CT conflicts.

## Not encoded in v1

Do not invent detailed rules for:
- pneumonia treatment;
- edema treatment;
- hemorrhage treatment;
- ILD subtype diagnosis;
- TB diagnosis;
- malignancy diagnosis;
- quantitative overlap geometry;
- automated bbox matching;
- pediatric opacity reasoning;
- immunocompromised-host algorithms.

These require separate evidence/skills.
