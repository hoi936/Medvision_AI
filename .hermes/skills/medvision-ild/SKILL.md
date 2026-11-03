---
name: medvision-ild
description: Evidence-grounded reasoning procedure for the VinBigData ILD radiographic finding in MedVision Hermes. Treats the CXR output as broad interstitial-pattern evidence, separates CXR from HRCT characterization, prevents automatic IPF/UIP/fibrosis diagnosis, handles ILA and progression boundaries, deduplicates overlapping broad findings, and produces a bounded assessment for clinician review.
---

# MedVision ILD Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: ild
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`ILD`

This skill does not establish IPF, UIP, NSIP, CTD-ILD, hypersensitivity pneumonitis, pulmonary fibrosis, PPF, or another final ILD subtype.

## Progressive disclosure

Before applying detailed evidence rules, load:

`skill_view("medvision-ild", "references/references.md")`

When detailed classification, ILA, UIP/IPF, PPF, HRCT terminology, or scope boundaries are required, load:

`skill_view("medvision-ild", "references/ILD_EVIDENCE.md")`

Do not invent medical facts not supported by those references.

## Core semantic rule

`ILD` from the CXR AI is **broad radiographic evidence compatible with an interstitial pattern**.

It is NOT automatically:
- IPF;
- UIP;
- NSIP;
- pulmonary fibrosis;
- CTD-ILD;
- hypersensitivity pneumonitis;
- PPF;
- a treatment indication.

## Procedure

### Step 1 — Preserve CXR evidence

Record:
- canonical finding `ILD`;
- model score;
- distribution if supplied;
- radiologist/manual interpretation if supplied;
- model/version.

Do not convert model score into subtype probability.

### Step 2 — Separate CXR from HRCT

If no HRCT/CT characterization is supplied:
- do not invent reticulation;
- do not invent GGO;
- do not invent traction bronchiectasis;
- do not invent honeycombing;
- do not invent UIP pattern;
- mark fibrosis status unknown.

If suspected diffuse lung disease context is truly present, `HRCT_CHARACTERIZATION_RELEVANT` may be identified as a clinician-facing consideration [S4].

Do not autonomously order CT.

### Step 3 — Preserve actual HRCT morphology

When HRCT findings are explicitly supplied, record:
- reticulation;
- GGO;
- traction bronchiectasis/bronchiolectasis;
- honeycombing;
- architectural distortion;
- distribution;
- reported pattern.

Do not infer etiology from morphology alone.

### Step 4 — Separate fibrotic and non-fibrotic context

Current ERS/ATS classification distinguishes fibrotic and non-fibrotic interstitial disorders [S2].

Therefore:
- `ILD -> pulmonary fibrosis` is prohibited;
- fibrosis must be independently supported.

If fibrosis evidence is supplied, preserve it as a more-specific characterization.

### Step 5 — UIP / IPF guardrail

If HRCT explicitly reports UIP/probable-UIP or another IPF-evaluation pattern:
- preserve the imaging pattern;
- do not automatically diagnose IPF [S3].

Maintain separate:
- imaging pattern;
- clinical/etiologic diagnosis;
- diagnostic confidence.

### Step 6 — ILA vs clinical ILD

If CT abnormalities meet an ILA context:
- preserve `ILA` as a CT concept;
- do not automatically treat it as a specific ILD [S5].

Do not call a CXR classifier output an ATS-defined ILA.

Use symptoms, PFTs, imaging progression and other supplied context to distinguish disease-level concern.

### Step 7 — Clinical and secondary-cause context

Record only if supplied:
- dyspnea/cough;
- exposure history;
- autoimmune/CTD context;
- medication/radiation context;
- family history;
- pulmonary physiology.

Do not invent secondary causes.

### Step 8 — Evaluate PPF only when longitudinal evidence is adequate

PPF applies to an adult with ILD other than IPF and requires at least two of:
- worsening respiratory symptoms;
- physiological progression;
- radiological progression

within the past year, with no alternative explanation [S3].

If required evidence is missing:

`ppf_evaluable: false`

Do not diagnose PPF from one image or one positive model result.

### Step 9 — Overlap with Lung Opacity / Infiltration

If ILD coexists with:
- `Lung Opacity`;
- `Infiltration`;

preserve all upstream results.

If they plausibly describe the same process:
emit:

`OVERLAPPING_FINDING_EVIDENCE`

Do not double/triple count.

ILD may provide the more-specific interstitial-pattern interpretation.

