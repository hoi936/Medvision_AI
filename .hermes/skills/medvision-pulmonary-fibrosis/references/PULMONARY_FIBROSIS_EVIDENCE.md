# PULMONARY_FIBROSIS_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Pulmonary fibrosis** trong MedVision Hermes.

`Pulmonary fibrosis` trong VinBigData/VinDr-CXR phải được xử lý trước hết như một **local radiographic finding compatible with chronic fibrotic/scarring change**, không phải là chẩn đoán idiopathic pulmonary fibrosis (IPF), usual interstitial pneumonia (UIP), progressive pulmonary fibrosis (PPF), hay một căn nguyên cụ thể.

Phạm vi v1:
- adult chest-radiograph reasoning;
- CXR fibrosis finding vs HRCT fibrosis characterization;
- overlap với ILD, Lung Opacity, Infiltration;
- fibrotic morphology on HRCT when explicitly supplied;
- UIP/IPF guardrails;
- PPF evaluability only from adequate longitudinal evidence;
- disease-cause uncertainty;
- missing evidence, conflict detection, doctor review.

Không tự mở rộng v1 thành:
- IPF treatment engine;
- CTD-ILD diagnostic pathway;
- hypersensitivity-pneumonitis pathway;
- occupational/post-infectious fibrosis attribution;
- sarcoidosis;
- drug/radiation fibrosis;
- autonomous HRCT, biopsy, bronchoscopy, or treatment ordering.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **standard thoracic-imaging terminology for fibrosis-related CT descriptors**

### S2 — VinDr-CXR dataset paper 2022
**Nguyen HQ, Lam K, Le LT, et al. VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations. Scientific Data. 2022.**  
PMID: 35858929  
PMCID: PMC9300612  
DOI: 10.1038/s41597-022-01498-w  
Role: **dataset semantics: Pulmonary fibrosis and ILD are distinct local labels, separate from global disease-level labels**

### S3 — ATS/ERS/JRS/ALAT IPF + PPF Guideline 2022
**Raghu G, Remy-Jardin M, Richeldi L, et al. Idiopathic Pulmonary Fibrosis (an Update) and Progressive Pulmonary Fibrosis in Adults: An Official ATS/ERS/JRS/ALAT Clinical Practice Guideline. Am J Respir Crit Care Med. 2022.**  
PMID: 35486072  
PMCID: PMC9851481  
DOI: 10.1164/rccm.202202-0399ST  
Role: **UIP/IPF separation and PPF criteria**

### S4 — Rodriguez et al. 2022
**Rodriguez K, Ashby CL, Varela VR, Sharma A. High-Resolution Computed Tomography of Fibrotic Interstitial Lung Disease. Semin Respir Crit Care Med. 2022.**  
PMID: 36307108  
DOI: 10.1055/s-0042-1755563  
Role: **HRCT features of fibrotic ILD and multidisciplinary context**

### S5 — Lederer et al. 2024
**Lederer C, Storman M, Tarnoki AD, Tarnoki DL, Margaritopoulos GA, Prosch H. Imaging in the diagnosis and management of fibrosing interstitial lung diseases. Breathe (Sheff). 2024.**  
PMID: 38746908  
PMCID: PMC11091715  
DOI: 10.1183/20734735.0006-2024  
Role: **HRCT signs/patterns of fibrosis and the importance of clinical context**

### S6 — ERS/ATS Interstitial Pneumonia Classification 2025
**Ryerson CJ, Adegunsoye A, Piciucchi S, et al. Update of the international multidisciplinary classification of the interstitial pneumonias: an ERS/ATS statement. Eur Respir J. 2025.**  
PMID: 40774805  
DOI: 10.1183/13993003.00158-2025  
Role: **fibrotic vs non-fibrotic classification and diagnostic-confidence context**

### Source precedence

1. S3 for IPF/PPF rules.
2. S6 for current interstitial-pneumonia classification.
3. S4/S5 for HRCT fibrotic morphology.
4. S1 for standardized terminology.
5. S2 for dataset provenance/taxonomy.

---

## 2. Core semantic rule

A VinBigData `Pulmonary fibrosis` output is:

`RADIOGRAPHIC_EVIDENCE_COMPATIBLE_WITH_CHRONIC_FIBROTIC_OR_SCARRING_CHANGE`

