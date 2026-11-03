# LUNG_OPACITY_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Lung Opacity** trong MedVision Hermes.

`Lung Opacity` trong VinBigData phải được xử lý trước hết như một **broad, nonspecific radiographic descriptor**, không phải là một chẩn đoán nguyên nhân và không phải synonym bắt buộc của `Consolidation`, `Atelectasis`, `Nodule/Mass`, hay một bệnh cụ thể.

Phạm vi v1:
- adult chest-radiograph reasoning;
- `opacity` semantics và giới hạn terminology;
- quan hệ với các VinDr/VinBigData local finding labels khác;
- overlapping-evidence handling để tránh double counting;
- focal vs diffuse / more-specific-pattern context nếu được cung cấp;
- CT/radiologist characterization nếu có;
- context-specific imaging guidance only when the clinical scenario actually matches;
- missing evidence, conflict detection, uncertainty, and doctor review.

Không tự mở rộng v1 thành disease engine cho pneumonia, edema, hemorrhage, tumor, ILD, TB, hoặc các disease-specific pathways đã/đang có skill riêng.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **primary terminology: opacity as a nonspecific descriptor; infiltrate terminology; CT-only use of ground-glass terminology**

### S2 — VinDr-CXR dataset paper 2022
**Nguyen HQ, Lam K, Le LT, et al. VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations. Scientific Data. 2022.**  
PMID: 35858929  
PMCID: PMC9300612  
DOI: 10.1038/s41597-022-01498-w  
Role: **dataset semantics: Lung opacity is a local radiographic finding; disease labels are separate global diagnostic impressions**

### S3 — ACR Appropriateness Criteria: Diffuse Lung Disease
**American College of Radiology. ACR Appropriateness Criteria — Diffuse Lung Disease. New 2021.**  
URL: https://acsearch.acr.org/docs/3157911/Narrative/  
Role: **diffuse-pattern imaging context only**

### S4 — ACR Appropriateness Criteria: Acute Respiratory Illness in Immunocompetent Patients
**American College of Radiology. ACR Appropriateness Criteria — Acute Respiratory Illness in Immunocompetent Patients. Revised 2024.**  
URL: https://acsearch.acr.org/docs/69446/Narrative/  
Role: **acute symptomatic clinical context only; not a generic Lung Opacity rule**

### S5 — Duggan et al. 2021
**Duggan GE, Reicher JJ, Liu Y, Tse D, Shetty S. Improving reference standards for validation of AI-based radiography. Br J Radiol. 2021.**  
PMID: 34142868  
PMCID: PMC8248225  
DOI: 10.1259/bjr.20210435  
Role: **AI/radiologist reference-standard caution and inter-reader variability**

### Source precedence

1. S1 for thoracic-imaging terminology.
2. S2 for VinDr/VinBigData label semantics.
3. S3/S4 only when their specific clinical scenario is actually present.
4. S5 for AI/reference-standard uncertainty, not for disease diagnosis.

---

## 2. Core semantic rule

### S1

`Opacity` refers to a **focal or diffuse nonspecific area of increased attenuation**.

It is a general descriptor and **does not indicate the nature of the condition causing the opacity**.

Fleischner 2024 also notes that `infiltrate` is an obsolete/nonrecommended term that historically has sometimes been used synonymously with opacity.

### Hermes interpretation

A VinBigData `Lung Opacity` output is:

`NONSPECIFIC_RADIOGRAPHIC_OPACITY_EVIDENCE`

It is NOT automatically:
- pneumonia;
- consolidation;
- atelectasis;
- pulmonary edema;
- pulmonary hemorrhage;
- lung tumor;
- tuberculosis;
- interstitial lung disease;
- ground-glass opacity;
- any final disease diagnosis.

---

## 3. Dataset semantics: finding != diagnosis

### S2

VinDr-CXR separates:
- **local labels** representing radiographic abnormalities/findings; and
- **global labels** representing suspected disease-level diagnostic impressions.

`Lung opacity` is a local label.

Examples of global disease labels in the dataset include:
- Lung tumor;
- Pneumonia;
- Tuberculosis;
- COPD;
- Other diseases;
- No finding.

### Hermes rule

Do not transform:

`Lung Opacity -> Pneumonia`

or:

`Lung Opacity -> Lung tumor`

simply because a disease can produce an opacity.

The local finding and any disease hypothesis must remain separate evidence objects.

---

## 4. Relationship to Consolidation

### S1

`Opacity` is an umbrella descriptor.

`Consolidation` has a more specific imaging definition involving replacement of alveolar air by fluid or other material, producing increased attenuation; it is still itself non-etiologic.

### Hermes behavior

If both are positive:

`Lung Opacity + Consolidation`

preserve both model outputs.

But do NOT count them as two independent disease-confirming pieces of evidence if they refer to the same radiographic region/process.

Emit where appropriate:

`OVERLAPPING_FINDING_EVIDENCE`

This flag is **MEDVISION_SYSTEM_POLICY**, not a Fleischner term.

