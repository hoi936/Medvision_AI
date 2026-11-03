# ATELECTASIS_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Atelectasis** trong MedVision Hermes.

`Atelectasis` trong VinBigData phải được xử lý trước hết như một **radiographic finding / pathophysiologic state**, không phải một chẩn đoán nguyên nhân hoàn chỉnh.

Phạm vi v1:
- adult chest-radiograph/CT reasoning;
- lobar, segmental/subsegmental, linear, rounded atelectasis terminology;
- mechanism hypotheses;
- acute/critical-care and perioperative clinical context;
- differentiation from pneumonia/consolidation reasoning;
- missing evidence, conflict detection, and safety.

Không tự mở rộng các rule v1 sang pediatric/neonatal atelectasis nếu không có nguồn riêng.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **primary terminology and thoracic-imaging semantics**

### S2 — Marini 2019
**Marini JJ. Acute Lobar Atelectasis. Chest. 2019.**  
PMID: 30528423  
DOI: 10.1016/j.chest.2018.11.014  
Role: **acute lobar atelectasis clinical consequences and context**

### S3 — Cortés Campos & Martínez Rodríguez 2014
**Manifestations of lobar atelectasis on chest X-rays and correlation with computed tomography findings. Radiologia. 2014.**  
PMID: 24252304  
DOI: 10.1016/j.rx.2013.08.003  
Role: **CXR manifestations, volume-loss recognition, CT correlation, obstructive context**

### S4 — Woodring & Reed 1996
**Woodring JH, Reed JC. Types and mechanisms of pulmonary atelectasis. J Thorac Imaging. 1996.**  
PMID: 8820021  
DOI: 10.1097/00005382-199621000-00002  
Role: **classic mechanism taxonomy, direct/indirect radiographic signs, pneumonia guardrail**

### S5 — Zeng et al. 2022
**Zeng C, Lagier D, Lee JW, Vidal Melo MF. Perioperative Pulmonary Atelectasis: Part I. Biology and Mechanisms. Anesthesiology. 2022.**  
PMID: 34499087  
PMCID: PMC9869183  
DOI: 10.1097/ALN.0000000000003943  
Role: **perioperative pathophysiology only**

### S6 — Lagier et al. 2022
**Lagier D, Zeng C, Fernandez-Bustamante A, Vidal Melo MF. Perioperative Pulmonary Atelectasis: Part II. Clinical Implications. Anesthesiology. 2022.**  
PMID: 34710217  
PMCID: PMC9885487  
DOI: 10.1097/ALN.0000000000004009  
Role: **perioperative clinical implications only**

### Source precedence

1. S1 for terminology and imaging definitions.
2. S2/S3 for adult acute/lobar clinical-imaging context.
3. S4 for classic mechanism/sign framework and the pneumonia guardrail.
4. S5/S6 only when perioperative/anesthesia context is actually present.

---

## 2. Definition and imaging semantics

### Supported by S1

Atelectasis is a **partial or complete collapse of the lung**.

S1 describes mechanisms including:
- loss of negative pressure in the pleural space and/or compression of lung parenchyma;
- resorption of air following airway obstruction;
- increased alveolar surface tension, including surfactant dysfunction.

S1 states that atelectatic lung has:
- lower volume;
- higher attenuation than normal lung;
- possible displacement of fissures, bronchi, and vessels;
- possible hyperinflation of adjacent lobes;
- possible obscuration of cardiac or mediastinal interfaces.

### Standardized forms in S1

- **Lobar:** entire pulmonary lobe.
- **Linear:** local plate-/band-like collapse, often in dependent regions.
- **Rounded:** rounded collapsed lung adjacent to pleural disease; may show a comet-tail configuration.
- **Segmental:** anatomical segment.
- **Subsegmental:** anatomical subsegment, often appearing linear.

### Hermes interpretation

A VinBigData `Atelectasis` AI output is:

`RADIOGRAPHIC_EVIDENCE`

It is NOT automatically:
- pneumonia;
- lung cancer;
- mucus plugging;
- foreign-body obstruction;
- postoperative complication;
- pleural-effusion complication;
- respiratory failure;
- an indication for bronchoscopy or any other procedure.

---

## 3. Radiographic evidence and volume loss

### S3
Chest radiography is useful for diagnosing lobar atelectasis and recognizing signs of volume loss. CT can help correlate radiographic findings and identify or evaluate a central obstructive process.

### S4
Classic direct signs include:
- crowding of pulmonary vessels;
- crowding of air bronchograms;
- displacement of interlobar fissures.

Classic indirect signs include:
- pulmonary opacification;
- diaphragm elevation;
- displacement of trachea/heart/mediastinum;
- hilar displacement;
- compensatory hyperexpansion;
- rib approximation.

### Hermes rule

Do not require every classic sign to be present.

