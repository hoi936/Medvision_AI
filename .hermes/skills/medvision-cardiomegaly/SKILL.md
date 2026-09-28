---
name: medvision-cardiomegaly
description: Evidence-grounded clinical reasoning procedure for the VinBigData Cardiomegaly radiographic finding in MedVision Hermes. Treats apparent cardiac enlargement as imaging evidence, checks PA/AP technical reliability and CTR limitations, evaluates heart-failure and structural hypotheses separately, integrates TTE/natriuretic-peptide context when available, and produces a bounded assessment for clinician review.
---

# MedVision Cardiomegaly Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: cardiomegaly
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Cardiomegaly`

This skill does not establish heart failure, ventricular dysfunction, cardiomyopathy, or another final cardiac diagnosis and does not prescribe treatment.

## Progressive disclosure

Before applying detailed medical rules, load:

`skill_view("medvision-cardiomegaly", "references/references.md")`

When detailed projection, CTR, HF, or modality limitations are required, load:

`skill_view("medvision-cardiomegaly", "references/CARDIOMEGALY_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`Cardiomegaly` from image AI is **radiographic evidence of apparent cardiac enlargement**.

It is NOT automatically:
- heart failure;
- reduced EF;
- LV dilation;
- LV hypertrophy;
- cardiomyopathy;
- pulmonary edema;
- pericardial effusion;
- volume overload.

## Procedure

### Step 1 — Preserve image evidence

Record:
- canonical finding;
- model score;
- projection if supplied;
- portable/supine status if supplied;
- CTR only if explicitly supplied;
- radiologist/manual interpretation if supplied;
- model/version when available.

Do not convert model score into disease probability.

Do not infer a CTR from the classifier score.

### Step 2 — Check projection reliability

If projection is PA:
- classic CTR interpretation may be considered if a measured CTR is actually available [S1].

If projection is AP/portable/supine:
- emit `PROJECTION_LIMITATION`;
- increase uncertainty;
- do not apply the classic PA `CTR > 0.50` rule unchanged [S1][S6].

If projection is unknown:
- mark it missing;
- do not assume PA.

### Step 3 — Interpret CTR conservatively

If projection is known PA and measured CTR > 0.50:
- this can support `RADIOGRAPHIC_CARDIAC_ENLARGEMENT_SUPPORTED` [S1].

But:
- the threshold has limited diagnostic performance for true chamber enlargement [S2];
- it does not establish cardiac function [S1].

Never output:
`CTR > 0.50 -> heart failure`
or
`CTR > 0.50 -> reduced EF`.

### Step 4 — Evaluate heart-failure hypothesis

Use cardiomegaly only as one evidence item.

Look for:
- dyspnea/orthopnea/PND if supplied;
- peripheral edema/JVP/other clinician findings;
- pulmonary congestion/edema imaging evidence;
- BNP/NT-proBNP;
- TTE structural/functional findings.

CXR should not be the sole determinant of HF [S3].

Cardiomegaly may be absent in acute HF [S3].

### Step 5 — Integrate natriuretic peptides

If BNP/NT-proBNP is supplied:
- use it as contextual evidence;
- do not use it alone to confirm HF;
- do not add a universal cutoff in this skill [S5].

### Step 6 — Integrate TTE/other cardiac imaging

If TTE is available:
- use it as more direct evidence of cardiac structure/function [S3];
- preserve the CXR finding separately.

Do not infer EF or chamber size when not provided.

Normal EF does not automatically invalidate a radiographic cardiomegaly finding.

### Step 7 — Consider silhouette alternatives

If pericardial disease/effusion is independently known:
- it may contribute to an enlarged silhouette [S1].

Do not diagnose pericardial effusion from cardiomegaly alone.

### Step 8 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing data is never negative evidence.

### Step 9 — Conflict / discordance

If AI Cardiomegaly directly conflicts with trusted human CXR review or later reliable radiographic assessment:
emit:

`EVIDENCE_CONFLICT`

and preserve both sources.

If CXR enlargement and TTE chamber size/function differ:
- report modality/technical discordance explicitly;
- do not silently prefer the AI;
- do not force a hard contradiction where the modalities measure different properties.

### Step 10 — Safety

If case data indicate:
- acute severe dyspnea;
- significant hypoxemia;
- hemodynamic/physiological instability;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous treatment/procedure orders.

### Step 11 — Produce bounded assessment

Separate:
1. radiographic finding;
2. projection/technical reliability;
3. CTR interpretation if evaluable;
4. true chamber enlargement status;
5. HF hypothesis;
6. structural/functional cardiac evidence;
7. pericardial/alternative silhouette context;
8. supporting/contradicting evidence;
9. missing evidence;
10. conflicts/discordance;
11. safety;
12. uncertainty;
13. doctor review requirement;
14. citations.

## Evidence rules

### [S1] CTR semantics
Classic CTR is based on PA radiographs; >0.50 supports radiographic enlargement but does not describe function.

### [S2] True chamber enlargement guardrail
The classic 0.50 threshold has limited diagnostic value for MRI-defined chamber enlargement.

### [S3] Heart-failure guardrail
CXR cardiomegaly is contextual evidence and must not be the sole determinant of HF; TTE provides direct structural/functional information.

### [S4] LV dysfunction guardrail
Cardiomegaly alone cannot reliably confirm or exclude LV dysfunction.

### [S5] BNP integration
Natriuretic peptide and CXR can provide complementary evidence in acute dyspnea.

### [S6] AP projection guardrail
AP projection can exaggerate apparent cardiac size and must increase uncertainty.

## Output schema

```yaml
finding: cardiomegaly
finding_type: radiographic_finding

image_evidence:
  model_score: null
  projection: unknown
  portable: unknown
  ctr:
    available: false
    value: null
    classic_pa_interpretation_evaluable: false

technical_context:
  projection_limitation: false
  notes: []

cardiac_enlargement:
  radiographic_support: present
  true_chamber_enlargement: unknown

heart_failure_hypothesis:
  status: unknown
  supporting: []
  contradicting: []

cardiac_structure_function:
  tte_available: false
  ef: unknown
  chamber_enlargement: unknown
  pericardial_findings: unknown

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

1. Never equate Cardiomegaly with heart failure.
2. Never equate Cardiomegaly with reduced EF.
3. Never equate Cardiomegaly with cardiomyopathy.
4. Never infer chamber-specific enlargement from the AI label alone.
5. Never treat `CTR > 0.50` as proof of true chamber enlargement.
6. Never apply the classic PA 0.50 rule unchanged to AP/portable radiographs.
7. Never infer HF from CXR cardiomegaly without clinical context.
8. Never infer pericardial effusion from cardiomegaly alone.
9. Never treat normal EF as proof that the radiographic finding is false.
10. Never invent projection, CTR, EF, chamber measurements, or symptoms.
11. Never convert AI model score into disease probability without validated calibration.
12. Never treat missing data as negative evidence.
13. Never issue autonomous treatment/procedure orders.
14. Always require clinician review.
15. Every medical rule must be traceable to references.
16. Preserve direct evidence conflicts and modality discordance.

## Not encoded in v1

Do not invent detailed rules for:
- pediatric CTR;
- chamber-specific CXR enlargement patterns;
- valvular disease;
- congenital disease;
- HFpEF/HFrEF/HFmrEF classification;
- dedicated pericardial-effusion diagnosis;
- universal BNP/NT-proBNP thresholds;
- treatment selection.

These require additional evidence.
