# PLEURAL_THICKENING_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Pleural thickening** trong MedVision Hermes.

`Pleural thickening` trong VinBigData/VinDr-CXR phải được xử lý trước hết như một **local radiographic pleural abnormality**, không phải là chẩn đoán asbestos-related disease, pleural plaque, asbestosis, mesothelioma, pleural metastasis, tuberculosis, empyema, hay một căn nguyên cụ thể.

Phạm vi v1:
- adult chest-radiograph reasoning;
- pleural thickening as focal/multifocal/diffuse and unilateral/bilateral when supplied;
- separation of CXR finding from CT/MRI/PET characterization;
- asbestos-related disease guardrails;
- pleural plaque vs diffuse pleural thickening distinction;
- malignant pleural disease concern without pathology-level diagnosis;
- overlap/coexistence with Pleural effusion, Pulmonary fibrosis, and later Calcification skill;
- missing evidence, conflict detection, uncertainty, and doctor review.

Không tự mở rộng v1 thành:
- mesothelioma diagnostic engine;
- asbestos-exposure inference engine;
- TB diagnostic engine;
- empyema diagnostic engine;
- autonomous CT/PET/biopsy/thoracoscopy/treatment ordering.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **standard thoracic-imaging terminology and pleural imaging descriptors**

### S2 — VinDr-CXR dataset paper 2022
**Nguyen HQ, Lam K, Le LT, et al. VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations. Scientific Data. 2022.**  
PMID: 35858929  
PMCID: PMC9300612  
DOI: 10.1038/s41597-022-01498-w  
Role: **dataset semantics: local radiographic finding vs global disease-level labels**

### S3 — Yamada et al. 2024
**Yamada A, Taiji R, Nishimoto Y, et al. Pictorial Review of Pleural Disease: Multimodality Imaging and Differential Diagnosis. RadioGraphics. 2024.**  
PMID: 38547031  
DOI: 10.1148/rg.230079  
Role: **primary pleural-imaging review: distribution, morphology, broad differential, multimodality characterization**

### S4 — BTS Pleural Disease Guideline 2023
**Roberts ME, Rahman NM, Maskell NA, et al. British Thoracic Society Guideline for pleural disease. Thorax. 2023.**  
PMID: 37433578  
DOI: 10.1136/thorax-2022-219784  
Role: **current pleural-disease clinical framework, especially malignant pleural disease/investigation context**

### S5 — Alfudhili et al. 2016
**Alfudhili KM, Lynch DA, Laurent F, Ferretti GR, Dunet V, Beigelman-Aubry C. Focal pleural thickening mimicking pleural plaques on chest computed tomography: tips and tricks. Br J Radiol. 2016.**  
PMID: 26539633  
PMCID: PMC4985966  
DOI: 10.1259/bjr.20150792  
Role: **pleural-plaque mimics and false attribution guardrail**

### S6 — Miles et al. 2008
**Miles SE, Sandrini A, Johnson AR, Yates DH. Clinical consequences of asbestos-related diffuse pleural thickening: A review. J Occup Med Toxicol. 2008.**  
PMID: 18775081  
PMCID: PMC2553409  
DOI: 10.1186/1745-6673-3-20  
Role: **asbestos-related diffuse pleural thickening and distinction from pleural plaques**

### Source precedence

1. S3 for broad pleural-thickening imaging differential and morphology.
2. S4 for clinical pleural-disease framework.
3. S6 for asbestos-related diffuse pleural thickening.
4. S5 for pleural-plaque mimics/false attribution.
5. S1 for terminology.
6. S2 for dataset provenance.

---

## 2. Core semantic rule

A VinBigData `Pleural thickening` output is:

`RADIOGRAPHIC_EVIDENCE_OF_PLEURAL_THICKENING_OR_PLEURAL_ABNORMALITY`