If AI reports atelectasis but no localization or volume-loss details are available:
- preserve the finding;
- mark morphology/localization as missing or unknown;
- do not invent a lobe, mechanism, or cause.

---

## 4. Mechanism hypotheses

Mechanisms should be handled as **hypotheses**, not final causes.

### 4.1 Obstructive / resorptive

Supported by S1, S3, S4.

Possible obstructive contexts include:
- foreign body;
- neoplasm;
- other airway obstruction.

### Hermes behavior
If localized/lobar atelectasis is accompanied by evidence suggesting central airway obstruction, an obstructive mechanism may be raised as a differential hypothesis.

Do NOT infer:

`Atelectasis -> lung cancer`

A central tumor is one possible cause, not a default explanation.

### 4.2 Compressive / passive

Supported by S1 and S4.

Potential contexts include:
- pleural effusion;
- pneumothorax;
- space-occupying thoracic processes;
- other compression/hypoventilation contexts.

### Hermes behavior
If pleural effusion or another compressive context is present, Hermes may state:

`compressive mechanism is plausible`

but must not claim proven causality solely from co-occurrence.

### 4.3 Surface-tension / adhesive

Supported by S1 and S4.

Surfactant dysfunction or deficiency can contribute to collapse.

Do not infer this mechanism unless the case context supports it.

### 4.4 Fibrotic / cicatrization

S4 describes cicatrization atelectasis in association with pulmonary fibrosis.

If fibrosis is present, it can support this mechanism hypothesis.

### 4.5 Gravity-dependent / perioperative

S4 describes gravity-dependent atelectasis.

S5/S6 describe perioperative atelectasis as common and mechanistically related to collapsing forces, surface tension, ventilation/anesthesia context, and reduced lung expansion.

Only apply perioperative-specific reasoning when surgery/anesthesia/ventilation context is present.

---

## 5. Clinical consequences

### S2
Clinical consequences of acute lobar collapse can be minor or serious depending on:
- extent;
- mechanism;
- patient vulnerability;
- abruptness of onset;
- hypoxic vasoconstriction;
- compensatory reserve.

### S5
Perioperative atelectasis can:
- impair blood oxygenation;
- reduce lung compliance.

### S6
In perioperative patients, clinical impact may range from gas-exchange/mechanics impairment to more serious postoperative respiratory insufficiency in selected cases.

### Hermes behavior

Do not equate radiographic atelectasis with respiratory failure.

If there is:
- significant hypoxemia;
- worsening respiratory status;
- physiological compromise;

raise:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is a workflow-safety action; it is not a statement that all atelectasis is emergent.

---

## 6. Pneumonia / infection guardrail

### S4
Atelectasis can be misinterpreted as pneumonia.

S4 explicitly states that radiographic atelectasis alone should not establish "atelectatic pneumonia"; clinical signs/symptoms of pneumonia and appropriate microbiological evidence are required for that diagnosis in the framework described by the review.

### Hermes rules

Atelectasis alone:
- does not confirm pneumonia;
- does not confirm bacterial infection.

If fever, cough, inflammatory/infectious evidence, microbiology, or other compatible data are present:
- infection/pneumonia can be evaluated as a separate hypothesis.

Do not convert:
`Atelectasis + opacity`
directly into:
`Pneumonia confirmed`.

### Important nuance

Absence of fever or infectious evidence:
- can reduce support for pneumonia;
- does NOT contradict the atelectasis finding itself.

---

## 7. Obstructing-lesion guardrail

S1/S3/S4 support airway obstruction as a mechanism of atelectasis.

Examples include foreign body or neoplasm.

### Hermes rule

If persistent/localized/lobar atelectasis and other evidence suggest obstruction:
- raise `OBSTRUCTIVE_CAUSE_TO_REVIEW` as a differential/safety-relevant hypothesis;
- preserve uncertainty;
- recommend clinician/radiologist review within the workflow.

Do NOT state:
`central tumor`
or
`lung cancer`
unless case evidence independently supports that hypothesis.

---

## 8. Supporting evidence model

### IMAGE_EVIDENCE
- AI Atelectasis finding;
- localization if available;
- morphology if available;
- signs of volume loss if reported;
- radiologist/manual interpretation;
- CT correlation if available.

### CLINICAL_EVIDENCE
Potentially relevant:
- dyspnea;
- hypoxemia;
- postoperative/anesthesia status;
- immobilization/critical illness;
- infection symptoms;
- airway-obstruction symptoms/history.

### ASSOCIATED_IMAGING_EVIDENCE
Potentially relevant:
- pleural effusion;
- pneumothorax;
- pulmonary fibrosis;
- central obstructive lesion;
- adjacent hyperinflation/structural displacement.

These are contextual evidence, not automatic causes.

---

## 9. Contradicting and conflicting evidence

