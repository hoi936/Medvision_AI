# CONSOLIDATION_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Consolidation** trong MedVision Hermes.

`Consolidation` trong VinBigData phải được xử lý trước hết như một **radiographic descriptor / imaging finding**, không phải là một chẩn đoán nguyên nhân.

Phạm vi v1:
- adult chest radiograph / CT semantics;
- acute vs chronic etiologic reasoning ở mức tổng quát;
- pneumonia, pulmonary edema, và pulmonary hemorrhage là các nhánh differential quan trọng;
- missing evidence, conflict detection, uncertainty, và safety;
- không tự động chọn điều trị.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **primary terminology and imaging semantics**

### S2 — Kjeldsberg et al. 2002
**Kjeldsberg KM, Oh K, Murray KA, Cannon G. Radiographic approach to multifocal consolidation. Semin Ultrasound CT MR. 2002.**  
PMID: 12465686  
DOI: 10.1016/S0887-2171(02)90018-1  
Role: **broad radiographic differential and acute-vs-chronic context**

### S3 — ATS/IDSA CAP Guideline 2019
**Metlay JP, et al. Diagnosis and Treatment of Adults with Community-acquired Pneumonia. Am J Respir Crit Care Med. 2019.**  
PMID: 31573350  
PMCID: PMC6812437  
DOI: 10.1164/rccm.201908-1581ST  
Role: **community-acquired pneumonia clinical context only**

### S4 — Barile 2020
**Barile M. Pulmonary Edema: A Pictorial Review of Imaging Manifestations and Current Understanding of Mechanisms of Disease. Eur J Radiol Open. 2020.**  
PMID: 33163585  
PMCID: PMC7607415  
DOI: 10.1016/j.ejro.2020.100274  
Role: **pulmonary edema differential branch**

### S5 — Reisman et al. 2021
**Reisman S, Chung M, Bernheim A. A Review of Clinical and Imaging Features of Diffuse Pulmonary Hemorrhage. AJR Am J Roentgenol. 2021.**  
PMID: 33826359  
DOI: 10.2214/AJR.20.23399  
Role: **pulmonary hemorrhage differential branch**

### Source precedence

1. S1 for the definition and imaging meaning of `consolidation`.
2. S2 for broad differential structure and acute/chronic temporal context.
3. S3 only for the pneumonia branch.
4. S4 only for the pulmonary-edema branch.
5. S5 only for the pulmonary-hemorrhage branch.

---

## 2. Definition and imaging semantics

### Supported by S1

Consolidation is increased attenuation of lung parenchyma caused by evacuation of alveolar air and replacement by fluid or other material.

On radiographs:
- it appears as a homogeneous increase in attenuation.

On CT:
- it is an opacity that obscures underlying bronchi and vessels;
- patent bronchi within consolidation can produce air bronchograms.

Most importantly, S1 states that **consolidation is a descriptor and does not indicate the pathologic nature of the underlying condition**.

### Hermes interpretation

A VinBigData `Consolidation` output is:

`RADIOGRAPHIC_EVIDENCE`

It is NOT automatically:
- pneumonia;
- bacterial infection;
- pulmonary edema;
- pulmonary hemorrhage;
- malignancy;
- organizing pneumonia;
- pulmonary infarction;
- an indication for antibiotics or another therapy.

---

## 3. Differential framework

### Supported by S2

Multifocal consolidation has numerous causes.

For acute symptoms (days to weeks), important/common categories include:
- edema;
- pneumonia;
- hemorrhage.

For more chronic symptoms (weeks to months), differential categories can include:
- alveolar proteinosis;
- neoplastic processes;
- granulomatous/inflammatory disorders;
- lipoid pneumonia;
- other conditions.

### Hermes rule

Use temporal context as one piece of evidence.

Do NOT infer etiology solely from:
- acute vs chronic duration;
- consolidation distribution;
- one AI label.

