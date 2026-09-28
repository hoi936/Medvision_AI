# CARDIOMEGALY_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Cardiomegaly** trong MedVision Hermes.

`Cardiomegaly` trong VinBigData phải được xử lý trước hết như một **chest-radiograph finding of an enlarged cardiac silhouette / increased apparent cardiac size**, không phải là chẩn đoán heart failure, reduced ejection fraction, cardiomyopathy, hay một bệnh tim cụ thể.

Phạm vi v1:
- adult chest-radiograph interpretation;
- cardiothoracic ratio (CTR) semantics;
- projection/technical limitations, especially PA vs AP/portable;
- heart-failure hypothesis integration;
- echocardiographic/structural correlation when available;
- pericardial/technical alternatives for an enlarged silhouette;
- missing evidence, conflict detection, uncertainty, and safety.

Không tự mở rộng các rule này sang pediatric/neonatal CTR nếu chưa có nguồn riêng.

---

## 1. Evidence hierarchy

### S1 — Truszkiewicz et al. 2021
**Truszkiewicz K, Poręba R, Gać P. Radiological Cardiothoracic Ratio in Evidence-Based Medicine. J Clin Med. 2021.**  
PMID: 34066783  
PMCID: PMC8125954  
DOI: 10.3390/jcm10092016  
Role: **primary CTR definition, PA interpretation, projection limitations, and cardiac-silhouette caveats**

### S2 — Soares Torres et al. 2021
**Soares Torres F, Eifer DA, Sanchez Tijmes F, Nguyen ET, Hanneman K. Diagnostic performance of chest radiography measurements for the assessment of cardiac chamber enlargement. CMAJ. 2021.**  
PMID: 34750176  
PMCID: PMC8584372  
DOI: 10.1503/cmaj.210083  
Role: **diagnostic limitations of the conventional CTR 0.50 threshold against cardiac MRI**

### S3 — AHA/ACC/HFSA Heart Failure Guideline 2022
**Heidenreich PA, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. Circulation. 2022.**  
PMID: 35363499  
DOI: 10.1161/CIR.0000000000001063  
Role: **heart-failure clinical integration, CXR limitations, and transthoracic echocardiography role**

### S4 — Badgett et al. 1996
**Badgett RG, Mulrow CD, Otto PM, Ramírez G. How well can the chest radiograph diagnose left ventricular dysfunction? J Gen Intern Med. 1996.**  
PMID: 8945695  
DOI: 10.1007/BF02599031  
Role: **classic evidence that cardiomegaly/CXR alone cannot adequately confirm or exclude LV dysfunction**

### S5 — Knudsen et al. 2004
**Knudsen CW, Omland T, Clopton P, et al. Diagnostic value of B-Type natriuretic peptide and chest radiographic findings in patients with acute dyspnea. Am J Med. 2004.**  
PMID: 15006584  
DOI: 10.1016/j.amjmed.2003.10.028  
Role: **integration of BNP, CXR findings, and clinical context in acute dyspnea**

### S6 — Sahin et al. 2018
**Sahin H, Chowdhry DN, Olsen A, Nemer O, Wahl L. Is there any diagnostic value of anteroposterior chest radiography in predicting cardiac chamber enlargement? Int J Cardiovasc Imaging. 2019.**  
PMID: 30143921  
Role: **AP portable CXR magnification/diagnostic limitations relative to echocardiography and CT**

### Source precedence

1. S1 for CTR definition and projection/technical semantics.
2. S2 for modern evidence on the limited diagnostic value of a fixed CTR 0.50 threshold for true chamber enlargement.
3. S3 for current heart-failure diagnostic integration and TTE role.
4. S4 for stable evidence on CXR limitations for LV dysfunction.
5. S5 for acute-dyspnea integration of natriuretic peptide and CXR.
6. S6 specifically for AP portable projection limitations.

---

## 2. Core semantic rule

A VinBigData `Cardiomegaly` AI output is:

