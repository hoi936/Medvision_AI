# HEART_FAILURE_EVIDENCE.md

## 0. Scope

This document defines MedVision Disease Analysis v2 reasoning for:

**Heart failure syndrome / cardiogenic congestion hypothesis**

It is not:
- a new VinBigData finding skill;
- a new top-level Hermes skill;
- a treatment/disposition engine.

Target flow remains:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ heart-failure/congestion reference module
```

Central rules:

```text
Cardiomegaly / Pleural effusion / Lung Opacity
!=
Heart failure diagnosis
```

and:

```text
Heart failure syndrome
!=
Radiographic pulmonary congestion
```

HF can exist without obvious CXR congestion, and CXR abnormalities can have non-HF causes.

## 1. Current disease definition

The 2026 Second Universal Definition describes HF as a clinical syndrome established by accumulating compatible:
- symptoms/signs;
- structural or functional cardiac abnormality;
- laboratory evidence such as natriuretic peptides;
- imaging/hemodynamic evidence of pulmonary/systemic congestion or altered cardiac output.

No single test establishes HF.

## 2. MedVision disease-analysis states

Internal system-policy labels:

```text
HEART_FAILURE_HYPOTHESIS_SUPPORTED
CARDIOGENIC_CONGESTION_HYPOTHESIS_SUPPORTED
IMAGING_FINDINGS_WITHOUT_SUFFICIENT_HF_CLINICAL_SUPPORT
HEART_FAILURE_POSSIBLE_WITHOUT_RADIOGRAPHIC_CONGESTION
HEART_FAILURE_HYPOTHESIS_CONFLICTED
HEART_FAILURE_HYPOTHESIS_NOT_ESTABLISHED
HF_PHENOTYPE_UNRESOLVED
HF_OBJECTIVE_EVIDENCE_INCOMPLETE
```

These are bounded reasoning states, not final physician diagnoses.

## 3. Imaging evidence

### Cardiomegaly

Preserve `Cardiomegaly` as radiographic evidence of apparent cardiac enlargement.

It does not establish:
- HF;
- reduced EF;
- LV dilation;
- HFpEF;
- HFrEF;
- acute decompensation.

Projection/technique limitations remain governed by the existing cardiomegaly skill.

### Pleural effusion

Pleural effusion can occur with HF/congestion but is nonspecific.

Do not infer:
- cardiogenic cause;
- transudate;
- HF diagnosis;
- drainage need.

### Lung Opacity / Infiltration / Consolidation

These classes are not synonyms for pulmonary edema.

If AI provides only generic airspace findings:
- preserve them as morphology;
- do not assign cardiogenic edema etiology.

A trusted radiologist/CT description of pulmonary edema, vascular congestion, or interstitial edema is stronger congestion evidence than generic AI classes.

### CXR congestion

CXR is part of HF diagnostic assessment but has limitations.

Therefore:

```text
explicit CXR congestion
+ compatible clinical/cardiac evidence
→ may support HF/congestion hypothesis
```

but:

```text
CXR finding alone
→ not HF diagnosis
```

### No Finding

`No finding` in the 14-class VinBigData output does not universally exclude HF.

HF may still be supported by:
- symptoms/signs;
- echo;
- natriuretic-peptide context;
- hemodynamics;
- trusted non-CXR imaging.

## 4. Clinical syndrome

Use only supplied data.

Typical compatible features include:
- dyspnea;
- orthopnea;
- paroxysmal nocturnal dyspnea;
- reduced exercise tolerance;
- fatigue;
- ankle/peripheral edema;
- elevated JVP;
- hepatojugular reflux;
- S3;
- rales/crackles;
- abdominal swelling.

No single symptom/sign establishes HF.

Missing data stays missing.

## 5. Natriuretic peptides

BNP/NT-proBNP can support HF diagnostic reasoning, especially in dyspnea.

Elevated NP is not HF-specific. Known alternative contributors include:
- atrial fibrillation;
- ACS;
- LV hypertrophy;
- valvular disease;
- advancing age;
- anemia;
- renal failure;
- pulmonary embolism;
- pulmonary hypertension;
- severe pneumonia;
- critical illness;
- sepsis.

Therefore:

```text
elevated BNP/NT-proBNP != HF confirmed
```

The 2026 ESC guideline also requires contextual interpretation for age, obesity, kidney dysfunction, and other modifiers.

Obesity can yield disproportionately low NP values, and the 2026 Second Universal Definition notes some unequivocal HFpEF patients may have normal NP values.

Therefore:

```text
low/normal NP != universal HF exclusion
```

No single universal numeric NP cutoff is encoded in MedVision v1.

## 6. Echocardiography and objective cardiac evidence

TTE is central to:
- cardiac structure/function;
- EF;
- filling-pressure evidence;
- valvular assessment;
- HF phenotype.

Hermes must not infer EF from CXR.

If echo is supplied, it is stronger evidence for cardiac structure/function than apparent cardiac size on CXR, while upstream CXR provenance remains preserved.

## 7. HF phenotype

Use current 2026 source precedence.

Possible outputs:

```text
HFrEF
HFpEF
HF_with_improved_EF
HF_PHENOTYPE_UNRESOLVED
```

Only assign phenotype when adequate cardiac imaging plus supported HF syndrome exists.

Do not phenotype from:
- CXR alone;
- BNP alone;
- symptoms alone;
- AI score.

The 2026 ESC framework currently treats reduced EF in the context of symptoms/signs and LVEF below the preserved range, while the 2026 Second Universal Definition intentionally moves away from treating rigid EF cutoffs as the sole disease definition.

Preserve older clinician-documented labels such as `HFmrEF` with source/time; do not silently rewrite historical documentation.

HFpEF is not established by preserved EF alone. It requires a compatible syndrome plus objective support such as filling-pressure/cardiac evidence.

HF with improved EF requires longitudinal evidence; one higher EF measurement is insufficient.

## 8. Basic fusion states

### A — compatible syndrome + objective cardiac/congestion evidence

Example:

```text
dyspnea + orthopnea
+ elevated JVP
+ echo structural/functional abnormality
+ supportive NP or congestion evidence
```

Output:

`HEART_FAILURE_HYPOTHESIS_SUPPORTED`

### B — CXR findings only

Example:

```text
Cardiomegaly POSITIVE
Pleural effusion POSITIVE
clinical data missing
```

Output:

`IMAGING_FINDINGS_WITHOUT_SUFFICIENT_HF_CLINICAL_SUPPORT`

### C — supported HF without radiographic congestion

Example:

```text
No finding POSITIVE
+ dyspnea/orthopnea
+ echo cardiac dysfunction
+ supportive NP/hemodynamics
```

Output:

`HEART_FAILURE_POSSIBLE_WITHOUT_RADIOGRAPHIC_CONGESTION`

or `HEART_FAILURE_HYPOTHESIS_SUPPORTED` when total evidence is sufficient.

### D — explicit congestion + compatible HF evidence

Example:

```text
radiologist: pulmonary vascular/interstitial congestion
+ dyspnea
+ supportive cardiac/NP evidence
```

Output may include:

`CARDIOGENIC_CONGESTION_HYPOTHESIS_SUPPORTED`

This does not independently establish EF phenotype.

### E — trusted conflict

If CXR suggests congestion while stronger later CT/echo/hemodynamic evidence argues against cardiogenic congestion:

`HEART_FAILURE_HYPOTHESIS_CONFLICTED`

and/or:

`EVIDENCE_CONFLICT`

Preserve source and timing.

## 9. Kidney dysfunction

Kidney dysfunction can elevate BNP/NT-proBNP.

Therefore:
- preserve kidney dysfunction as an NP modifier;
- do not discard NP entirely;
- do not automatically confirm HF;
- do not force a kidney-vs-HF winner.

## 10. Obesity

Obesity can lower NP values.

Therefore obesity + low/normal NP must not automatically exclude HF when other objective evidence is strong.

## 11. Pneumonia vs HF

If airspace findings, fever/inflammatory context, and cardiac/congestion evidence coexist:
- preserve pneumonia hypothesis;
- preserve HF/congestion hypothesis;
- preserve shared/overlapping evidence;
- do not force a winner without evidence.

Generic Lung Opacity/Consolidation must not be assigned automatically to edema or pneumonia.

## 12. AI score semantics

Never convert:

```text
Cardiomegaly score = 0.95
```

into:

```text
95% probability of HF
```

Finding score remains model output only.

## 13. Safety

Independent severe evidence such as:
- severe hypoxemia;
- respiratory failure;
- shock/hypoperfusion;
- severe trusted congestion evidence;

may support:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do not autonomously:
- prescribe diuretics;
- start oxygen/ventilation;
- start vasoactive therapy;
- admit to ICU;
- order echo/CT;
- perform thoracentesis;
- modify HF medications.

## 14. Recommended output

```yaml
disease_hypothesis:
  name: heart_failure
  status: not_established|possible|supported|conflicted

