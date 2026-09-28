# PNEUMOTHORAX_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet cho **Pneumothorax** trong MedVision Hermes.

**Phạm vi của bộ nguồn v1:** chủ yếu là **adult spontaneous pneumothorax**, đặc biệt primary spontaneous pneumothorax (PSP), cùng thuật ngữ hình ảnh ngực chuẩn hóa.

**Không tự mở rộng các rule dưới đây sang:**
- traumatic pneumothorax,
- iatrogenic pneumothorax,
- pediatric pneumothorax,
- neonatal pneumothorax,
- ventilated/ICU pneumothorax,

trừ khi có nguồn riêng hỗ trợ.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role in Hermes: **terminology / radiographic finding semantics / structured reporting**

### S2 — British Thoracic Society 2023
**British Thoracic Society Guideline for pleural disease. Thorax. 2023.**  
PMID: 37553157 (summary article)  
Guideline full text: Thorax 2023;78(Suppl 3):s1  
Role in Hermes: **current adult spontaneous pneumothorax clinical context, physiological compromise, management context, recurrence/follow-up**

### S3 — Joint ERS/EACTS/ESTS 2024
**Walker S, et al. Joint ERS/EACTS/ESTS clinical practice guidelines on adults with spontaneous pneumothorax. Eur Respir J. 2024.**  
PMID: 38806203  
DOI: 10.1183/13993003.00797-2023  
Role in Hermes: **current international evidence-based clinical practice guidance**

### S4 — ERS Task Force 2015
**Tschopp JM, et al. ERS task force statement: diagnosis and treatment of primary spontaneous pneumothorax. Eur Respir J. 2015.**  
PMID: 26113675  
DOI: 10.1183/09031936.00219214  
Role in Hermes: **supporting historical/current clinical context for PSP and symptom-driven assessment**

### S5 — BTS 2010
**MacDuff A, Arnold A, Harvey J; BTS Pleural Disease Guideline Group. Management of spontaneous pneumothorax: British Thoracic Society Pleural Disease Guideline 2010. Thorax. 2010.**  
PMID: 20696690  
DOI: 10.1136/thx.2010.136986  
Role in Hermes: **historical supporting guideline**

### Source precedence rule

When sources disagree:

1. Prefer S2/S3 for current clinical practice.
2. Prefer S1 for thoracic-imaging terminology.
3. Use S4 as supporting background.
4. Use S5 as historical context only and **do not allow it to override newer 2023/2024 guidance**.

---

## 2. Definition

### Supported fact
Pneumothorax refers to **air in the pleural space**.

- S1 illustrates pneumothorax on chest radiography/CT as air in the pleural space.
- S2 describes pneumothorax as air in the pleural space.
- S2 further defines *spontaneous* pneumothorax as occurring without trauma or a causative medical intervention.

### Hermes interpretation
`Pneumothorax` from the image model must first be treated as a **radiographic finding / imaging evidence**, not as a complete etiologic diagnosis.

The finding alone does **not** establish:
- primary vs secondary spontaneous pneumothorax,
- traumatic vs iatrogenic cause,
- tension physiology,
- clinical stability,
- treatment requirement.

Those require additional context.

---

## 3. Radiographic evidence

### Supported by S1
The Fleischner glossary provides standardized thoracic-imaging terminology and illustrates pneumothorax on chest radiography and CT as air in the pleural space.

### Safe v1 reasoning rule
When the image AI outputs `pneumothorax`:

- classify it as **IMAGE_EVIDENCE**;
- preserve laterality/localization if the AI service provides it;
- preserve model score separately from clinical confidence;
- do not infer etiology or physiological severity from the label alone.

### Not yet sufficiently sourced for v1
This five-source set is **not sufficient to encode a comprehensive chest-X-ray mimic/differential list** (for example technical artifacts that can mimic pneumothorax).

Therefore:
- do not invent radiographic mimic rules;
- add a dedicated radiology review/reference before encoding them.

---

## 4. Clinical context

### Current-guideline principles

S2 and S3 support a **symptom- and clinical-stability-aware approach** to adult spontaneous pneumothorax.

S2 states that conservative management can be considered in adults with primary spontaneous pneumothorax who are asymptomatic or minimally symptomatic and have no physiological compromise.