`RADIOGRAPHIC_EVIDENCE_OF_APPARENT_CARDIAC_ENLARGEMENT`

It is NOT automatically:
- heart failure;
- reduced ejection fraction;
- left ventricular dilation;
- cardiomyopathy;
- volume overload;
- pulmonary edema;
- pericardial effusion;
- valvular disease;
- an indication for treatment.

The image label should not be converted directly into a clinical diagnosis.

---

## 3. Cardiothoracic ratio semantics

### Supported by S1

CTR is the ratio of the maximum transverse cardiac dimension to the maximum transverse thoracic dimension on a **posteroanterior (PA)** chest radiograph.

A conventional value above `0.50` is commonly treated as supporting radiographic cardiac enlargement.

S1 also emphasizes:
- CTR should be based on PA radiographs;
- interpretation in other projections has important limitations;
- increased CTR does not directly describe cardiac function;
- an enlarged cardiac silhouette can be difficult to distinguish from enlargement related to pericardial disease.

### Supported by S2

The traditional CTR cutpoint of `0.50` has limited diagnostic performance for true cardiac chamber enlargement when cardiac MRI is used as the reference.

In the PA subgroup of S2, a 0.50 threshold showed only moderate sensitivity and specificity.

### Hermes rule

If:
- projection is explicitly PA; and
- a measured CTR is explicitly provided;

then `CTR > 0.50` may be recorded as:

`RADIOGRAPHIC_CARDIAC_ENLARGEMENT_SUPPORTED`

But it must NOT be translated into:
- definite chamber enlargement;
- reduced EF;
- HF;
- cardiomyopathy.

If projection is unknown:
- do not assume PA;
- do not apply the classic `0.50` threshold as if technique were validated.

If CTR is not provided:
- do not invent or calculate it from an AI class score.

---

## 4. PA vs AP / portable projection

### S1 and S6

AP portable radiographs can misrepresent apparent heart size because of technical/geometric factors.

S6 found AP radiographs yielded higher apparent CTR/heart measurements than CT-based measures and that a standard `0.50` cutoff on AP radiographs had poor specificity for cardiac chamber enlargement.

### Hermes behavior

For:
- `AP`;
- `portable AP`;
- `supine AP`;
- or projection not reliably known;

increase technical uncertainty.

Emit where appropriate:

`PROJECTION_LIMITATION`

Do NOT apply the classic PA `CTR > 0.50` interpretation unchanged to an AP image.

Do NOT change the VinBigData AI finding to negative solely because projection is AP; instead preserve the model evidence and qualify its reliability.

---

## 5. Heart-failure branch

### S3

Chest X-ray is useful in patients with signs/symptoms of heart failure because it can assess:
- cardiomegaly;
- pulmonary venous congestion;
- interstitial/alveolar edema;
- alternative cardiopulmonary causes.

However, S3 states that:
- CXR findings other than congestion are meaningful for HF only in clinical context;
- cardiomegaly may be absent in acute HF;
- CXR has limited sensitivity/specificity and should not be the sole determinant of the presence or cause of HF.

### Hermes behavior

Cardiomegaly can support an HF hypothesis only when integrated with relevant case evidence such as:
- dyspnea;
- orthopnea/PND if supplied;
- edema/JVP/other clinician findings if supplied;
- pulmonary congestion/edema imaging findings;
- BNP/NT-proBNP if supplied;
- echocardiographic structural/functional abnormalities if supplied.

Do NOT output:

`Cardiomegaly -> heart failure confirmed`

A patient can have HF without cardiomegaly, particularly in acute presentations [S3].

---

## 6. Natriuretic peptide integration

### S5

In patients presenting with acute dyspnea, BNP and chest-radiographic findings provided complementary diagnostic information for HF.

S5 demonstrated that BNP and findings such as cardiomegaly/congestion each added information beyond history/clinical variables.

### Hermes behavior