It is NOT automatically:
- asbestos exposure;
- asbestos-related pleural disease;
- pleural plaque;
- asbestosis;
- malignant pleural mesothelioma;
- pleural metastasis;
- tuberculosis;
- chronic empyema;
- a treatment/procedure indication.

---

## 3. Dataset semantics: finding != disease

### S2

VinDr-CXR separates local radiographic labels from global suspected-disease labels.

### Hermes behavior

Preserve:

```text
finding = "Pleural thickening"
```

as an upstream finding.

Do not transform it into a disease diagnosis or exposure history.

---

## 4. Morphology and distribution

### S3

Pleural thickening can be:
- unilateral or bilateral;
- focal, multifocal, or diffuse.

A broad spectrum of pleural disorders can produce thickening.

### Hermes behavior

Record only if explicitly supplied:
- focal / multifocal / diffuse;
- unilateral / bilateral;
- smooth / irregular / nodular;
- circumferential involvement;
- mediastinal pleural involvement;
- associated pleural effusion;
- calcification;
- chest-wall/diaphragmatic involvement;
- prior imaging change.

Do not invent morphology from the CXR class alone.

---

## 5. CXR vs CT/MRI/PET separation

### S3

CT, MRI, and FDG PET/CT can aid characterization and differentiation of pleural abnormalities in appropriate contexts.

### Hermes behavior

From a CXR `Pleural thickening` result alone, do NOT infer:
- nodular pleural disease;
- circumferential pleural encasement;
- pleural plaque;
- calcified pleural plaque;
- chest-wall invasion;
- PET avidity;
- malignant histology.

If cross-sectional imaging is supplied:
- preserve its morphology separately;
- use it as more-specific characterization evidence.

If clinically appropriate, Hermes may identify:

`PLEURAL_CROSS_SECTIONAL_CHARACTERIZATION_RELEVANT`

as a clinician-facing consideration.

Do not autonomously order imaging.

---

## 6. Pleural plaque vs pleural thickening

### S3 / S5 / S6

Pleural plaques and diffuse pleural thickening are not interchangeable entities.

S5 emphasizes that multiple normal structures and disease processes can mimic focal pleural plaques on CT.

S6 describes asbestos-related diffuse pleural thickening as pathologically distinct from pleural plaques, although they may coexist.

### Hermes behavior

Never infer:

`Pleural thickening -> pleural plaque`

If CT explicitly reports a pleural plaque:
- record it as a more-specific pleural morphology;
- preserve the original CXR finding separately.

If calcification is also present:
- do not infer that calcification is pleural unless localization is explicitly supplied.

---

## 7. Asbestos guardrail

### S6

Diffuse pleural thickening may be associated with asbestos exposure, but asbestos-related diffuse pleural thickening is a specific etiologic context.

Pleural plaques may coexist but are a distinct pathologic process.

### Hermes behavior

Never infer:

`Pleural thickening -> asbestos exposure`

or:

`Pleural thickening -> asbestosis`

Only raise an asbestos-related pleural disease hypothesis when independent evidence exists, such as:
- documented occupational/environmental asbestos exposure;
- trusted clinician history;
- CT morphology interpreted in that context.

Even then:
- preserve uncertainty;
- do not diagnose asbestosis solely from pleural thickening.

---

## 8. Malignant pleural disease guardrail

### S3 / S4

Pleural thickening has a broad benign and malignant differential.

S3 describes malignant pleural processes, including malignant pleural mesothelioma and metastases, as possible causes of pleural thickening.

Some cross-sectional imaging morphologies can increase concern, but morphology does not equal pathology.

### Hermes behavior

If CT/MRI reports suspicious pleural morphology, such as:
- nodular pleural thickening;
- circumferential pleural involvement/encasement;
- other explicitly suspicious pleural features;

Hermes may increase:

`MALIGNANT_PLEURAL_DISEASE_CONCERN`

But MUST NOT output:
- `mesothelioma confirmed`;
- `pleural metastasis confirmed`;
- another pathology diagnosis

