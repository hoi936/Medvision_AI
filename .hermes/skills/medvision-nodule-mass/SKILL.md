---
name: medvision-nodule-mass
description: Evidence-grounded clinical reasoning procedure for the VinBigData Nodule/Mass radiographic finding in MedVision Hermes. Treats the AI output as focal-lesion evidence rather than cancer, separates CXR detection from CT characterization, applies nodule/mass terminology conservatively, evaluates malignancy risk without diagnosing malignancy, and preserves guideline scope and clinician review.
---

# MedVision Nodule/Mass Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: nodule_mass
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Nodule/Mass`

This skill does not diagnose lung cancer and does not autonomously select CT, PET-CT, biopsy, surgery, or treatment.

## Progressive disclosure

Before applying detailed medical rules, load:

`skill_view("medvision-nodule-mass", "references/references.md")`

When detailed terminology, guideline-scope, morphology, or risk boundaries are required, load:

`skill_view("medvision-nodule-mass", "references/NODULE_MASS_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Nodule/Mass` from image AI is **radiographic evidence of a focal pulmonary lesion**.

It is NOT automatically:
- lung cancer;
- malignancy;
- metastasis;
- benign tumor;
- infection;
- indication for invasive testing.

## Procedure

### Step 1 — Preserve CXR evidence

Record:
- canonical finding;
- model score;
- localization if supplied;
- radiologist/manual interpretation if supplied;
- model/version.

Do not infer:
- lesion diameter;
- nodule vs mass terminology;
- CT attenuation type;
- histology.

Do not convert model score into malignancy probability.

### Step 2 — Check age and evaluation scope

Record:
- age;
- screening vs incidental context if known;
- known primary malignancy;
- immunocompromised status.

If age is missing, mark missing.

Do not silently apply an age-specific guideline to an unknown-age case.

### Step 3 — Determine whether CT characterization exists

If an adult >=35 has an indeterminate CXR pulmonary nodule and no CT characterization:
- `CT_CHARACTERIZATION_RELEVANT` may be reported as a clinician-facing evaluation consideration [S2].

Do not issue a CT order.

Do not jump from CXR-only evidence directly to PET-CT, biopsy, or surgery.

### Step 4 — If CT exists, characterize lesion

Record only explicitly supplied:
- size in mm;
- solid / ground-glass / part-solid;
- margin;
- location;
- multiplicity;
- internal calcium/fat/cystic/cavitary components;
- prior change/growth.

Thin-section CT is the preferred basis for detailed small-nodule morphology [S1].

### Step 5 — Apply nodule vs mass terminology

If a reliable measured average diameter is supplied:
- <=30 mm -> nodule terminology is appropriate;
- >30 mm -> mass terminology is appropriate [S1].

A mass is not synonymous with malignancy.

### Step 6 — Check Fleischner 2017 evaluability

Fleischner 2017 can be considered only when the case matches its scope:
- incidental CT-detected pulmonary nodule;
- adult >=35;
- not lung-cancer screening;
- not immunocompromised;
- no known primary cancer at risk for metastasis [S3].

If the scope or required CT characterization is missing:

`fleischner_ct_guidance_evaluable: false`

Do not invent a follow-up interval.

### Step 7 — Evaluate malignancy risk separately

Consider only supplied evidence such as:
- lesion size;
- morphology/spiculation;
- location;
- multiplicity;
- prior growth;
- age;
- smoking and other patient risk context.

Spiculation may increase concern [S3] but does not establish malignancy.

Use:

`malignancy_risk_hypothesis`

not:

`lung_cancer_diagnosis`.

Do not invent a numeric probability unless a validated risk calculator has been deliberately implemented and all required inputs are available.

### Step 8 — Prior imaging

If comparable prior imaging exists:
- preserve measurements and dates;
- identify growth/stability only from actual comparable data.

Do not infer growth from changes in classifier score.

### Step 9 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing evidence is not negative evidence.

### Step 10 — Conflict and modality discordance

If AI conflicts with trusted human CXR review:

emit:

`EVIDENCE_CONFLICT`

If CXR AI is positive but CT reports no corresponding pulmonary lesion:
- preserve the initial AI result;
- treat CT as stronger lesion-characterization evidence;
- report discordance;
- do not continue as if the lesion were CT-confirmed.

### Step 11 — Safety

Nodule/Mass alone is not automatically an emergency.

If independent case evidence shows:
- major hemoptysis;
- severe respiratory compromise;
- physiologic instability;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous imaging, procedure, or treatment orders.

### Step 12 — Produce bounded assessment

Separate:
1. CXR focal-lesion evidence;
2. CT characterization status;
3. nodule/mass terminology if measurable;
4. guideline scope/evaluability;
5. malignancy-risk hypothesis;
6. prior imaging/growth;
7. supporting/contradicting evidence;
8. missing evidence;
9. conflicts/discordance;
10. safety;
11. uncertainty;
12. doctor review;
13. citations.

## Evidence rules

### [S1] Terminology
Nodule <=30 mm; mass >30 mm. CT morphology includes solid, ground-glass, part-solid and other structural/margin descriptors.

### [S2] CXR-to-CT rule
For the specified ACR adult >=35 CXR-only indeterminate-nodule variant, CT chest without IV contrast is the usually appropriate next imaging study.

### [S3] Fleischner scope/risk rule
Fleischner 2017 is for incidental CT-detected nodules in adults >=35 and has important exclusions; size/morphology/risk context matter.

### [S4][S5] Risk-based reasoning
Downstream evaluation is based on estimated malignancy probability, characterization, benefits/harms, and patient context/preferences.

## Output schema

```yaml
finding: nodule_mass
finding_type: radiographic_focal_lesion

cxr_evidence:
  model_score: null
  localization: unknown
  radiologist_interpretation: unknown

ct_characterization:
  available: false
  size_mm: null
  terminology: unknown
  attenuation: unknown
  margin: unknown
  location: unknown
  multiplicity: unknown
  internal_components: []
  prior_growth: unknown

scope:
  age: unknown
  acr_cxr_variant_evaluable: false
  fleischner_ct_guidance_evaluable: false
  known_primary_cancer: unknown
  immunocompromised: unknown
  screening_context: unknown

malignancy_risk_hypothesis:
  status: unknown
  supporting: []
  reducing: []
  quantitative_probability: null

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

1. Never equate `Nodule/Mass` with lung cancer.
2. Never equate a >30 mm mass with malignancy.
3. Never equate spiculation with histologic cancer.
4. Never infer size from AI score/class.
5. Never apply Fleischner CT guidance to uncharacterized CXR-only evidence.
6. Never apply Fleischner outside scope without explicit qualification.
7. Never jump from CXR-only evidence directly to PET/biopsy/surgery.
8. Never infer metastasis from multiplicity alone.
9. Never infer growth from AI-score changes.
10. Never invent a malignancy percentage.
11. Never convert AI score into cancer/malignancy probability.
12. Never treat missing data as negative evidence.
13. Never issue autonomous imaging/procedure/treatment orders.
14. Always require clinician review.
15. Every medical rule must be traceable to references.
16. Preserve conflicts and CXR-vs-CT discordance.

## Not encoded in v1

Do not invent detailed rules for:
- Brock/Mayo/Herder numeric risk calculators;
- Lung-RADS screening;
- detailed calcification-pattern algorithms;
- PET SUV interpretation;
- biopsy-method selection;
- surgery thresholds;
- known-cancer metastatic workup;
- immunocompromised-host algorithms;
- pediatric pulmonary nodules.

These require additional evidence.
