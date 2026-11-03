# ILD_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **ILD** trong MedVision Hermes.

`ILD` trong VinBigData phải được xử lý trước hết như một **chest-radiograph finding compatible with an interstitial lung abnormality/pattern**, không phải là một chẩn đoán subtype của interstitial lung disease.

Phạm vi v1:
- adult chest-radiograph reasoning;
- CXR finding vs HRCT pattern separation;
- fibrotic vs non-fibrotic interstitial-disease context;
- CT descriptors such as reticulation, traction bronchiectasis/bronchiolectasis, honeycombing only when CT provides them;
- distinction between incidental interstitial lung abnormalities (ILA) and clinical ILD;
- UIP/IPF guardrails;
- progressive pulmonary fibrosis (PPF) evaluability using supplied longitudinal evidence;
- overlap with broad findings such as Lung Opacity and Infiltration;
- missing evidence, conflicts, uncertainty, doctor review.

Không tự mở rộng v1 thành:
- subtype-specific treatment engine;
- connective-tissue-disease workup algorithm;
- hypersensitivity-pneumonitis diagnostic engine;
- sarcoidosis algorithm;
- genetic/familial pulmonary-fibrosis pathway;
- autonomous HRCT, biopsy, bronchoscopy, or treatment ordering.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **standard thoracic-imaging terminology, including fibrosis-related CT descriptors**

### S2 — ERS/ATS Interstitial Pneumonia Classification 2025
**Ryerson CJ, Adegunsoye A, Piciucchi S, et al. Update of the international multidisciplinary classification of the interstitial pneumonias: an ERS/ATS statement. Eur Respir J. 2025.**  
PMID: 40774805  
DOI: 10.1183/13993003.00158-2025  
Role: **current multidisciplinary classification, fibrotic vs non-fibrotic framework, idiopathic vs secondary causes, diagnostic confidence**

### S3 — ATS/ERS/JRS/ALAT IPF + PPF Guideline 2022
**Raghu G, Remy-Jardin M, Richeldi L, et al. Idiopathic Pulmonary Fibrosis (an Update) and Progressive Pulmonary Fibrosis in Adults: An Official ATS/ERS/JRS/ALAT Clinical Practice Guideline. Am J Respir Crit Care Med. 2022.**  
PMID: 35486072  
PMCID: PMC9851481  
DOI: 10.1164/rccm.202202-0399ST  
Role: **UIP/IPF imaging framework and PPF criteria**

### S4 — ACR Appropriateness Criteria: Diffuse Lung Disease
**American College of Radiology. ACR Appropriateness Criteria — Diffuse Lung Disease. New 2021.**  
URL: https://acsearch.acr.org/docs/3157911/Narrative/  
Role: **CXR/CT imaging context for suspected diffuse lung disease**

### S5 — ATS Clinical Statement on ILA 2025
**Podolanczuk AJ, Hunninghake GM, Wilson KC, et al. Approach to the Evaluation and Management of Interstitial Lung Abnormalities: An Official American Thoracic Society Clinical Statement. Am J Respir Crit Care Med. 2025.**  
PMID: 40387336  
PMCID: PMC12264694  
DOI: 10.1164/rccm.202505-1054ST  
Role: **CT-defined ILA, working distinction between ILA and clinical ILD, symptom/PFT/imaging context**

### Source precedence

1. S2 for current interstitial-pneumonia classification.
2. S3 for IPF/UIP and PPF-specific rules.
3. S5 for ILA-vs-ILD distinction.
4. S1 for imaging terminology.
5. S4 for imaging-appropriateness context.

---

## 2. Core semantic rule

A VinBigData `ILD` output is:

`RADIOGRAPHIC_EVIDENCE_COMPATIBLE_WITH_AN_INTERSTITIAL_PATTERN`

It is NOT automatically:
- idiopathic pulmonary fibrosis (IPF);
- usual interstitial pneumonia (UIP);
- nonspecific interstitial pneumonia (NSIP);
- connective-tissue-disease-associated ILD;
- hypersensitivity pneumonitis;
- sarcoidosis;
- pulmonary fibrosis;
- progressive pulmonary fibrosis;
- a treatment indication.

A CXR classifier cannot by itself establish a specific multidisciplinary ILD diagnosis.

---

## 3. Current classification context

### S2

The 2025 ERS/ATS update expands classification beyond idiopathic interstitial pneumonias to include secondary causes.