It is NOT automatically:
- idiopathic pulmonary fibrosis;
- usual interstitial pneumonia;
- progressive pulmonary fibrosis;
- fibrotic NSIP;
- CTD-ILD;
- hypersensitivity pneumonitis;
- occupational fibrosis;
- post-infectious fibrosis;
- drug/radiation fibrosis;
- any specific etiology.

---

## 3. Dataset semantics: local finding != disease diagnosis

### S2

VinDr-CXR separates:
- 22 local labels representing localized findings;
- 6 global labels representing suspected disease-level diagnostic impressions.

`Pulmonary fibrosis` and `Interstitial lung disease (ILD)` are both local labels.

### Hermes behavior

Preserve:

```text
finding = "Pulmonary fibrosis"
```

as upstream provenance.

Do not transform the local label into:
- IPF;
- UIP;
- a disease subtype;
- a specific cause.

---

## 4. Relationship to ILD

### S2 / S6

VinDr-CXR represents `ILD` and `Pulmonary fibrosis` as distinct local findings.

ERS/ATS 2025 classifies interstitial disorders into fibrotic and non-fibrotic categories, so fibrosis is a characteristic of some interstitial disorders rather than a synonym for all ILD.

### Hermes behavior

If:

`ILD + Pulmonary fibrosis`

are both positive:
- preserve both upstream results;
- allow Pulmonary fibrosis to refine fibrosis status within a broader interstitial-pattern context;
- identify overlap when both plausibly describe the same process;
- do not count them as two independent confirmations of IPF or another disease.

Emit where appropriate:

`OVERLAPPING_FINDING_EVIDENCE`

This is `MEDVISION_SYSTEM_POLICY`.

---

## 5. CXR vs HRCT separation

### S4 / S5

Radiography may suggest fibrotic lung disease, but HRCT provides detailed characterization of parenchymal fibrosis.

HRCT fibrotic features can include:
- reticulation;
- traction bronchiectasis;
- traction bronchiolectasis;
- honeycombing;
- architectural distortion;
- volume loss.

### Hermes behavior

From CXR `Pulmonary fibrosis` alone, do NOT infer:
- honeycombing;
- traction bronchiectasis;
- traction bronchiolectasis;
- UIP;
- specific HRCT distribution;
- exact fibrosis extent.

If no CT/HRCT data are supplied:

```text
hrct_characterization: unavailable
specific_fibrotic_pattern: unknown
```

If fibrotic ILD is genuinely suspected, Hermes may identify:

`HRCT_CHARACTERIZATION_RELEVANT`

as a clinician-facing evaluation consideration.

Do not autonomously order HRCT.

---

## 6. Honeycombing guardrail

### S1 / S4 / S5

Honeycombing is a CT fibrosis descriptor and must be interpreted with other fibrotic features and distribution.

### Hermes behavior

Never infer:

`Pulmonary fibrosis CXR -> honeycombing`

If HRCT explicitly reports honeycombing:
- preserve it as strong fibrotic imaging evidence;
- record the reported distribution if supplied;
- do not automatically diagnose IPF.

Do not confuse honeycombing with other cystic/emphysematous appearances.

---

## 7. Traction bronchiectasis / bronchiolectasis

### S4 / S5

Traction bronchiectasis and bronchiolectasis are important HRCT signs associated with fibrotic remodeling.

### Hermes behavior

Record them only when:
- CT/HRCT or trusted radiology interpretation explicitly supplies them.

Do not infer them from:
- CXR model label;
- AI score;
- generic `Pulmonary fibrosis`.

---

## 8. UIP / IPF guardrail

### S3

IPF is a clinical diagnosis involving an appropriate clinical context and radiological/histopathological criteria.

UIP/probable-UIP are imaging-pattern categories used in IPF evaluation.

### Hermes behavior

Never infer:

`Pulmonary fibrosis -> UIP`

or:

`Pulmonary fibrosis -> IPF`

If HRCT explicitly reports:
- UIP;
- probable UIP;
- another fibrotic pattern;

preserve that imaging pattern separately from the disease diagnosis.

Do not output `IPF confirmed` unless a trusted clinician/pathology/MDD source explicitly supplies it.

---

## 9. Etiology guardrail

Pulmonary fibrosis can occur in multiple disease contexts.

### Hermes behavior

Do NOT assign cause from the fibrosis finding alone.

Potential cause-related evidence may include, only if supplied:
- connective-tissue-disease context;
- environmental/occupational exposure;
- medication/radiation exposure;
- prior infection;
- family/genetic history;
- autoimmune serology;
- pathology;
- multidisciplinary diagnosis.