S3 similarly gives a conditional recommendation for conservative care in minimally symptomatic, clinically stable PSP.

S4 states that management of first-episode PSP is driven by symptoms rather than pneumothorax size alone.

### Hermes reasoning consequences

#### Rule C1 — Symptoms matter
Hermes should explicitly look for:
- breathlessness/dyspnoea,
- chest pain,
- physiological compromise / instability indicators available in the case.

#### Rule C2 — Absence of symptoms is NOT hard contradiction
A patient can have spontaneous pneumothorax with minimal or no symptoms.

Therefore:
- `no dyspnoea` alone must not negate an image finding;
- `no chest pain` alone must not negate an image finding.

#### Rule C3 — Image magnitude alone must not determine urgency
Hermes must not convert:
- image AI score,
- apparent image size,
- model confidence

directly into a management decision.

Current guidelines emphasize clinical symptoms and stability.

---

## 5. Etiologic classification context

### Supported context

Spontaneous pneumothorax is defined in S2 as occurring in the absence of trauma or a causative medical intervention.

S4 focuses on **primary spontaneous pneumothorax**, occurring in people without known underlying lung disease, and identifies smoking as an important risk factor for PSP.

### Missing data Hermes should seek if clinically relevant

To interpret a pneumothorax finding, useful missing context includes:

- recent chest trauma;
- recent thoracic procedure / central line / intervention;
- known underlying lung disease;
- previous pneumothorax;
- smoking history;
- current respiratory symptoms;
- available vital signs / oxygenation / physiological stability.

These fields help avoid incorrectly treating all pneumothoraces as PSP.

---

## 6. Supporting evidence model

Hermes should separate evidence by source.

### IMAGE_EVIDENCE
- AI pneumothorax finding.
- Laterality/localization if available.
- Any radiologist/manual finding if present.

### CLINICAL_EVIDENCE
Potential supporting context can include respiratory/chest symptoms, but symptoms are not mandatory for the imaging finding to be real.

### HISTORY_EVIDENCE
- previous pneumothorax;
- smoking history in PSP context;
- underlying pulmonary disease;
- recent trauma/procedure (important for classification).

### PHYSIOLOGIC_EVIDENCE
- available evidence of clinical stability or compromise.

### Important constraint
Supporting clinical evidence can increase **clinical concern/consistency**, but Hermes must not transform evidence aggregation into an unvalidated numerical probability of disease.

---

## 7. Contradicting evidence

For v1, use conservative contradiction semantics.

### Not a contradiction by itself
- absence of dyspnoea;
- absence of chest pain;
- clinically mild presentation.

Guidelines explicitly recognize minimally symptomatic/asymptomatic PSP.

### Potential inconsistency requiring review
- AI suggests pneumothorax but a trusted radiologist interpretation explicitly states no pneumothorax;
- image finding conflicts with a later definitive imaging study.

These two examples are **MedVision evidence-consistency policy**, not direct rules from S1–S5. They must be labeled as system policy, not medical guideline statements.

---

## 8. Missing evidence

For a pneumothorax case, Hermes should identify which of the following are unavailable rather than assuming them:

- symptoms (especially breathlessness/chest pain);
- physiological stability;
- oxygenation/vital-sign data if available in the clinical workflow;
- trauma/procedural history;
- known underlying lung disease;
- previous pneumothorax;
- smoking history;
- radiologist review if the system workflow includes it.

### Output language
Use:
- `missing_data`
- `unknown`
- `not provided`

Do not convert missing data into negative evidence.

---

## 9. Safety / red-flag policy

### Source-supported principle
S2 distinguishes minimally symptomatic/stable presentations from those with significant symptoms or physiological compromise, and identifies tension pneumothorax / significant physiological compromise as high-risk clinical contexts.

### Hermes safety behavior
If case data indicate possible:
- significant breathlessness,
- physiological compromise/instability,
- tension-pneumothorax context,

Hermes should:

1. set a **HIGH_PRIORITY_CLINICAL_REVIEW** flag;
2. state that prompt clinician assessment is required;
3. avoid autonomous treatment instructions;
4. avoid delaying review while waiting for optional evidence.