The update:
- recognizes interstitial and alveolar-filling disorders;
- subclasses interstitial disorders as **fibrotic** or **non-fibrotic**;
- updates terminology and adds patterns;
- explicitly incorporates **diagnostic confidence** into patient evaluation/management.

### Hermes behavior

A generic `ILD` CXR output must not be promoted to one named subtype.

Maintain separate fields for:
- broad interstitial-pattern evidence;
- fibrosis status;
- HRCT pattern;
- etiology/subtype hypothesis;
- diagnostic confidence.

If those are not provided:
mark them `unknown`.

---

## 4. CXR vs HRCT separation

### S4

For **suspected diffuse lung disease**, ACR rates both:
- chest radiography; and
- CT chest without IV contrast

as `Usually Appropriate` for initial imaging.

For confirmed diffuse lung disease with acute deterioration, radiography and noncontrast CT also have roles.

### Hermes behavior

If ILD is positive on CXR but no CT/HRCT characterization exists:
- preserve the CXR finding;
- do not invent an HRCT pattern;
- subtype remains unknown;
- fibrosis status remains unknown unless independently supported.

Hermes may identify:

`HRCT_CHARACTERIZATION_RELEVANT`

as a clinician-facing evaluation consideration when the case truly matches suspected diffuse lung disease.

Do NOT autonomously order CT/HRCT.

---

## 5. CT terminology

### S1

Fleischner 2024 standardizes thoracic-imaging terms including:
- reticular/reticulation-related descriptors;
- honeycombing;
- traction bronchiectasis / bronchiolectasis;
- fibrosis and associated CT morphology.

### Hermes behavior

Only record:
- reticulation;
- traction bronchiectasis;
- traction bronchiolectasis;
- honeycombing;
- architectural distortion;
- ground-glass opacity;
- distribution

when those findings are explicitly supplied from CT/HRCT or a trusted radiology interpretation.

Do NOT infer them from a generic CXR `ILD` class.

---

## 6. Fibrosis guardrail

### S2

Interstitial disorders can be fibrotic or non-fibrotic.

Therefore:

`ILD -> pulmonary fibrosis`

is prohibited.

### Hermes behavior

If CT or a separate trusted finding explicitly supports fibrosis:
- record `fibrotic_features: present`;
- preserve the broad ILD finding separately.

If fibrosis evidence is absent:
- do not assume either fibrotic or non-fibrotic disease;
- mark `fibrosis_status: unknown`.

If `ILD` and a separate `Pulmonary fibrosis` model output later coexist:
- preserve both;
- identify possible overlap where they refer to the same process;
- do not double count.

`OVERLAPPING_FINDING_EVIDENCE` is `MEDVISION_SYSTEM_POLICY`.

---

## 7. UIP / IPF guardrail

### S3

The 2022 ATS/ERS/JRS/ALAT guideline uses radiologic and histopathologic criteria in IPF evaluation.

HRCT patterns such as:
- UIP;
- probable UIP;
- indeterminate for UIP;
- findings suggesting an alternative diagnosis

belong in an appropriate multidisciplinary IPF diagnostic context.

Fibrotic CT features can include combinations of:
- reticulation;
- traction bronchiectasis/bronchiolectasis;
- honeycombing;
- characteristic distribution.

### Hermes behavior

Never infer:

`CXR ILD -> UIP`

or:

`CXR ILD -> IPF`

If HRCT explicitly reports a UIP-compatible/UIP pattern:
- preserve that imaging pattern;
- do not automatically convert it into `IPF confirmed`;
- look for age, exposure, autoimmune/secondary-cause, pathology and multidisciplinary context if supplied.

An imaging pattern and an etiologic clinical diagnosis are separate objects.

---

## 8. ILA vs clinical ILD

### S5

ATS 2025 defines **interstitial lung abnormality (ILA)** using CT-detected nondependent bilateral parenchymal abnormalities meeting a defined extent criterion.

Potential CT features include:
- ground-glass opacity;
- reticulation;
- lung distortion;
- traction bronchiectasis;
- honeycombing.

The statement distinguishes clinical ILD from ILA using additional evidence that can include:
- respiratory symptoms attributable to an interstitial process;
- abnormal or declining lung function;
- fibrotic or progressive imaging abnormalities;
- a specific fibrotic ILD pattern on imaging or pathology.

### Hermes behavior

Do NOT equate:
- incidental CT ILA with a definite ILD subtype;
- generic CXR `ILD` classifier output with ATS-defined CT ILA;
- one CT interstitial feature with a complete clinical ILD diagnosis.