congestion_hypothesis:
  pulmonary: unknown|absent|possible|supported
  systemic: unknown|absent|possible|supported
  cardiogenic_origin: unknown|possible|supported

clinical_support:
  symptoms: []
  signs: []
  missing: []

imaging_support:
  cxr_findings: []
  explicit_congestion_findings: []
  echo_findings: []
  other_imaging: []
  radiographic_congestion: unknown|absent|possible|supported

biomarkers:
  bnp: unknown
  nt_probnp: unknown
  interpretation: unknown
  modifiers: []

cardiac_structure_function:
  status: unknown
  lvef: unknown
  filling_pressure_evidence: unknown
  structural_abnormalities: []

phenotype:
  status: unresolved
  label: null
  source: null

competing_hypotheses: []
supporting_evidence: []
contradicting_evidence: []
missing_evidence: []
conflicts: []

safety:
  priority: routine|elevated|high
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true
```

## 15. Hard constraints

Hermes MUST NOT:

1. Convert Cardiomegaly directly into HF.
2. Convert Pleural effusion directly into HF.
3. Convert Lung Opacity/Infiltration/Consolidation directly into pulmonary edema.
4. Infer EF from CXR.
5. Infer a specific chamber abnormality from generic cardiomegaly.
6. Confirm HF from elevated BNP/NT-proBNP alone.
7. Universally exclude HF from low/normal BNP/NT-proBNP.
8. Ignore known NP modifiers.
9. Infer HFpEF from preserved EF alone.
10. Infer improved EF from one study.
11. Rewrite historical phenotype labels without provenance.
12. Treat absence of CXR congestion as HF exclusion.
13. Treat No Finding as universal HF exclusion.
14. Force edema vs pneumonia when evidence is mixed.
15. Convert AI score to HF probability.
16. Double-count overlapping CXR evidence.
17. Drop trusted contradictory evidence.
18. Issue autonomous treatment, imaging, procedure, or disposition instructions.
19. Omit doctor review.