Without such evidence:

`etiology: unknown`

Do not use co-findings such as pleural thickening alone to infer an occupational exposure.

---

## 10. PPF — progressive pulmonary fibrosis

### S3

In an adult with ILD of known or unknown etiology **other than IPF** and radiological evidence of pulmonary fibrosis, PPF requires at least **two of three** domains occurring within the past year with no alternative explanation:

1. worsening respiratory symptoms;
2. physiological progression;
3. radiological progression.

S3 further defines accepted physiological/radiological criteria.

### Hermes behavior

Only evaluate PPF when adequate longitudinal evidence is explicitly supplied.

If only:
- one CXR;
- one CT;
- one AI output;
- fibrosis without longitudinal evidence;

then:

```text
ppf_evaluable: false
```

Do NOT infer PPF from chronic fibrosis alone.

Do not autonomously select antifibrotic therapy.

---

## 11. Relationship to Lung Opacity

If:

`Pulmonary fibrosis + Lung Opacity`

are positive:
- preserve both;
- fibrosis may be the more-specific chronic-pattern finding when they plausibly describe the same region/process;
- identify overlap;
- avoid double counting.

Do NOT infer a particular disease from the overlap.

---

## 12. Relationship to Infiltration

`Infiltration` is a legacy nonspecific label.

If:

`Pulmonary fibrosis + Infiltration`

are positive:
- preserve both for provenance;
- fibrosis is the more-specific chronic structural finding;
- do not let `Infiltration` independently amplify the same fibrosis hypothesis when overlap is likely.

If Lung Opacity is also present:
- preserve all;
- avoid triple counting.

---

## 13. Relationship to Consolidation

If:

`Pulmonary fibrosis + Consolidation`

are both positive:
- preserve both;
- they may represent coexisting or overlapping processes;
- do not infer acute exacerbation of ILD/fibrosis automatically.

Acute exacerbation requires additional clinical and temporal evidence and is not encoded as a direct two-label rule in v1.

---

## 14. Relationship to Pleural Thickening

If:

`Pulmonary fibrosis + Pleural thickening`

are both positive:
- preserve both findings;
- do not infer asbestos exposure, asbestosis, or another occupational disease from co-occurrence alone.

Exposure and etiologic attribution require independent evidence.

---

## 15. Multidisciplinary context

### S4 / S5 / S6

Fibrotic ILD diagnosis depends on integration of:
- imaging pattern;
- clinical context;
- serology;
- exposure history;
- pathology when available;
- multidisciplinary evaluation.

### Hermes behavior

Maintain separate:
- radiographic fibrosis;
- HRCT morphology/pattern;
- ILD context;
- cause hypothesis;
- diagnostic confidence;
- documented multidisciplinary diagnosis.

Do not fabricate MDD consensus.

---

## 16. Supporting evidence model

### CXR_EVIDENCE
- AI `Pulmonary fibrosis`;
- model score;
- localization/distribution if supplied;
- radiologist interpretation;
- prior CXR comparison.

### HRCT_EVIDENCE
Potentially relevant:
- reticulation;
- traction bronchiectasis;
- traction bronchiolectasis;
- honeycombing;
- architectural distortion;
- volume loss;
- GGO;
- reported UIP/probable-UIP/other fibrotic pattern;
- distribution.

### CLINICAL_EVIDENCE
Potentially relevant:
- dyspnea/cough;
- symptom duration;
- oxygenation;
- autoimmune/CTD context;
- occupational/environmental exposure;
- medication/radiation exposure;
- family history.

### PHYSIOLOGIC_EVIDENCE
Potentially relevant:
- FVC;
- DLCO;
- longitudinal PFT changes.

### DEFINITIVE_CONTEXT
- pathology;
- trusted clinical diagnosis;
- documented multidisciplinary diagnosis.

---

## 17. Conflict detection

Examples:
- AI reports Pulmonary fibrosis while trusted human CXR review explicitly reports no fibrotic change;
- CXR AI is positive but high-quality HRCT reports no corresponding pulmonary fibrosis.

Emit:

`EVIDENCE_CONFLICT`

Preserve both.

HRCT is more specific for fibrotic morphology, but the upstream AI result remains in the audit trail.

---

## 18. Missing evidence

Potential missing fields:
- HRCT characterization;
- fibrosis extent/distribution;
- ILD context;
- symptoms/chronicity;
- PFTs;
- serial imaging;
- exposure history;
- CTD/autoimmune context;
- medication/radiation context;
- family history;
- pathology/MDD if a specific diagnosis is being considered.