Keep:
`CT_ILA`
and
`clinical_ILD`
as separate concepts when relevant.

---

## 9. Pulmonary-function and clinical context

Potential clinically relevant evidence includes:
- dyspnea;
- cough;
- oxygenation;
- pulmonary function tests;
- longitudinal FVC/DLCO information when supplied;
- exposure history;
- autoimmune/connective-tissue-disease context;
- medication/radiation context;
- family history.

### Hermes behavior

These can modify:
- diagnostic confidence;
- subtype hypotheses;
- progression assessment.

Do not invent any missing exposure, autoimmune, occupational, medication or family history.

Normal symptoms/PFTs do not necessarily negate an imaging finding.

---

## 10. Progressive Pulmonary Fibrosis (PPF)

### S3

In an adult with an ILD **other than IPF**, PPF is defined by at least **two of three** domains occurring within the past year, with no alternative explanation:

1. worsening respiratory symptoms;
2. physiological progression;
3. radiological progression.

### Hermes behavior

Only evaluate PPF if the supplied case contains adequate longitudinal evidence.

Required logic:
- established/non-IPF ILD context must be relevant;
- time interval must be available;
- at least two required domains must be supportable;
- alternative explanation must not be silently ignored.

If longitudinal evidence is insufficient:

```text
ppf_evaluable: false
```

Do NOT infer PPF from:
- one CXR;
- one positive ILD score;
- fibrosis alone;
- worsening symptoms alone.

This skill v1 does not autonomously select antifibrotic treatment.

---

## 11. Relationship to Lung Opacity

`Lung Opacity` is broader/nonspecific compared with an ILD-pattern finding.

### Hermes behavior

If:

`ILD + Lung Opacity`

are positive:
- preserve both;
- ILD can act as the more-specific interstitial-pattern evidence;
- identify possible overlap if they plausibly reflect the same abnormality;
- do not count both as independent disease evidence.

Emit where appropriate:

`OVERLAPPING_FINDING_EVIDENCE`

---

## 12. Relationship to Infiltration

`Infiltration` is a legacy nonspecific dataset label.

### Hermes behavior

If:

`ILD + Infiltration`

are positive:
- preserve both upstream labels;
- treat ILD as more specific for interstitial-pattern reasoning;
- do not let the legacy label independently strengthen the same ILD hypothesis when overlap is likely.

If Lung Opacity is also present:
- preserve all;
- avoid triple counting.

---

## 13. Relationship to Consolidation

`Consolidation` and `ILD` may coexist.

### Hermes behavior

Preserve both findings.

Do NOT infer:

`ILD + Consolidation -> acute exacerbation of ILD`

Acute exacerbation/deterioration requires clinical and temporal context and exclusion/consideration of alternatives.

If severe respiratory deterioration is supplied:
- raise clinical priority;
- keep etiology uncertain unless evidence supports it.

---

## 14. Multidisciplinary diagnosis and diagnostic confidence

### S2

The 2025 classification is explicitly multidisciplinary and incorporates diagnostic confidence.

### Hermes behavior

Maintain:
- imaging evidence;
- clinical evidence;
- pulmonary-function evidence;
- exposure/secondary-cause evidence;
- pathology if available;
- diagnostic confidence.

Do not fabricate multidisciplinary consensus.

Suggested statuses:
- `low`;
- `intermediate`;
- `high`;
- `unknown`

only when the system has an explicit rule/source for how that status was assigned.

Otherwise leave `diagnostic_confidence: unknown`.

---

## 15. Supporting evidence model

### CXR_EVIDENCE
- AI `ILD`;
- model score;
- distribution if supplied;
- radiologist/manual interpretation.

### HRCT_EVIDENCE
Potentially relevant:
- reticulation;
- ground-glass opacity;
- traction bronchiectasis/bronchiolectasis;
- honeycombing;
- architectural distortion;
- axial/craniocaudal distribution;
- UIP/probable-UIP/other pattern if explicitly reported.

### CLINICAL_EVIDENCE
- dyspnea/cough;
- symptom duration;
- exposure history;
- autoimmune/CTD context;
- medications/radiation;
- family history;
- oxygenation.

### PHYSIOLOGIC_EVIDENCE
- PFTs;
- FVC trend;
- DLCO trend;
- other supplied pulmonary physiology.