### Not contradiction by itself
- no fever;
- no cough;
- no dyspnea;
- normal oxygenation.

These may affect etiologic or severity hypotheses but do not by themselves negate the image finding.

### Evidence conflict
Examples:
- AI says atelectasis while trusted human review explicitly says no atelectasis;
- later definitive imaging contradicts the initial finding.

These are **MedVision system-policy conflict rules**.

Emit:

`EVIDENCE_CONFLICT`

and preserve both sources.

---

## 10. Missing evidence

Useful missing fields may include:

- localization/lobe;
- extent;
- signs of volume loss;
- current respiratory status;
- oxygenation/vitals;
- recent surgery/anesthesia;
- mechanical-ventilation context;
- pleural effusion/pneumothorax context;
- infection symptoms/labs;
- obstruction history;
- CT or radiologist confirmation if clinically relevant;
- persistence/chronicity.

Missing data is not negative evidence.

---

## 11. Safety policy

### MedVision workflow safety

If case data indicate:
- significant hypoxemia;
- respiratory distress;
- physiological instability;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do not independently prescribe respiratory therapy, bronchoscopy, recruitment maneuvers, ventilation changes, or surgery.

### Obstructive context

If a central obstruction is suggested by available evidence:
emit:

`OBSTRUCTIVE_CAUSE_TO_REVIEW`

Do not identify a specific malignancy without evidence.

---

## 12. Perioperative evidence boundary

S5 and S6 are high-quality modern sources but are **perioperative** reviews.

Therefore:

Use them only when the case includes:
- recent surgery;
- general anesthesia;
- intraoperative/postoperative context;
- relevant ventilation context.

Do NOT generalize perioperative intervention recommendations to all atelectasis cases.

In MedVision v1, these sources inform:
- mechanism;
- consequence;
- risk context;

not autonomous treatment selection.

---

## 13. AI score interpretation

### MedVision system policy

AI model score is not automatically:
- probability the patient has atelectasis;
- degree of lung collapse;
- clinical severity;
- etiology probability;
- urgency.

Keep separate:

```text
image_model_score
radiographic_finding
mechanism_hypotheses
clinical_consequence
safety_flags
uncertainty
```

Never convert `0.86` into “86% probability of atelectasis” unless the model is explicitly calibrated and validated for that interpretation.

---

## 14. Recommended structured output

```yaml
finding: atelectasis
finding_type: radiographic_finding

image_evidence:
  model_score: null
  localization: unknown
  extent: unknown
  morphology: unknown
  volume_loss_features: []

mechanism_hypotheses:
  obstructive:
    status: unknown
    evidence: []
  compressive:
    status: unknown
    evidence: []
  surface_tension_related:
    status: unknown
    evidence: []
  fibrotic:
    status: unknown
    evidence: []
  gravity_or_perioperative:
    status: unknown
    evidence: []

clinical_context:
  respiratory_status: unknown
  perioperative_context: unknown
  infectious_context: unknown

differential_context:
  pneumonia:
    status: unknown
    evidence: []
  obstructing_lesion:
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

1. Equate AI Atelectasis output with a final diagnosis of cause.
2. Equate atelectasis with pneumonia.
3. Equate atelectasis with lung cancer.
4. Infer mucus plug, foreign body, tumor, or any obstruction without supporting context.
5. Infer perioperative atelectasis without perioperative context.
6. Infer respiratory failure from the image label alone.
7. Infer a specific lobe or morphology when not supplied.
8. Treat absence of fever/cough as evidence against the atelectasis finding itself.
9. Treat coexisting pleural effusion as proof of compressive causation.
10. Convert AI score into patient disease probability without validated calibration.
11. Treat missing information as negative evidence.
12. Issue autonomous treatment/procedure orders.
13. Present the draft assessment as the physician's final diagnosis.
14. Add unsourced medical rules.

---

## 16. Evidence gaps for v2

Potential additions:
- pediatric/neonatal atelectasis;
- postoperative intervention effectiveness by patient subgroup;
- dedicated bronchoscopy indications;
- mucus-plug-specific diagnostic evidence;
- disease-specific obstructive causes;
- detailed CXR mimic studies;
- quantitative atelectasis severity/volume methods;
- ultrasound-specific diagnosis outside perioperative literature.

Do not invent these detailed rules in v1.

---

## 17. Bottom line

```text
Atelectasis AI finding
        ↓
preserve radiographic evidence
        ↓
characterize localization / volume-loss evidence if available
        ↓
evaluate mechanism hypotheses
        ↓
evaluate pneumonia separately
        ↓
evaluate obstructive cause separately
        ↓
check respiratory/perioperative context
        ↓
identify missing/conflicting evidence
        ↓
apply safety flags
        ↓
bounded assessment
        ↓
doctor review required
```