Missing evidence is not negative evidence.

---

## 19. Safety policy

Pulmonary fibrosis finding alone is not automatically an emergency.

If independent evidence shows:
- severe/new respiratory distress;
- major hypoxemia;
- rapid physiological deterioration;
- another acute high-risk syndrome;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not autonomously prescribe:
- antifibrotics;
- corticosteroids;
- immunosuppression;
- oxygen/ventilation changes;
- HRCT;
- bronchoscopy;
- biopsy;
- surgery;
- other procedures/treatment.

---

## 20. AI score interpretation

AI model score is not automatically:
- probability of IPF;
- probability of UIP;
- probability of PPF;
- probability of fibrotic ILD;
- fibrosis extent;
- severity;
- progression rate.

Keep separate:

```text
image_model_score
cxr_fibrosis_finding
hrct_fibrotic_features
hrct_pattern
etiology_hypothesis
progression_status
diagnostic_confidence
uncertainty
```

Never convert `0.92` into:
- “92% probability of IPF”;
- “92% probability of fibrotic ILD”;
- another patient-level disease probability.

---

## 21. Recommended structured output

```yaml
finding: pulmonary_fibrosis
finding_type: radiographic_fibrotic_finding

cxr_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  radiologist_interpretation: unknown

hrct_characterization:
  available: false
  reticulation: unknown
  traction_bronchiectasis: unknown
  traction_bronchiolectasis: unknown
  honeycombing: unknown
  architectural_distortion: unknown
  volume_loss: unknown
  ground_glass_opacity: unknown
  distribution: unknown
  reported_pattern: unknown

fibrotic_context:
  fibrosis_supported: true
  ild_context: unknown
  uip_pattern: unknown
  ipf_status: unknown
  etiology: unknown
  diagnostic_confidence: unknown

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
  priority: routine|elevated|high
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true

citations: []
```

---

## 22. Prohibited inferences

Hermes MUST NOT:

1. Equate `Pulmonary fibrosis` with IPF.
2. Equate `Pulmonary fibrosis` with UIP.
3. Equate `Pulmonary fibrosis` with PPF.
4. Equate `Pulmonary fibrosis` with a specific ILD subtype.
5. Infer a specific etiology from the CXR fibrosis label.
6. Infer honeycombing from CXR fibrosis.
7. Infer traction bronchiectasis/bronchiolectasis from CXR fibrosis.
8. Infer a specific HRCT pattern from the CXR label.
9. Treat UIP-pattern imaging as automatically equal to IPF.
10. Diagnose PPF from a single study.
11. Diagnose PPF without adequate longitudinal criteria.
12. Double count `ILD + Pulmonary fibrosis` as two independent disease confirmations.
13. Triple count Pulmonary fibrosis with Lung Opacity/Infiltration.
14. Infer acute exacerbation from Pulmonary fibrosis + Consolidation alone.
15. Infer occupational etiology from Pulmonary fibrosis + Pleural thickening alone.
16. Invent exposure, CTD, PFT, pathology, or family-history evidence.
17. Convert AI score into IPF/fibrotic-ILD probability.
18. Treat missing data as negative evidence.
19. Issue autonomous imaging/procedure/treatment orders.
20. Present the finding as a final multidisciplinary diagnosis.
21. Add unsourced subtype/cause-specific rules.

---

## 23. Evidence gaps for v2

Potential additions:
- IPF-specific diagnosis workflow;
- CTD-ILD;
- hypersensitivity pneumonitis;
- occupational fibrosis/asbestosis;
- post-infectious fibrosis;
- drug/radiation fibrosis;
- sarcoidosis;
- familial/genetic pulmonary fibrosis;
- acute exacerbation;
- quantitative fibrosis extent;
- treatment selection.

Do not invent these detailed rules in v1.

---

## 24. Bottom line

```text
Pulmonary fibrosis AI finding on CXR
        ↓
preserve as local fibrotic/scarring evidence
        ↓
HRCT available?
├─ no  → specific pattern / etiology unknown
└─ yes → record actual fibrotic features and distribution
        ↓
separate fibrosis from UIP/IPF
        ↓
integrate broader ILD context
        ↓
PPF only with adequate longitudinal criteria
        ↓
deduplicate ILD / Lung Opacity / Infiltration overlap
        ↓
preserve conflicts and missing evidence
        ↓
bounded assessment
        ↓
doctor review required
```