### PATHOLOGY / MDD
- biopsy/pathology if supplied;
- documented multidisciplinary diagnosis if supplied.

---

## 16. Conflict detection

Examples:
- AI says ILD while trusted human CXR review explicitly reports no interstitial abnormality;
- CXR AI suggests ILD while high-quality HRCT reports no corresponding interstitial abnormality.

Emit:

`EVIDENCE_CONFLICT`

Preserve both sources.

When CXR and HRCT differ:
- HRCT is more specific for interstitial characterization;
- do not erase the original AI result;
- report modality discordance.

---

## 17. Missing evidence

Potential missing fields:
- HRCT characterization;
- fibrosis status;
- distribution;
- symptoms/chronicity;
- PFTs;
- exposure history;
- autoimmune/CTD context;
- medication/radiation context;
- family history;
- prior imaging;
- longitudinal physiology;
- pathology/MDD when subtype diagnosis is being considered.

Missing data is not negative evidence.

---

## 18. Safety policy

ILD CXR finding alone is not automatically an emergency.

If independent data show:
- severe/new respiratory distress;
- significant hypoxemia;
- rapid physiological deterioration;
- another acute high-risk syndrome;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not autonomously prescribe:
- corticosteroids;
- antifibrotics;
- immunosuppression;
- oxygen/ventilation changes;
- HRCT;
- bronchoscopy;
- biopsy;
- other procedures/treatment.

---

## 19. AI score interpretation

AI model score is not automatically:
- probability of IPF;
- probability of UIP;
- probability of fibrosis;
- probability of CTD-ILD;
- probability of PPF;
- disease severity.

Keep separate:

```text
image_model_score
cxr_interstitial_pattern
hrct_pattern
fibrosis_status
clinical_ild_hypothesis
subtype_hypothesis
progression_status
uncertainty
```

Never convert `0.91` into:
- “91% probability of IPF”;
- “91% probability of UIP”;
- another subtype probability.

---

## 20. Recommended structured output

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
  priority: routine|elevated|high
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true

citations: []
```

---

## 21. Prohibited inferences

Hermes MUST NOT:

1. Equate `ILD` with IPF.
2. Equate `ILD` with UIP.
3. Equate `ILD` with NSIP.
4. Equate `ILD` with pulmonary fibrosis.
5. Equate `ILD` with CTD-ILD.
6. Equate `ILD` with hypersensitivity pneumonitis.
7. Infer HRCT reticulation, honeycombing, traction bronchiectasis or GGO from a CXR class.
8. Treat a UIP imaging pattern as automatically equivalent to IPF.
9. Treat a CT ILA as automatically equivalent to a specific clinical ILD.
10. Diagnose PPF from a single study.
11. Diagnose PPF without adequate longitudinal evidence and at least two applicable progression domains.
12. Treat `ILD + Consolidation` as automatic acute exacerbation.
13. Double/triple count ILD with overlapping Lung Opacity/Infiltration findings.
14. Invent exposure, CTD, family-history, PFT or pathology information.
15. Convert AI score into ILD-subtype probability.
16. Treat missing evidence as negative evidence.
17. Issue autonomous imaging/procedure/treatment orders.
18. Present the assessment as final multidisciplinary diagnosis.
19. Add unsourced subtype-specific rules.

---

## 22. Evidence gaps for v2

Potential additions:
- CTD-ILD diagnostic pathways;
- hypersensitivity-pneumonitis guideline integration;
- sarcoidosis;
- occupational/environmental ILD;
- medication/radiation-associated ILD;
- familial/genetic pulmonary fibrosis;
- acute exacerbation diagnostic criteria;
- quantitative PFT decline implementation;
- antifibrotic/immunosuppressive treatment logic;
- pathology-pattern integration.

Do not invent these detailed rules in v1.

---

## 23. Bottom line

```text
ILD AI finding on CXR
        ↓
preserve as broad radiographic interstitial-pattern evidence
        ↓
HRCT available?
├─ no  → subtype unknown / fibrosis unknown
└─ yes → record actual CT morphology and reported pattern
        ↓
separate fibrotic vs non-fibrotic context
        ↓
separate ILA vs clinical ILD
        ↓
never convert UIP pattern directly to IPF
        ↓
PPF only if adequate longitudinal criteria are supplied
        ↓
deduplicate Lung Opacity / Infiltration overlap
        ↓
identify missing/conflicting evidence
        ↓
bounded multidisciplinary-style assessment
        ↓
doctor review required
```