A more-specific finding may refine the broad opacity description, but the broad Lung Opacity result is not silently deleted.

---

## 5. Relationship to Atelectasis

Atelectasis can manifest with increased pulmonary opacity and volume-loss signs, but it has a more specific definition and mechanism framework.

### Hermes behavior

If:

`Lung Opacity + Atelectasis`

preserve both findings.

If the evidence plausibly refers to the same region/process:
- identify overlap;
- do not double count as two independent etiologic evidences.

Do NOT infer:
- pneumonia;
- obstruction;
- severity

from co-occurrence alone.

This overlap handling is `MEDVISION_SYSTEM_POLICY`.

---

## 6. Relationship to Nodule/Mass

A nodule or mass is a focal lesion with more specific morphology/size terminology than generic opacity.

### Hermes behavior

If:

`Lung Opacity + Nodule/Mass`

and both plausibly refer to the same focal region:
- preserve both classifier outputs;
- use the more-specific focal-lesion characterization when available;
- flag possible overlap;
- do not count broad opacity as independent evidence of malignancy.

Do NOT infer lung cancer.

---

## 7. Relationship to Infiltration

### S1

Fleischner 2024 considers `infiltrate` obsolete/nonrecommended terminology and notes historical synonymy with opacity.

### S2

VinDr-CXR nevertheless contains `Infiltration` and `Lung opacity` as distinct local labels in its annotation schema.

### Hermes behavior

Because the dataset exposes both classes:
- preserve both outputs when both are positive;
- do not silently collapse one into the other at ingestion;
- mark semantic overlap where appropriate;
- do not count them as independent disease evidence merely because both classifiers are positive.

Do not use the obsolete radiologic term issue to rewrite the upstream canonical label.

---

## 8. Ground-glass terminology guardrail

### S1

Fleischner 2024 states that although ground-glass was historically described on radiographs, the term has been specifically defined for **CT** and should only be applied in the context of CT.

### Hermes behavior

Do NOT convert a CXR `Lung Opacity` finding into:

`ground-glass opacity`

unless CT evidence explicitly provides that characterization.

If CT states ground-glass opacity:
- preserve it as CT morphology;
- do not infer etiology from GGO alone.

---

## 9. Focal vs diffuse characterization

`Opacity` may be focal or diffuse [S1].

### Hermes behavior

If localization/distribution is explicitly provided, record:
- focal;
- multifocal;
- diffuse;
- unilateral/bilateral;
- lobe/zone when supplied.

Do NOT invent distribution.

Distribution can guide which more-specific reasoning branch becomes relevant but does not establish etiology by itself.

---

## 10. Diffuse-lung-disease context

### S3 scope

ACR Diffuse Lung Disease addresses cases where **diffuse lung disease is clinically suspected**.

The ACR document discusses chest radiography and CT/HRCT in evaluation of suspected diffuse lung disease.

### Hermes behavior

Only when the case actually contains:
- diffuse opacity/pattern evidence; and
- a clinician-supported or otherwise appropriate diffuse-lung-disease context;

may Hermes identify:

`DIFFUSE_LUNG_DISEASE_CHARACTERIZATION_RELEVANT`

as a clinician-facing evaluation consideration.

Do NOT:
- turn every Lung Opacity into ILD;
- automatically recommend HRCT for every opacity;
- issue an imaging order.

---

## 11. Acute respiratory illness context

### S4 scope

ACR Acute Respiratory Illness in Immunocompetent Patients is structured by clinical risk scenario.

Imaging appropriateness differs depending on:
- physical examination;
- vital signs;
- risk factors;
- initial radiographic findings;
- the specific clinical question.

### Hermes behavior

Use S4 only when an acute respiratory illness scenario is actually present.

Do NOT create a universal rule:

`Lung Opacity -> CT`

or:

`Lung Opacity -> pneumonia`

When acute respiratory symptoms are present, opacity remains imaging evidence and must be integrated with the clinical syndrome.

---

## 12. AI/reference-standard uncertainty

### S5

Duggan et al. studied chest-radiograph findings including `airspace opacity` and showed that individual-reader agreement and reproducibility are imperfect; multi-reader adjudication can improve reference-standard quality.

### Hermes behavior

The AI output is not ground truth.

If a trusted human review or later definitive imaging disagrees:
- preserve both;
- emit `EVIDENCE_CONFLICT`.

Do not silently prefer AI.

This finding is particularly suitable for conservative uncertainty handling because broad opacity categories can have reader variability.

---

## 13. Supporting evidence model

### IMAGE_EVIDENCE
- AI `Lung Opacity`;
- model score;
- localization/bounding box if supplied;
- focal vs diffuse if supplied;
- radiologist/manual interpretation;
- CT characterization if available.

### MORE_SPECIFIC_IMAGE_EVIDENCE
Potentially relevant:
- Consolidation;
- Atelectasis;
- Nodule/Mass;
- Pleural effusion;
- ILD;
- Pulmonary fibrosis;
- Infiltration;
- other canonical findings.