If timing is missing:
`temporal_context: unknown`

is valid.

---

## 4. Pneumonia / infection branch

### S3 scope

The ATS/IDSA guideline applies to adults with community-acquired pneumonia in an appropriate clinical/radiographic context.

It should not be interpreted as saying that every pulmonary consolidation is pneumonia.

### Hermes behavior

When consolidation is accompanied by compatible evidence such as:
- fever;
- cough / sputum;
- respiratory symptoms;
- inflammatory or microbiological evidence;
- clinician-documented infectious syndrome;

pneumonia can become a supported hypothesis.

However:

`Consolidation -> Pneumonia`

is prohibited.

A consolidation finding without compatible clinical evidence remains etiologically nonspecific.

Do not use the consolidation finding alone to:
- confirm bacterial infection;
- select antibiotics;
- infer pathogen.

---

## 5. Pulmonary edema branch

### S4

Pulmonary edema results from extravascular fluid accumulation in the pulmonary interstitium/alveoli and can arise through multiple mechanisms, including hydrostatic and permeability-related processes.

Its radiographic manifestations are variable and may include airspace opacification/consolidation in appropriate contexts.

### Hermes behavior

If consolidation is accompanied by compatible evidence such as:
- pulmonary congestion pattern;
- edema-related imaging findings;
- cardiac/volume-overload context;
- supportive clinical/laboratory evidence;

pulmonary edema may become a hypothesis.

Do NOT infer:
`Consolidation -> Cardiogenic pulmonary edema`

from the consolidation label alone.

Do not autonomously select diuretics or other treatment.

---

## 6. Pulmonary hemorrhage branch

### S5

Diffuse pulmonary hemorrhage has nonspecific clinical and imaging findings.

Chest radiography commonly shows alveolar opacification, and integration of:
- clinical;
- radiologic;
- laboratory;
- pathologic information

is important for diagnosis and etiologic identification.

### Hermes behavior

If consolidation is accompanied by evidence such as:
- hemoptysis;
- falling hemoglobin/anemia context;
- relevant autoimmune/coagulation/medication context;
- clinician concern for alveolar hemorrhage;

pulmonary hemorrhage may become a differential hypothesis.

Do NOT require hemoptysis to be present before considering hemorrhage.

Do NOT diagnose diffuse alveolar hemorrhage from imaging alone.

If hemorrhage is strongly suspected with physiologic compromise:
emit `HIGH_PRIORITY_CLINICAL_REVIEW`.

---

## 7. Air bronchogram semantics

S1 notes that patent bronchi within consolidation may appear as air bronchograms.

### Hermes rule

An air bronchogram:
- can support morphology of airspace consolidation;
- does NOT by itself determine etiology.

Do NOT infer pneumonia solely from an air bronchogram.

---

## 8. Relationship to other VinBigData findings

Potentially coexisting findings include:
- Infiltration;
- Lung Opacity;
- Pleural effusion;
- Cardiomegaly;
- Atelectasis;
- Pneumothorax;
- other findings.

### Hermes rule

Co-occurrence can modify hypotheses but must not be treated as causal proof.

Examples:
- Consolidation + Pleural effusion does not automatically mean parapneumonic effusion.
- Consolidation + Cardiomegaly does not automatically prove cardiogenic edema.
- Consolidation + Atelectasis does not automatically prove infection.

Dataset co-occurrence is not a medical causal rule.

---

## 9. Supporting evidence model

### IMAGE_EVIDENCE
- AI Consolidation finding;
- localization/distribution if explicitly supplied;
- air bronchogram if reported;
- radiologist/manual interpretation;
- CT correlation if available.

### CLINICAL_EVIDENCE
Potentially relevant:
- fever;
- cough/sputum;
- dyspnea;
- chest pain;
- hemoptysis;
- acute vs chronic symptom duration;
- cardiac/volume-overload context;
- malignancy/inflammatory history.

