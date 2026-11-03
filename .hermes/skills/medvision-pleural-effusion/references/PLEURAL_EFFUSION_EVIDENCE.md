# PLEURAL_EFFUSION_EVIDENCE.md

## 0. Scope

Evidence sheet v1 for the VinBigData finding **Pleural effusion** in MedVision Hermes.

Treat the AI output first as a **radiographic finding**, not an etiologic diagnosis. v1 focuses on adults, especially undiagnosed unilateral pleural effusion, pleural-fluid classification, and high-level etiologic branches.

## 1. Sources

- **S1 — Fleischner Society 2024**: Bankier AA, et al. *Fleischner Society: Glossary of Terms for Thoracic Imaging*. Radiology. 2024. PMID 38411514. DOI 10.1148/radiol.232558. Primary role: imaging terminology.
- **S2 — BTS Pleural Disease Guideline 2023**: Roberts ME, et al. *British Thoracic Society Guideline for pleural disease*. Thorax. 2023. PMID 37433578. DOI 10.1136/thorax-2022-219784. Primary role: current adult pleural-disease guidance.
- **S3 — Porcel et al. 2015**: *The diagnosis of pleural effusions*. Expert Rev Respir Med. PMID 26449328. DOI 10.1586/17476348.2015.1098535. Primary role: diagnostic framework.
- **S4 — Light 2013**: *The Light criteria: the beginning and why they are useful 40 years later*. Clin Chest Med. PMID 23411053. DOI 10.1016/j.ccm.2012.11.006. Primary role: transudate/exudate classification and limitations.
- **S5 — ATS/STS/STR 2018**: Feller-Kopman DJ, et al. *Management of Malignant Pleural Effusions*. Am J Respir Crit Care Med. PMID 30272503. DOI 10.1164/rccm.201807-1415ST. Primary role: malignant pleural effusion branch only.

Source precedence: S2 for current general clinical guidance; S1 for imaging terminology; S3 for general diagnostic framework; S4 for Light criteria; S5 only for malignant pleural effusion context.

## 2. Definition and imaging semantics

S1 defines pleural effusion as **excessive pleural fluid**. Causes may include mechanical factors, edema, infection, inflammation, or malignancy.

Radiographic/CT features described by S1:
- small effusions may blunt the costophrenic angles and have a meniscus-shaped appearance;
- larger effusions may appear as homogeneous dependent opacities;
- CT may characterize fluid, loculation, pleural thickening, and hyperemia.

### Hermes rule

A VinBigData `Pleural effusion` output is `RADIOGRAPHIC_EVIDENCE`.

It is **not automatically** heart failure, infection, malignancy, tuberculosis, transudate, exudate, or an indication for a procedure.

## 3. Core diagnostic principle

S2 and S3 support integrating:
- clinical history and examination;
- imaging;
- serum laboratory data when relevant;
- pleural-fluid characteristics/analysis when available.

Hermes must not infer a single cause from the X-ray label alone.

## 4. Etiologic hypothesis branches

### 4.1 Heart failure

S2 states serum NT-proBNP can support heart failure as a cause of unilateral pleural effusion when heart failure is clinically suspected, but it should **not be used in isolation** because multiple conditions may coexist.

Hermes may output `heart-failure-related effusion: supported hypothesis` only when the broader case context supports it.

### 4.2 Pleural infection / parapneumonic effusion

For **suspected pleural infection**, S2 uses pleural-fluid pH as an important risk-stratification parameter:
- pH `<= 7.2`: high risk of complicated parapneumonic effusion / pleural infection;
- pH `> 7.2 and < 7.4`: intermediate risk; LDH and other clinical/imaging features become relevant;
- pH `>= 7.4`: lower risk in this specific decision context.

S2 notes pleural-fluid LDH `>900 IU/L` as relevant in the intermediate pH range, together with other supporting features.

Hermes may emit `PLEURAL_INFECTION_HIGH_RISK` and `HIGH_PRIORITY_CLINICAL_REVIEW`, but must **not autonomously order drainage, antibiotics, or another procedure**.

### 4.3 Malignancy

S2 supports pleural-fluid cytology as an initial test when secondary pleural malignancy is suspected. Negative cytology does **not** by itself exclude malignancy when suspicion remains.

Imaging can support suspicion, but negative imaging does not necessarily exclude malignancy.

S5 applies only to the malignant pleural effusion branch and must not be generalized to all pleural effusions.

### 4.4 Tuberculous pleural effusion

S2 gives context-dependent roles to pleural-fluid ADA and/or IFN-gamma and emphasizes appropriate diagnostic context. Hermes must not apply a universal ADA-only rule.