### Important
Hermes is a decision-support system. It does not independently prescribe drainage, surgery, aspiration, or other interventions.

---

## 10. Management knowledge — allowed use

S2 and S3 contain management recommendations, but in MedVision v1 these should be used as **context for reasoning and safety**, not as autonomous treatment orders.

Safe use:
- understand that symptoms and stability matter;
- understand that not every radiographic PSP requires the same intervention;
- recognize recurrence/history as clinically relevant.

Unsafe use:
- automatically issue a procedure order;
- choose a specific intervention without clinician review;
- infer management solely from model score.

---

## 11. Recurrence / history

S2 and S3 recognize recurrence prevention as an important management dimension.

Hermes should therefore record:
- first episode vs recurrent episode,
- ipsilateral/contralateral history if available.

For v1 this information contributes to the assessment context but must not directly trigger a treatment order.

---

## 12. Differential diagnosis and radiographic mimics

### Evidence gap in current source pack
The selected five sources are strong for:
- terminology,
- spontaneous pneumothorax guidance,
- clinical stability,
- management context.

They are **not a complete evidence pack for radiographic mimics/differential diagnosis**.

Therefore v1 must output:

`radiographic_mimics: NOT_ENCODED_IN_V1`

until a dedicated thoracic-radiology differential source is added.

---

## 13. Associated VinBigData findings

Do not hard-code associations such as:
- pneumothorax + pleural effusion,
- pneumothorax + atelectasis,
- etc.

unless supported by a specific clinical/radiologic source or learned only as dataset co-occurrence for research.

Dataset co-occurrence must not be presented as a causal medical rule.

---

## 14. AI-score interpretation

### MedVision system policy
The image model score is an **AI model output**, not automatically:
- disease probability,
- clinical severity,
- treatment urgency.

Hermes must preserve these separately:

```text
image_model_score
clinical_evidence_strength
clinical_uncertainty
safety_flags
```

Never rewrite an AI score such as `0.92` as “92% chance the patient has pneumothorax” unless the model has been explicitly calibrated and validated for that interpretation.

---

## 15. Recommended structured output for pneumothorax reasoning

```yaml
finding: pneumothorax
finding_type: radiographic_finding

image_evidence:
  present: true|false|unknown
  model_score: null
  localization: null

clinical_evidence:
  supporting: []
  not_supporting: []
  unknown: []

classification_context:
  spontaneous_possible: unknown
  primary_vs_secondary: unknown
  trauma_or_procedure: unknown

physiologic_status:
  stable: unknown
  compromise_signs: []

missing_data: []

conflicts: []

safety:
  priority: routine|elevated|high
  reasons: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true

citations: []
```

---

## 16. Prohibited inferences

Hermes MUST NOT:

1. Equate an AI image label with a final diagnosis.
2. Convert AI model score to disease probability without validated calibration.
3. Infer primary spontaneous pneumothorax without checking trauma/procedure and underlying lung disease context.
4. Infer tension pneumothorax solely from the `pneumothorax` image label.
5. Infer clinical stability from missing symptoms/vitals.
6. Treat absence of symptoms as proof the image finding is false.
7. Generate autonomous treatment orders.
8. Use BTS 2010 to override BTS 2023 or ERS/EACTS/ESTS 2024.
9. Invent radiographic mimics not present in the evidence pack.
10. Present a draft assessment as the final physician diagnosis.

---

## 17. Evidence gaps for v2

Before expanding this skill, add dedicated sources for:

- chest-radiograph signs and technical mimics;
- traumatic pneumothorax;
- iatrogenic pneumothorax;
- pediatric pneumothorax;
- ICU/mechanically ventilated patients;
- tension-pneumothorax imaging/clinical criteria;
- diagnostic performance of CXR vs ultrasound/CT, if relevant to MedVision.

---

## 18. Bottom line for Hermes

Pneumothorax in MedVision should be handled as:

```text
AI radiographic finding
        ↓
verify clinical context
        ↓
check symptoms + physiological status
        ↓
check etiology/classification context
        ↓
identify missing evidence
        ↓
check safety flags
        ↓
produce bounded assessment
        ↓
doctor review required
```

The skill must remain evidence-grounded and must not turn image-model output into an autonomous diagnosis or treatment decision.