### LAB_EVIDENCE
Potentially relevant:
- inflammatory markers;
- microbiology;
- hemoglobin trend;
- disease-specific laboratory evidence.

No single nonspecific lab value should be converted into a definitive cause without context.

---

## 10. Contradicting and conflicting evidence

### Not contradiction by itself
- no fever;
- no cough;
- no hemoptysis;
- normal inflammatory markers.

These may reduce support for a specific branch but do not by themselves negate the consolidation finding.

### Evidence conflict
Examples:
- AI reports consolidation but trusted human review explicitly reports no consolidation;
- later definitive imaging contradicts the initial finding.

These are `MEDVISION_SYSTEM_POLICY` conflict rules.

Emit:

`EVIDENCE_CONFLICT`

and preserve both sources.

---

## 11. Missing evidence

Potential missing fields include:
- localization/distribution;
- symptom duration;
- fever/infectious symptoms;
- microbiology/inflammatory data if infection is suspected;
- cardiac/volume status if edema is suspected;
- hemoglobin/hemoptysis context if hemorrhage is suspected;
- CT or radiologist correlation where clinically relevant;
- physiologic stability / oxygenation.

Missing information is not negative evidence.

---

## 12. Safety policy

If case data show:
- significant hypoxemia;
- respiratory distress;
- physiological instability;
- strong concern for major pulmonary hemorrhage or another acute high-risk process;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do not independently prescribe:
- antibiotics;
- diuretics;
- steroids/immunosuppression;
- ventilation changes;
- invasive diagnostic procedures.

---

## 13. AI score interpretation

AI model score is not automatically:
- probability the patient has pneumonia;
- probability of edema;
- probability of hemorrhage;
- disease severity;
- treatment urgency.

Keep separate:

```text
image_model_score
radiographic_finding
etiologic_hypotheses
clinical_evidence
safety_flags
uncertainty
```

Never convert `0.91` into “91% probability of pneumonia” or “91% probability of consolidation in the patient” unless validated calibration explicitly supports that interpretation.

---

## 14. Recommended structured output

```yaml
finding: consolidation
finding_type: radiographic_descriptor

image_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  air_bronchogram: unknown

temporal_context:
  acute_subacute_chronic: unknown

etiologic_hypotheses:
  pneumonia_or_infection:
    status: unknown
    evidence: []
  pulmonary_edema:
    status: unknown
    evidence: []
  pulmonary_hemorrhage:
    status: unknown
    evidence: []
  inflammatory_or_organizing_process:
    status: unknown
    evidence: []
  neoplastic_or_other:
    status: unknown
    evidence: []

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

## 15. Prohibited inferences

Hermes MUST NOT:

1. Equate Consolidation AI output with pneumonia.
2. Equate consolidation with bacterial infection.
3. Infer pathogen from the consolidation pattern alone.
4. Equate consolidation with cardiogenic pulmonary edema.
5. Equate consolidation with pulmonary hemorrhage.
6. Infer malignancy from consolidation alone.
7. Infer cause solely from an air bronchogram.
8. Treat absence of fever/cough as contradiction of consolidation itself.
9. Treat absence of hemoptysis as exclusion of pulmonary hemorrhage.
10. Infer a specific distribution/location when not supplied.
11. Convert AI score into disease probability without validated calibration.
12. Treat missing data as negative evidence.
13. Issue autonomous treatment/procedure orders.
14. Present the assessment as a final physician diagnosis.
15. Add unsourced medical rules.

---

## 16. Evidence gaps for v2

Potential future additions:
- dedicated organizing-pneumonia consensus/review;
- pulmonary infarction/embolism-related consolidation;
- aspiration-related consolidation;
- immunocompromised-host differential;
- malignancy presenting as persistent consolidation;
- pediatric consolidation;
- distribution-specific algorithms;
- quantitative severity methods.

Do not invent these rules in v1.