### 4.5 Other causes

S2 and S3 describe a broad differential including systemic, inflammatory, infectious, malignant, and other conditions. If available evidence is insufficient, `etiology remains undetermined` is valid.

## 5. Light criteria

Only evaluate when the required paired pleural-fluid and serum values are available.

Biochemically classify as **exudative by Light criteria** if any one is true:

1. pleural-fluid protein / serum protein `> 0.5`
2. pleural-fluid LDH / serum LDH `> 0.6`
3. pleural-fluid LDH `> 2/3` of the laboratory upper limit of normal serum LDH

Otherwise the pattern is consistent with a transudate by Light criteria.

### Limitation

S4 describes Light criteria as a useful starting point but reports that a meaningful fraction of true transudates can be misclassified as exudates, especially in patients receiving diuretics.

Use output labels such as:
- `EXUDATIVE_BY_LIGHT_CRITERIA`
- `TRANSUDATIVE_BY_LIGHT_CRITERIA`

Do not treat either label as a final etiologic diagnosis.

## 6. Evidence buckets

### IMAGE_EVIDENCE
- AI pleural-effusion finding;
- laterality/extent only if explicitly provided;
- radiologist/manual findings when available.

### CLINICAL_EVIDENCE
Potentially relevant context includes respiratory symptoms, infection context, cardiac disease, malignancy history, TB context, and autoimmune context.

### SERUM_LAB_EVIDENCE
Potentially relevant: serum protein, serum LDH, serum NT-proBNP, and other disease-directed tests.

### PLEURAL_FLUID_EVIDENCE
Potentially relevant: protein, LDH, pH, glucose, cytology, microbiology, ADA/IFN-gamma when clinically appropriate.

## 7. Conflict and missing-data semantics

Absence of dyspnea or fever does not negate the radiographic finding.

If AI output conflicts with trusted human review or later definitive imaging, emit `EVIDENCE_CONFLICT` and preserve both sources. This is a MedVision system policy.

Potential missing data include symptoms/physiology, cardiac/infection/malignancy/TB context, paired protein/LDH values, pleural-fluid pH/glucose when infection is suspected, cytology when malignancy is suspected, and microbiology when infection is suspected.

Missing data is not negative evidence.

## 8. Safety policy

If significant respiratory compromise or physiological instability is present, emit `HIGH_PRIORITY_CLINICAL_REVIEW` as a MedVision workflow-safety rule.

If suspected pleural infection has high-risk pleural-fluid features from S2, emit `PLEURAL_INFECTION_HIGH_RISK` and require prompt clinician review.

Hermes must not independently order thoracentesis, drainage, indwelling catheter, pleurodesis, surgery, antibiotics, or anticancer therapy.

## 9. AI score semantics

The image-model score is not automatically:
- patient disease probability;
- etiology probability;
- fluid volume;
- severity;
- treatment urgency.

Never rewrite `0.87` as “87% probability the patient has pleural effusion” unless the model has been specifically calibrated and validated for that interpretation.

## 10. Recommended output

```yaml
finding: pleural_effusion
finding_type: radiographic_finding

image_evidence:
  model_score: null
  laterality: unknown
  size_or_extent: unknown

clinical_context:
  symptoms: []
  physiologic_status: unknown

pleural_fluid:
  available: false
  light_criteria:
    evaluable: false
    classification: unknown
  infection_risk:
    evaluable: false
    status: unknown

etiologic_hypotheses:
  heart_failure: {status: unknown, evidence: []}
  infection: {status: unknown, evidence: []}
  malignancy: {status: unknown, evidence: []}
  tuberculosis: {status: unknown, evidence: []}
  other: {status: undetermined}

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

## 11. Prohibited inferences

Hermes MUST NOT:
1. convert the AI finding directly into an etiologic diagnosis;
2. equate pleural effusion with heart failure, infection, malignancy, or TB;
3. use NT-proBNP alone to confirm etiology;
4. compute Light criteria from incomplete/unpaired data;
5. treat Light classification as a final disease diagnosis;
6. treat negative cytology as definitive exclusion of malignancy;
7. convert model score to patient disease probability without validated calibration;
8. treat missing information as negative evidence;
9. infer clinical stability from missing data;
10. generate autonomous treatment/procedure orders;
11. present a draft assessment as the physician's final diagnosis.

## 12. Evidence gaps for v2

Not yet encoded in detail:
- pediatric effusion;
- chylothorax;
- hemothorax;
- hepatic hydrothorax;
- renal-failure-related effusion;
- pulmonary-embolism-associated effusion;
- detailed thoracic-ultrasound phenotypes;
- detailed radiographic mimics/technical pitfalls.