If BNP or NT-proBNP is provided:
- use it as contextual evidence for or against an HF hypothesis;
- do not use it as standalone proof;
- do not encode a universal diagnostic threshold in this skill v1.

Reason:
- this skill is about `Cardiomegaly`;
- disease-specific biomarker thresholds depend on population/context and should be governed by dedicated HF reasoning if added later.

---

## 7. Left-ventricular dysfunction / EF guardrail

### S4

Cardiomegaly on CXR had limited diagnostic performance for reduced EF/LV dysfunction, and neither cardiomegaly nor redistribution alone adequately confirmed or excluded LV dysfunction in usual clinical settings.

### S2

CTR is an imperfect surrogate for true chamber enlargement.

### Hermes rule

Never infer from `Cardiomegaly` alone:
- reduced EF;
- preserved EF;
- LV dilation;
- LV hypertrophy;
- systolic dysfunction;
- diastolic dysfunction.

If EF or chamber measurements are not supplied:
mark them `unknown`.

---

## 8. Echocardiography / structural correlation

### S3

Transthoracic echocardiography (TTE) provides information on:
- cardiac structure;
- cardiac function;
- myocardium;
- valves;
- pericardium.

### Hermes behavior

If TTE data are available:
- keep CXR cardiomegaly as image evidence;
- use TTE as more direct evidence for structure/function;
- do not force agreement between CXR silhouette and TTE chamber measurements.

Examples:
- CXR cardiomegaly + normal EF does not invalidate the radiographic silhouette finding.
- CXR cardiomegaly + normal chamber dimensions should increase uncertainty about true chamber enlargement and raise technical/pericardial alternatives when supported.
- normal EF does not exclude HF in general.

Do not invent echocardiographic findings.

---

## 9. Pericardial / silhouette alternative

### S1

An enlarged cardiac silhouette/CTR may not reliably distinguish true cardiac enlargement from pericardial disease such as effusion.

### Hermes behavior

If known pericardial effusion is present:
- it can be considered as a possible contributor to enlarged cardiac silhouette;
- do not equate the CXR finding with myocardial chamber enlargement.

Do NOT diagnose pericardial effusion from cardiomegaly alone.

---

## 10. Relationship to other VinBigData findings

Potentially relevant co-findings:
- Pleural effusion;
- Lung Opacity;
- Consolidation;
- Infiltration;
- Aortic enlargement;
- other signs of pulmonary congestion if represented elsewhere.

### Hermes rule

Co-occurrence can change support for an HF or volume-overload hypothesis but does not prove causality.

Examples:
- Cardiomegaly + Pleural effusion does not automatically equal HF.
- Cardiomegaly + Consolidation does not automatically equal cardiogenic pulmonary edema.
- Cardiomegaly alone does not establish congestion.

Dataset co-occurrence is not causal clinical knowledge.

---

## 11. Supporting evidence model

### IMAGE_EVIDENCE
- AI Cardiomegaly finding;
- model score;
- projection if supplied;
- CTR if explicitly measured;
- radiologist/manual interpretation;
- congestion/edema co-findings if available.

### CLINICAL_EVIDENCE
Potentially relevant:
- dyspnea;
- orthopnea/PND;
- peripheral edema;
- known cardiac disease;
- acute vs chronic presentation;
- blood pressure/hemodynamic context.

### LAB_EVIDENCE
Potentially relevant:
- BNP/NT-proBNP;
- other disease-directed labs if supplied.

### CARDIAC_IMAGING_EVIDENCE
Potentially relevant:
- TTE chamber dimensions;
- EF;
- structural abnormalities;
- valve abnormalities;
- pericardial findings.

---

## 12. Contradicting and conflicting evidence

### Not contradiction by itself
- no dyspnea;
- normal BNP/NT-proBNP;
- normal EF.

These may reduce support for an HF hypothesis but do not automatically negate an enlarged cardiac silhouette.

