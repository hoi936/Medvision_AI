---
name: medvision-infiltration
description: Evidence-grounded compatibility and reasoning procedure for the VinBigData Infiltration radiographic label in MedVision Hermes. Preserves the canonical upstream label for provenance, treats infiltrate as legacy nonspecific terminology, prevents disease overinterpretation and overlap double counting, and produces a bounded assessment for clinician review.
---

# MedVision Infiltration Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: infiltration
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Infiltration`

This is primarily a **legacy-label compatibility + evidence de-duplication skill**.

It does not diagnose pneumonia, infection, ILD, edema, cancer, TB, or another etiology.

## Progressive disclosure

Before applying terminology/evidence rules, load:

`skill_view("medvision-infiltration", "references/references.md")`

When detailed overlap, dataset taxonomy, immune-status imaging scope, or terminology limitations are required, load:

`skill_view("medvision-infiltration", "references/INFILTRATION_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Infiltration` from image AI is a **legacy nonspecific radiographic label** [S1][S3].

It is NOT automatically:
- pneumonia;
- infection;
- consolidation;
- ILD;
- pulmonary edema;
- tuberculosis;
- malignancy.

The upstream label must still be preserved because it is a canonical dataset/model output [S2].

## Procedure

### Step 1 — Preserve upstream provenance

Record:
- canonical finding exactly as `Infiltration`;
- model score;
- localization/bounding box if supplied;
- distribution if supplied;
- radiologist/manual interpretation if supplied;
- model/version.

Do not rename or delete the canonical label.

Do not convert model score into disease probability.

### Step 2 — Apply modern terminology caution

Recognize that `infiltrate` is obsolete/nonrecommended and imprecise [S1][S3].

When generating clinician-facing reasoning:
- describe it as a nonspecific/opacity-like radiographic finding;
- do not promote `infiltrate` as a precise etiologic term.

Do not mutate the audit/provenance label.

### Step 3 — Keep finding and disease separate

`Infiltration` is a local VinDr-CXR finding label, separate from disease-level labels [S2].

Do not map it directly to:
- Pneumonia;
- Tuberculosis;
- Lung tumor;
- another disease.

### Step 4 — Check Lung Opacity overlap

If both `Infiltration` and `Lung Opacity` are positive:
- preserve both;
- emit `OVERLAPPING_FINDING_EVIDENCE` when appropriate;
- do not count both as independent disease-confirming evidence.

This is `MEDVISION_SYSTEM_POLICY`.

### Step 5 — Check Consolidation and other specific patterns

If more-specific findings are present, such as:
- Consolidation;
- Atelectasis;
- Nodule/Mass;
- ILD;
- Pulmonary fibrosis;

preserve all findings.

Use the more-specific descriptor for morphology where appropriate.

Do not infer etiology from co-occurrence.

### Step 6 — Prevent triple counting

If:
- Infiltration;
- Lung Opacity;
- Consolidation

are all positive and plausibly describe one process:
- preserve all three upstream outputs;
- mark overlap;
- do not treat them as three independent proofs of disease;
- do not infer pneumonia automatically.

### Step 7 — Infection hypothesis only from clinical context

If compatible clinical/lab/microbiologic evidence is supplied:
- infection/pneumonia may be evaluated as a separate hypothesis.

But:
`Infiltration -> pneumonia`
is prohibited [S3].

Absence of fever/cough does not negate the image finding itself.

### Step 8 — Scope-specific imaging context

If immunocompetent acute respiratory illness context is actually present:
- S4 may inform evaluation context.

If immunocompromised acute respiratory illness context is actually present:
- S5 may support `CT_CHARACTERIZATION_RELEVANT` in applicable scenarios.

Do not generalize either source outside scope.

Do not autonomously order CT.

### Step 9 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing information is not negative evidence.

### Step 10 — Conflict detection

If AI conflicts with trusted human review or later definitive imaging:

emit:

`EVIDENCE_CONFLICT`

Preserve both.

Do not silently prefer AI.

### Step 11 — Safety

`Infiltration` alone is not automatically an emergency.

If independent evidence shows:
- severe respiratory distress;
- significant hypoxemia;
- physiologic instability;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous imaging/procedure/treatment orders.

### Step 12 — Produce bounded assessment

Separate:
1. canonical upstream label;
2. legacy terminology note;
3. localization/distribution;
4. more-specific co-findings;
5. overlap/de-duplication flags;
6. infection/disease hypotheses;
7. immune/acute-respiratory context;
8. supporting/contradicting evidence;
9. missing evidence;
10. conflicts;
11. safety;
12. uncertainty;
13. clinician review;
14. citations.

## Evidence rules

### [S1] Terminology
`Infiltrate` is obsolete/nonrecommended; `opacity` is the preferred broad nonspecific terminology.

### [S2] Dataset semantics
`Infiltration` remains a distinct canonical local finding label and must be preserved for provenance.

### [S3] Imprecision guardrail
`Infiltrate` is nonspecific and does not imply a unique etiology.

### [S4][S5] Scope-limited imaging context
Acute-respiratory-illness imaging guidance applies only when the case matches the relevant immune-status scenario.

## Output schema

```yaml
finding: infiltration
finding_type: legacy_nonspecific_radiographic_label

image_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  focality: unknown
  radiologist_interpretation: unknown

terminology:
  canonical_label_preserved: true
  legacy_nonrecommended_term: true
  preferred_modern_descriptor: opacity_like

specific_pattern_context:
  lung_opacity: unknown
  consolidation: unknown
  atelectasis: unknown
  nodule_mass: unknown
  ild_or_fibrosis: unknown
  other: []

overlap:
  detected: false
  flags: []
  notes: []

clinical_context:
  acute_respiratory_illness: unknown
  immunocompromised: unknown
  infection_hypothesis: unknown

ct_characterization:
  available: false
  morphology: unknown

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

1. Never equate `Infiltration` with pneumonia.
2. Never equate `Infiltration` with infection.
3. Never equate `Infiltration` with Consolidation.
4. Never equate `Infiltration` with ILD.
5. Never equate `Infiltration` with pulmonary edema.
6. Never equate `Infiltration` with lung cancer.
7. Never count `Infiltration + Lung Opacity` as independent disease proof by default.
8. Never triple-count `Infiltration + Lung Opacity + Consolidation`.
9. Never delete/rename the canonical upstream `Infiltration` label in provenance.
10. Never infer etiology from distribution alone.
11. Never apply immunocompromised imaging rules outside scope.
12. Never automatically recommend CT for every `Infiltration`.
13. Never convert AI score into underlying-disease probability.
14. Never treat missing data as negative evidence.
15. Never issue autonomous imaging/procedure/treatment orders.
16. Always require clinician review.
17. Every medical/terminology rule must be traceable to references.
18. Preserve evidence conflicts.

## Not encoded in v1

Do not invent detailed rules for:
- pneumonia treatment;
- pathogen prediction;
- ILD subtype diagnosis;
- edema diagnosis/treatment;
- malignancy diagnosis;
- automated bbox overlap;
- pediatric terminology;
- disease-specific immunocompromised algorithms.

These require separate evidence/skills.