unless a trusted pathology/clinical source provides that diagnosis.

No numeric malignancy probability is encoded in v1.

---

## 9. Pleural effusion relationship

Pleural thickening and pleural effusion may coexist across multiple pleural diseases [S3][S4].

### Hermes behavior

If:

`Pleural thickening + Pleural effusion`

are both positive:
- preserve both findings;
- do not infer mesothelioma;
- do not infer TB;
- do not infer empyema;
- do not infer malignancy solely from co-occurrence.

Use pleural-effusion-specific evidence from the existing skill when relevant.

Do not double count coexisting pleural findings as independent proof of one etiology.

---

## 10. Pulmonary fibrosis relationship

Pleural thickening may coexist with parenchymal fibrosis in multiple settings.

### Hermes behavior

If:

`Pleural thickening + Pulmonary fibrosis`

are both positive:
- preserve both;
- do not automatically infer asbestosis;
- do not infer occupational exposure;
- keep pleural and parenchymal evidence separate.

If documented asbestos exposure and appropriate imaging context are present, asbestos-related disease may become a hypothesis, not an automatic diagnosis.

---

## 11. Calcification relationship

A future `Calcification` skill may coexist with Pleural thickening.

### Hermes behavior

If:

`Pleural thickening + Calcification`

are positive:
- preserve both upstream findings;
- do not assume the calcification is pleural;
- do not assume pleural plaque;
- require explicit localization/CT characterization to connect them.

If CT explicitly describes calcified pleural plaques:
- preserve that specific characterization.

---

## 12. Tuberculosis / infection guardrail

### S5 / S3

Prior tuberculosis and pleural inflammatory/infectious processes can be among causes of pleural abnormalities, but pleural thickening is nonspecific.

### Hermes behavior

Never infer:

`Pleural thickening -> tuberculosis`

or:

`Pleural thickening -> empyema`

Use:
- microbiology;
- symptoms;
- pleural-fluid data;
- clinical history;
- CT/US morphology

only when supplied.

The existing Pleural Effusion skill remains responsible for pleural-fluid reasoning.

---

## 13. Supporting evidence model

### CXR_EVIDENCE
- AI `Pleural thickening`;
- model score;
- side/localization if supplied;
- radiologist interpretation;
- prior CXR comparison.

### PLEURAL_CROSS_SECTIONAL_EVIDENCE
Potentially relevant:
- CT/MRI morphology;
- focal/multifocal/diffuse;
- smooth/irregular/nodular;
- circumferential involvement;
- mediastinal pleural involvement;
- calcification;
- plaque characterization;
- chest-wall/diaphragmatic involvement;
- associated effusion.

### EXPOSURE_CONTEXT
- asbestos exposure;
- occupational/environmental history.

### CLINICAL / DEFINITIVE EVIDENCE
- symptoms;
- pleural-fluid data;
- microbiology;
- cytology;
- pathology;
- trusted clinician diagnosis.

---

## 14. Conflict detection

Examples:
- AI reports Pleural thickening while trusted human CXR review says pleura are not thickened;
- CXR AI is positive but high-quality CT reports no corresponding pleural thickening.

Emit:

`EVIDENCE_CONFLICT`

Preserve both.

Treat CT as more specific for pleural morphology but retain the upstream AI result for audit.

---

## 15. Missing evidence

Potential missing fields:
- side/distribution;
- focal vs diffuse pattern;
- CT characterization;
- associated effusion;
- calcification localization;
- asbestos exposure history;
- TB/infection history;
- prior imaging;
- cytology/pathology if malignancy is being considered.

Missing evidence is not negative evidence.

---

## 16. Safety policy

Pleural thickening alone is not automatically an emergency.

If independent evidence shows:
- severe respiratory compromise;
- major hemodynamic instability;
- another acute high-risk pleural syndrome;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not autonomously prescribe/order:
- CT;
- PET/CT;
- thoracentesis;
- biopsy;
- thoracoscopy;
- surgery;
- antimicrobial therapy;
- oncologic treatment.