### Step 10 — Consolidation relationship

If ILD and Consolidation coexist:
- preserve both;
- do not automatically infer acute exacerbation;
- evaluate acute clinical deterioration separately.

### Step 11 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing evidence is not negative evidence.

### Step 12 — Conflict detection

If AI conflicts with trusted human review or high-quality HRCT:

emit:

`EVIDENCE_CONFLICT`

Preserve both.

Do not silently prefer AI.

### Step 13 — Safety

ILD alone is not automatically an emergency.

If independent evidence shows:
- severe/new respiratory distress;
- significant hypoxemia;
- rapid physiological deterioration;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous imaging/procedure/treatment orders.

### Step 14 — Produce bounded assessment

Separate:
1. CXR interstitial-pattern evidence;
2. HRCT characterization;
3. fibrosis status;
4. ILA vs clinical-ILD context;
5. subtype hypothesis;
6. diagnostic confidence;
7. symptoms/exposure/CTD context;
8. physiology;
9. progression/PPF evaluability;
10. overlap flags;
11. supporting/contradicting evidence;
12. missing evidence;
13. conflicts;
14. safety;
15. clinician review;
16. citations.

## Evidence rules

### [S2] Classification rule
Interstitial disorders include fibrotic and non-fibrotic categories and idiopathic/secondary causes; diagnostic confidence is part of multidisciplinary evaluation.

### [S3] UIP/IPF rule
An HRCT UIP-type pattern is an imaging component of IPF evaluation, not automatic IPF diagnosis.

### [S3] PPF rule
PPF requires at least 2 of 3 progression domains within one year with no alternative explanation in ILD other than IPF.

### [S5] ILA rule
ILA is a CT-defined abnormality concept and is distinct from clinical ILD.

### [S1] Terminology rule
CT morphology must remain modality-specific and should not be invented from a CXR class.

### [S4] Imaging-context rule
CT chest without contrast has an appropriate role in suspected diffuse lung disease but is not an autonomous order generated by this skill.

## Output schema

```yaml
finding: ild
finding_type: radiographic_interstitial_pattern

cxr_evidence:
  model_score: null
  distribution: unknown
  radiologist_interpretation: unknown

hrct_characterization:
  available: false
  reticulation: unknown
  ground_glass_opacity: unknown
  traction_bronchiectasis: unknown
  traction_bronchiolectasis: unknown
  honeycombing: unknown
  architectural_distortion: unknown
  distribution: unknown
  reported_pattern: unknown

interstitial_context:
  fibrosis_status: unknown
  ila_status: unknown
  clinical_ild_status: unknown
  subtype_hypothesis: unknown
  diagnostic_confidence: unknown

clinical_context:
  symptoms: []
  exposure_context: unknown
  autoimmune_ctd_context: unknown
  medication_radiation_context: unknown
  family_history: unknown

physiology:
  pft_available: false
  fvc: unknown
  dlco: unknown
  longitudinal_change: unknown

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

1. Never equate ILD with IPF.
2. Never equate ILD with UIP.
3. Never equate ILD with NSIP.
4. Never equate ILD with pulmonary fibrosis.
5. Never equate ILD with CTD-ILD.
6. Never equate ILD with hypersensitivity pneumonitis.
7. Never infer CT morphology from the CXR AI class.
8. Never equate a UIP imaging pattern with IPF diagnosis.
9. Never equate CT ILA with a specific clinical ILD.
10. Never diagnose PPF from a single study.
11. Never diagnose PPF without adequate longitudinal criteria.
12. Never infer acute ILD exacerbation from ILD + Consolidation alone.
13. Never double/triple count overlapping ILD/Lung Opacity/Infiltration evidence.
14. Never invent exposure, CTD, PFT, pathology, or family-history evidence.
15. Never convert AI score into subtype probability.
16. Never treat missing data as negative evidence.
17. Never issue autonomous imaging/procedure/treatment orders.
18. Always require clinician review.
19. Every medical/terminology rule must be traceable to references.
20. Preserve direct evidence conflicts and modality discordance.

## Not encoded in v1

Do not invent detailed rules for:
- CTD-ILD subtype diagnosis;
- hypersensitivity pneumonitis;
- sarcoidosis;
- occupational/environmental ILD;
- drug/radiation ILD;
- genetic/familial pulmonary fibrosis;
- acute-exacerbation diagnostic criteria;
- treatment selection.

These require separate evidence/skills.
