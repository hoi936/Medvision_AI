---
name: medvision-aortic-enlargement
description: Evidence-grounded clinical reasoning procedure for the VinBigData Aortic enlargement radiographic finding in MedVision Hermes. Treats abnormal aortic size/contour on CXR as screening evidence, requires direct imaging for aortic-disease characterization, checks acute-aortic-syndrome red flags, preserves age/body-size and measurement context, and produces a bounded assessment for clinician review.
---

# MedVision Aortic Enlargement Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: aortic_enlargement
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Aortic enlargement`

This skill does not establish aneurysm, dissection, acute aortic syndrome, hypertension, or another final aortic diagnosis and does not prescribe treatment.

## Progressive disclosure

Before applying detailed medical rules, load:

`skill_view("medvision-aortic-enlargement", "references/references.md")`

When detailed guideline boundaries, aortic measurement semantics, or AAS limitations are required, load:

`skill_view("medvision-aortic-enlargement", "references/AORTIC_ENLARGEMENT_EVIDENCE.md")`

Do not invent medical facts that are not supported by those references.

## Core semantic rule

`Aortic enlargement` from image AI is **radiographic evidence of abnormal aortic size/contour**.

It is NOT automatically:
- thoracic aortic aneurysm;
- aortic dissection;
- acute aortic syndrome;
- rupture;
- hypertension;
- indication for intervention.

## Procedure

### Step 1 — Preserve CXR evidence

Record:
- canonical finding;
- model score;
- contour/arch/mediastinal description if explicitly supplied;
- radiologist/manual interpretation;
- prior-CXR comparison if available;
- model/version.

Do not invent aortic diameter or segment.

Do not convert model score into disease probability.

### Step 2 — Check acute-aortic-syndrome context first

Look for case evidence of:
- abrupt severe chest/back pain;
- hemodynamic instability/shock;
- pulse or BP differential;
- neurologic deficit;
- aortic-regurgitation/pericardial complication if documented;
- clinician concern for AAS.

If high-risk context exists:

emit:
- `ACUTE_AORTIC_SYNDROME_CONCERN`
- `HIGH_PRIORITY_CLINICAL_REVIEW`

CXR does not confirm AAS, and normal CXR does not rule it out [S1][S2].

### Step 3 — Look for direct aortic imaging

If TTE, CT/CTA or MRI/MRA data are available:
record:
- modality;
- measured segment;
- maximum diameter;
- prior diameter/growth only if explicitly supplied.

Direct measurements are stronger evidence for true aortic dilation than a generic CXR class [S1][S2][S3].

### Step 4 — Interpret diameter only in proper context

Aortic size depends on:
- segment;
- measurement technique;
- age;
- sex;
- body size/height [S1][S2][S4][S5].

Do not import a universal numeric CXR threshold.

Do not apply measured ascending-aorta guideline definitions to an unmeasured CXR finding.

### Step 5 — Dilation / aneurysm hypothesis

If direct segment-specific imaging documents abnormal enlargement:
- `true_aortic_dilatation` may become supported.

Only evaluate an aneurysm hypothesis using appropriate measured aortic evidence and guideline context.

Never output:
`Aortic enlargement AI -> thoracic aortic aneurysm confirmed`.

### Step 6 — Hypertension context

If actual BP/history supports chronic hypertension:
- it may contribute to the context of aortic enlargement/remodeling.

Do not diagnose hypertension from CXR or aortic width [S6].

### Step 7 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing data is not negative evidence.

### Step 8 — Conflict / modality discordance

If AI directly conflicts with trusted human CXR review:
emit:

`EVIDENCE_CONFLICT`

If CXR suggests enlargement but direct cross-sectional measurement is normal:
- preserve both;
- report modality/measurement discordance;
- do not silently prefer AI.

### Step 9 — Safety

If suspected AAS or acute instability exists:
emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do not issue medication, surgery, endovascular, or imaging-protocol orders.

### Step 10 — Produce bounded assessment

Separate:
1. CXR aortic-enlargement evidence;
2. AAS safety concern;
3. direct aortic measurement;
4. size/indexing context;
5. true-dilation hypothesis;
6. aneurysm hypothesis;
7. hypertension context;
8. conflicts/discordance;
9. missing evidence;
10. uncertainty;
11. safety;
12. clinician-review requirement;
13. citations.

## Evidence rules

### [S1] CXR limitation
CXR abnormalities of aortic size/contour require confirmation; normal CXR does not exclude AAS.

### [S2] Measurement and AAS rule
Direct aortic measurements require defined segment/technique; CXR cannot diagnose AAS; CT is recommended initial imaging in suspected AAS, with appropriate alternatives.

### [S3] Reproducibility rule
Cross-sectional aortic diagnosis/surveillance requires high-quality reproducible measurement and awareness of artifacts.

### [S4][S5] Normal-size context
Aortic dimensions/geometry vary with age, sex, body size and cardiovascular context.

### [S6] Hypertension guardrail
Aortic arch width can be associated with chronic hypertension but cannot establish the diagnosis.

## Output schema

```yaml
finding: aortic_enlargement
finding_type: radiographic_finding

image_evidence:
  model_score: null
  aortic_contour: unknown
  mediastinal_context: unknown
  prior_change: unknown

direct_aortic_imaging:
  available: false
  modality: unknown
  segment: unknown
  diameter_mm: null
  prior_diameter_mm: null
  growth_rate: unknown

size_context:
  age: unknown
  sex: unknown
  height: unknown
  bsa: unknown

aortic_disease_hypotheses:
  true_aortic_dilatation:
    status: unknown
    evidence: []
  thoracic_aortic_aneurysm:
    status: unknown
    evidence: []
  acute_aortic_syndrome:
    status: unknown
    evidence: []
  chronic_hypertensive_remodeling:
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

1. Never equate `Aortic enlargement` with thoracic aortic aneurysm.
2. Never equate `Aortic enlargement` with aortic dissection.
3. Never equate `Aortic enlargement` with acute aortic syndrome.
4. Never use normal CXR to exclude AAS in a high-risk clinical context.
5. Never infer aortic diameter from AI score/class.
6. Never apply segment-specific CT/MRI thresholds directly to an unmeasured CXR finding.
7. Never diagnose hypertension from aortic enlargement.
8. Never infer benignity from age/body size alone.
9. Never invent aortic segment, diameter or growth.
10. Never convert model score into aneurysm/dissection probability.
11. Never treat missing data as negative evidence.
12. Never issue autonomous treatment/procedure orders.
13. Always require clinician review.
14. Every medical rule must be traceable to references.
15. Preserve direct evidence conflicts and modality discordance.

## Not encoded in v1

Do not invent detailed rules for:
- BAV-specific aortopathy;
- Marfan/Loeys-Dietz/HTAD;
- pregnancy;
- intervention thresholds;
- postoperative or post-TEVAR surveillance;
- pediatric aortic dimensions;
- universal CXR aortic-width thresholds.

These require additional evidence.