---

## 17. AI score interpretation

The AI score is not automatically:
- probability of mesothelioma;
- probability of asbestos-related disease;
- probability of tuberculosis;
- probability of pleural metastasis;
- pleural thickness in millimeters;
- disease severity.

Keep separate:

```text
image_model_score
cxr_pleural_thickening
cross_sectional_pleural_morphology
etiology_hypotheses
malignancy_concern
definitive_diagnosis
uncertainty
```

Never convert `0.87` into:
- “87% probability of mesothelioma”;
- “87% probability of asbestos disease”;
- another patient-level disease probability.

---

## 18. Recommended structured output

```yaml
finding: pleural_thickening
finding_type: radiographic_pleural_finding

cxr_evidence:
  model_score: null
  side: unknown
  distribution: unknown
  radiologist_interpretation: unknown

cross_sectional_characterization:
  available: false
  modality: unknown
  focality: unknown
  surface: unknown
  nodularity: unknown
  circumferential_involvement: unknown
  mediastinal_pleural_involvement: unknown
  calcification: unknown
  plaque_morphology: unknown
  associated_effusion: unknown

etiology_context:
  asbestos_exposure: unknown
  tuberculosis_or_infection_context: unknown
  malignancy_context: unknown
  other: []

pleural_disease_hypotheses:
  asbestos_related_pleural_disease:
    status: unknown
    evidence: []
  malignant_pleural_disease:
    status: unknown
    evidence: []
  infectious_inflammatory_pleural_disease:
    status: unknown
    evidence: []

overlap:
  pleural_effusion: unknown
  pulmonary_fibrosis: unknown
  calcification: unknown
  flags: []

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

## 19. Prohibited inferences

Hermes MUST NOT:

1. Equate Pleural thickening with asbestos exposure.
2. Equate Pleural thickening with pleural plaque.
3. Equate Pleural thickening with asbestosis.
4. Equate Pleural thickening with mesothelioma.
5. Equate Pleural thickening with pleural metastasis.
6. Equate Pleural thickening with tuberculosis.
7. Equate Pleural thickening with empyema.
8. Infer CT morphology from a generic CXR finding.
9. Infer pleural calcification from an unlocalized Calcification finding.
10. Infer occupational disease from Pleural thickening + Pulmonary fibrosis alone.
11. Infer malignancy from Pleural thickening + Pleural effusion alone.
12. Treat suspicious CT morphology as pathology confirmation.
13. Invent a numeric pleural-malignancy probability.
14. Convert AI score into disease probability.
15. Treat missing data as negative evidence.
16. Issue autonomous imaging/procedure/treatment orders.
17. Present the assessment as a final pathologic diagnosis.
18. Add unsourced etiologic rules.

---

## 20. Evidence gaps for v2

Potential additions:
- dedicated malignant pleural mesothelioma diagnostic pathway;
- validated CT malignancy feature models;
- asbestos-exposure occupational medicine framework;
- pleural plaque-specific characterization;
- detailed TB pleuritis pathway;
- empyema/chronic pleuritis morphology;
- PET/CT interpretation;
- biopsy/thoracoscopy decision logic.

Do not invent these detailed rules in v1.

---

## 21. Bottom line

```text
Pleural thickening AI finding on CXR
        ↓
preserve as local pleural abnormality
        ↓
cross-sectional imaging available?
├─ no  → morphology / etiology remain uncertain
└─ yes → record actual pleural morphology
        ↓
separate plaque / diffuse thickening / suspicious morphology
        ↓
do NOT infer asbestos exposure or malignancy
        ↓
integrate effusion / fibrosis / calcification without over-attribution
        ↓
preserve conflicts and missing evidence
        ↓
bounded assessment
        ↓
doctor review required
```