### CLINICAL_EVIDENCE
Potentially relevant:
- acute respiratory symptoms;
- fever/infectious evidence;
- hypoxemia;
- chronic respiratory symptoms;
- known cardiac/oncologic/inflammatory context.

These affect disease hypotheses but do not redefine the generic opacity itself.

---

## 14. Overlap / double-counting policy

This section is **MEDVISION_SYSTEM_POLICY**.

When broad and more-specific findings coexist:

```text
Lung Opacity
+
more-specific finding
```

Hermes should:

1. preserve every upstream AI output;
2. identify likely semantic/imaging overlap;
3. prefer the more-specific finding for pattern characterization;
4. avoid counting overlapping labels as independent disease-confirming evidence;
5. keep uncertainty if regional correspondence is unknown.

Suggested flag:

`OVERLAPPING_FINDING_EVIDENCE`

This is an evidence-fusion rule, not a medical diagnosis.

---

## 15. Contradicting and conflicting evidence

### Not contradiction by itself
- no fever;
- no cough;
- no dyspnea;
- normal routine labs.

These may affect disease hypotheses but do not automatically negate the image finding.

### Direct conflict
Examples:
- AI says Lung Opacity while trusted human review explicitly says no pulmonary opacity;
- CT or later definitive imaging indicates no corresponding abnormality.

Emit:

`EVIDENCE_CONFLICT`

and preserve both sources.

---

## 16. Missing evidence

Potential missing fields:
- localization;
- focal vs diffuse distribution;
- relation to other positive findings;
- clinical symptoms;
- time course;
- radiologist interpretation;
- CT characterization when clinically relevant;
- physiologic stability/oxygenation.

Missing data is not negative evidence.

---

## 17. Safety policy

A generic Lung Opacity is not automatically an emergency.

If independent clinical data show:
- severe respiratory distress;
- significant hypoxemia;
- physiologic instability;
- another acute high-risk syndrome;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not autonomously issue:
- antibiotics;
- diuretics;
- steroids;
- CT orders;
- invasive procedures;
- other disease-specific therapy.

---

## 18. AI score interpretation

The AI score is not automatically:
- probability of pneumonia;
- probability of cancer;
- probability of edema;
- probability of ILD;
- clinical severity;
- disease-specific urgency.

Keep separate:

```text
image_model_score
nonspecific_opacity_finding
more_specific_imaging_patterns
clinical_disease_hypotheses
overlap_flags
uncertainty
```

Never convert `0.89` into:
- “89% probability of pneumonia”;
- “89% probability of lung cancer”;
- another disease probability.

---

## 19. Recommended structured output

```yaml
finding: lung_opacity
finding_type: nonspecific_radiographic_descriptor

image_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  focality: unknown
  radiologist_interpretation: unknown

specific_pattern_context:
  consolidation: unknown
  atelectasis: unknown
  nodule_mass: unknown
  infiltration: unknown
  ild_or_fibrosis: unknown
  other: []

overlap:
  detected: false
  flags: []
  notes: []

ct_characterization:
  available: false
  morphology: unknown
  distribution: unknown

clinical_context:
  acute_respiratory_illness: unknown
  diffuse_lung_disease_context: unknown

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

## 20. Prohibited inferences

Hermes MUST NOT:

1. Equate Lung Opacity with pneumonia.
2. Equate Lung Opacity with lung tumor/cancer.
3. Equate Lung Opacity automatically with Consolidation.
4. Equate Lung Opacity automatically with Atelectasis.
5. Convert CXR Lung Opacity into ground-glass opacity without CT evidence.
6. Treat Infiltration + Lung Opacity as two independent disease-confirming evidences by default.
7. Double count Lung Opacity and a more-specific co-finding when they plausibly represent the same process.
8. Infer disease from distribution alone.
9. Automatically order CT for every Lung Opacity.
10. Convert AI score into an underlying-disease probability.
11. Treat missing data as negative evidence.
12. Issue autonomous treatment/procedure orders.
13. Present the broad finding as a final physician diagnosis.
14. Add unsourced disease-specific rules.

---

## 21. Evidence gaps for v2

Potential additions:
- explicit region-overlap computation between bounding boxes;
- quantitative overlap/de-duplication logic;
- dedicated `Infiltration` compatibility layer;
- disease-specific opacity patterns only through separate disease skills;
- pediatric opacity reasoning;
- immunocompromised-host pathways;
- projection/technical-artifact rules;
- longitudinal opacity-change semantics.

Do not invent these detailed rules in v1.

---

## 22. Bottom line

```text
Lung Opacity AI finding
        ↓
preserve as nonspecific radiographic descriptor
        ↓
characterize focal/diffuse/location if available
        ↓
look for more-specific co-findings
        ↓
OVERLAPPING_FINDING_EVIDENCE when appropriate
        ↓
do not double count
        ↓
integrate clinical / CT / human-review context
        ↓
keep disease hypotheses separate
        ↓
identify missing/conflicting evidence
        ↓
bounded assessment
        ↓
doctor review required
```