### Direct evidence conflict
Examples:
- AI says Cardiomegaly while trusted human CXR interpretation explicitly says heart size is normal;
- later repeat radiographic assessment under reliable technique directly contradicts the initial finding.

Emit:

`EVIDENCE_CONFLICT`

and preserve both sources.

### Modality/technical discordance

CXR cardiomegaly with normal TTE chamber dimensions is not automatically a hard contradiction because:
- modalities assess different properties;
- projection/magnification may matter;
- pericardial/silhouette factors may matter.

Report the discordance explicitly rather than silently choosing one source.

---

## 13. Missing evidence

Potential missing fields:
- PA vs AP projection;
- portable/supine technique;
- CTR measurement;
- dyspnea/orthopnea/edema context;
- signs of pulmonary congestion;
- BNP/NT-proBNP where HF is under consideration;
- TTE results;
- EF/chamber measurements;
- pericardial findings;
- hemodynamic/oxygenation status.

Missing data is not negative evidence.

---

## 14. Safety policy

If case data show:
- acute severe dyspnea;
- significant hypoxemia;
- physiological/hemodynamic instability;
- another acute cardiopulmonary safety concern;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is a MedVision workflow policy.

Do not independently prescribe:
- diuretics;
- vasodilators;
- inotropes;
- oxygen/ventilation changes;
- invasive procedures.

---

## 15. AI score interpretation

AI model score is not automatically:
- probability of true chamber enlargement;
- probability of HF;
- probability of reduced EF;
- clinical severity;
- treatment urgency.

Keep separate:

```text
image_model_score
radiographic_cardiac_enlargement
projection_reliability
heart_failure_hypothesis
cardiac_structure_function_evidence
safety_flags
uncertainty
```

Never convert `0.93` into “93% chance of heart failure” or “93% probability the patient has cardiomegaly” unless validated calibration explicitly supports that interpretation.

---

## 16. Recommended structured output

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
  priority: routine|elevated|high
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true

citations: []
```

---

## 17. Prohibited inferences

Hermes MUST NOT:

1. Equate Cardiomegaly AI output with heart failure.
2. Equate cardiomegaly with reduced EF.
3. Equate cardiomegaly with cardiomyopathy.
4. Infer LV dilation/LVH from CXR cardiomegaly alone.
5. Treat `CTR > 0.50` as proof of true chamber enlargement.
6. Apply the classic PA `0.50` CTR threshold unchanged to AP/portable radiographs.
7. Infer HF from cardiomegaly without clinical context.
8. Infer pericardial effusion from cardiomegaly alone.
9. Treat normal EF as proof that the radiographic finding is false.
10. Treat absence of cardiopulmonary symptoms as contradiction of the image finding itself.
11. Convert AI score into disease probability without validated calibration.
12. Treat missing information as negative evidence.
13. Issue autonomous treatment/procedure orders.
14. Present the draft assessment as the physician's final diagnosis.
15. Add unsourced medical rules.

---

## 18. Evidence gaps for v2

Potential additions:
- dedicated valvular-heart-disease branches;
- chamber-specific enlargement signs on CXR;
- dedicated pericardial-effusion reasoning;
- congenital heart disease;
- pediatric CTR;
- longitudinal change in cardiac silhouette;
- disease-specific BNP/NT-proBNP thresholds;
- HFpEF/HFrEF/HFmrEF reasoning;
- CT/MRI-specific heart-size rules.

Do not invent these detailed rules in v1.

---

## 19. Bottom line

```text
Cardiomegaly AI finding
        ↓
preserve radiographic evidence
        ↓
check PA vs AP / technical reliability
        ↓
interpret CTR only when actually available and appropriate
        ↓
evaluate HF hypothesis separately
        ↓
integrate natriuretic peptide / congestion if available
        ↓
integrate TTE structure/function if available
        ↓
consider pericardial/technical alternatives
        ↓
identify missing/conflicting evidence
        ↓
apply safety flags
        ↓
bounded assessment
        ↓
doctor review required
```
