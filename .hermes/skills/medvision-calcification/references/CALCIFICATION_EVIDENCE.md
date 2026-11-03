# CALCIFICATION_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Calcification** trong MedVision Hermes.

`Calcification` trong VinBigData/VinDr-CXR phải được xử lý trước hết như một **local thoracic radiographic finding**. Nó không tự xác định:
- anatomical compartment;
- structure of origin;
- benignity;
- malignancy;
- active or healed infection;
- pleural plaque;
- asbestos exposure;
- granuloma;
- pulmonary ossification;
- vascular/cardiac disease.

Triết lý trung tâm của v1 là:

```text
LOCALIZE FIRST
        ↓
CHARACTERIZE IF DATA EXISTS
        ↓
ONLY THEN CONSIDER ETIOLOGIC HYPOTHESES
```

Nếu localization/compartment không đủ rõ, giữ `unknown`.

Phạm vi v1:
- adult chest-radiograph reasoning;
- local label provenance;
- spatial localization vs true anatomical localization;
- pulmonary, pleural, nodal/mediastinal, chest-wall, cardiac/vascular possibilities;
- pulmonary nodule calcification pattern only when explicitly characterized;
- pulmonary calcification vs ossification;
- metastatic vs dystrophic pulmonary calcification only when pulmonary location + context support it;
- overlap with Nodule/Mass, Pleural thickening, Pulmonary fibrosis, Aortic enlargement, Cardiomegaly;
- conflict, uncertainty, missing evidence, doctor review.

Không tự mở rộng v1 thành:
- active TB diagnostic pathway;
- asbestos-related disease diagnosis;
- coronary/aortic-valve disease diagnosis;
- calcified-nodule treatment/follow-up engine;
- metabolic calcification workup;
- autonomous CT/biopsy/treatment ordering.

---

## 1. Evidence hierarchy

### S1 — VinDr-CXR dataset paper 2022
**Nguyen HQ, Lam K, Le LT, et al. VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations. Scientific Data. 2022.**  
PMID: 35858929  
PMCID: PMC9300612  
DOI: 10.1038/s41597-022-01498-w  
Role: **canonical dataset semantics: Calcification is a local label with localized annotation, distinct from disease-level global labels**

### S2 — Toussie et al. 2025
**Toussie D, Azour L, Garrana S, et al. Pulmonary Calcification and Ossification: Pathogenesis, CT Appearance, and Specific Disorders. RadioGraphics. 2025.**  
PMID: 40338797  
DOI: 10.1148/rg.240110  
Role: **pulmonary calcification vs ossification; metastatic vs dystrophic pulmonary calcification; CT pattern/context**

### S3 — Carvalho et al. 2022
**Carvalho JG, Sousa J, Fernandes C, França M. Chest calcifications beyond the lung parenchyma—A review. Radiologia (Engl Ed). 2022.**  
PMID: 36243445  
DOI: 10.1016/j.rxeng.2022.06.001  
Role: **location-based approach to extrapulmonary thoracic calcification**

### S4 — Baratella et al. 2025
**Baratella E, Carbi M, Minelli P, et al. Calcified Lung Nodules: A Diagnostic Challenge in Clinical Daily Practice. Tomography. 2025.**  
PMID: 40137568  
PMCID: PMC11946818  
DOI: 10.3390/tomography11030028  
Role: **calcified pulmonary nodules; pattern characterization; calcification does not inherently exclude malignancy**

### S5 — Fleischner Society 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **standard terminology for nodules/pleural plaques and pleural calcification context**

### S6 — Brown et al. 1994
**Brown K, Mund DF, Aberle DR, Batra P, Young DA. Intrathoracic calcifications: radiographic features and differential diagnoses. RadioGraphics. 1994.**  
PMID: 7855339  
DOI: 10.1148/radiographics.14.6.7855339  
Role: **foundational location/pattern framework across thoracic compartments**

### Source precedence

1. S1 for dataset provenance.
2. S2 for pulmonary calcification/ossification mechanisms.
3. S3 for modern location-based extrapulmonary differential.
4. S4 for calcified pulmonary nodules.
5. S5 for standardized terminology and pleural plaque context.
6. S6 for broad historical intrathoracic location/pattern framework.

---

## 2. Core semantic rule

A VinBigData `Calcification` output is:

`RADIOGRAPHIC_EVIDENCE_OF_THORACIC_CALCIFICATION`

It is NOT automatically:
- benign;
- malignant;
- healed granuloma;
- tuberculosis;
- hamartoma;
- pleural plaque;
- asbestos exposure;
- vascular calcification;
- valvular calcification;
- pulmonary ossification;
- metastatic pulmonary calcification;
- dystrophic pulmonary calcification.

---

## 3. Dataset semantics and localization limits

### S1

VinDr-CXR contains 22 local labels and 6 global disease-level labels.

`Calcification` is a local label and local findings are annotated with bounding boxes.

### Hermes behavior

Preserve:

```text
finding = "Calcification"
```

and preserve bounding box/image location when supplied.

Important distinction:

```text
2D image-plane localization
≠
definitive anatomical compartment
```

A bounding box may indicate where the opacity lies on the projection but does not by itself prove whether calcium is:
- pulmonary;
- pleural;
- nodal/mediastinal;
- chest-wall;
- vascular;
- cardiac.

Only assign anatomical compartment/structure when explicitly supported by trusted imaging interpretation or sufficiently specific cross-sectional imaging.

---

## 4. Location-first reasoning

### S3 / S6

Thoracic calcifications may arise in multiple compartments including:
- lung parenchyma;
- mediastinum;
- hilar/mediastinal lymph nodes;
- pleura;
- chest wall;
- other thoracic structures.

Location and morphology strongly influence the differential.

### Hermes behavior

Always attempt to populate:

```yaml
calcification_localization:
  status: known|partial|unknown
  compartment: pulmonary|pleural|nodal_mediastinal|chest_wall|cardiac_vascular|other|unknown
  structure: unknown
  source: unknown
```

If location is not explicitly established:

`compartment: unknown`

Do NOT start a compartment-specific etiologic branch solely from a generic positive class.

---

## 5. CXR vs CT separation

CT is more sensitive/specific for detailed calcification localization and morphology in many thoracic settings [S2][S3][S4][S6].

### Hermes behavior

From CXR Calcification alone, do NOT invent:
- intranodular calcification;
- pleural plaque;
- calcified lymph node;
- coronary calcium;
- aortic-wall calcification;
- valvular calcification;
- calcification pattern.

If CT is supplied:
- preserve actual localization;
- preserve actual morphology/pattern;
- keep the original CXR AI result in provenance.

Hermes may identify:

`CROSS_SECTIONAL_CALCIFICATION_CHARACTERIZATION_RELEVANT`

when localization or morphology is clinically important and unresolved.

Do not autonomously order CT.

---

## 6. Pulmonary calcification vs pulmonary ossification

### S2

Pulmonary calcification and pulmonary ossification are distinct processes with different pathogenesis, histology, and imaging appearances.

### Hermes behavior

Never infer:

`Calcification -> pulmonary ossification`

Even when Pulmonary fibrosis is also present:

`Calcification + Pulmonary fibrosis != dendriform pulmonary ossification`

Only record ossification when trusted CT/radiology/pathology evidence explicitly supports it.

---

## 7. Metastatic vs dystrophic pulmonary calcification

### S2

When calcification is truly pulmonary:
- metastatic pulmonary calcification (MPC) is associated with systemic hypercalcemia/metabolic context;
- dystrophic pulmonary calcification (DPC) is associated with local lung injury/scarring.

### Hermes behavior

Do NOT infer either mechanism from the generic CXR class.

Only consider these hypotheses when:
1. pulmonary localization is established; and
2. relevant metabolic or local-injury context is supplied.

Examples of required context:
- metabolic/calcium disorder data for MPC;
- known prior pulmonary injury/scarring for DPC.

Do not invent laboratory abnormalities.

---

## 8. Relationship to Nodule/Mass

### S4

Calcification may occur in benign and malignant pulmonary nodules.

Common calcification patterns can provide diagnostic clues, but calcification does **not inherently exclude malignancy**.

S4 describes patterns such as:
- diffuse;
- central;
- laminated/lamellated;
- popcorn;
- punctate;
- eccentric.

### Hermes behavior

If:

`Calcification + Nodule/Mass`

are both positive but no reliable same-lesion localization exists:
- preserve both;
- do NOT call it a calcified pulmonary nodule.

If CT or trusted radiology explicitly establishes calcification within the nodule/mass:
- record `intranodular_calcification: true`;
- record pattern if supplied;
- use pattern as morphology evidence.

Do NOT automatically conclude:
- benign;
- hamartoma;
- granuloma;
- malignancy excluded.

If same-lesion overlap is explicit:

`OVERLAPPING_FINDING_EVIDENCE`

may be emitted as `MEDVISION_SYSTEM_POLICY` to prevent double counting as independent disease evidence.

---

## 9. Benignity / malignancy guardrail

### S4

Calcification is often associated with benign processes, but malignant pulmonary nodules can also calcify.

### Hermes behavior

Never infer:

`calcification -> benign`

or:

`calcified nodule -> malignancy excluded`

If a CT pattern is supplied:
- describe the pattern;
- allow it to modify a bounded risk hypothesis;
- do not manufacture a numeric malignancy probability.

Existing Nodule/Mass skill remains responsible for broader focal-lesion reasoning.

---

## 10. Relationship to Pleural thickening

### S3 / S5

Pleural calcification can occur in chronic inflammatory and asbestos-related contexts.

Fleischner describes pleural plaques as focal fibrohyaline parietal pleural lesions that often contain calcification and are usually associated with prior asbestos exposure.

### Hermes behavior

If:

`Calcification + Pleural thickening`

are positive but calcification location is not explicitly pleural:
- preserve both;
- do NOT infer calcified pleural plaque;
- do NOT infer asbestos exposure.

If CT explicitly reports calcified pleural plaque:
- preserve that characterization;
- keep exposure history separate.

Do not infer exposure solely from generic Calcification + Pleural thickening.

---

## 11. Calcified lymph nodes / granulomatous context

### S3

Calcified mediastinal lymph nodes may occur after healed granulomatous infection, but the differential includes other disorders such as pneumoconioses and sarcoidosis.

### Hermes behavior

If CT explicitly localizes calcification to hilar/mediastinal nodes:
- record nodal localization;
- consider prior granulomatous disease only as a hypothesis when context supports it.

Never infer:
- active tuberculosis;
- prior tuberculosis with certainty;
- sarcoidosis;
- silicosis

from nodal calcification alone.

If prior healed granulomatous disease is explicitly documented:
- preserve it as historical context;
- do not convert it into active infection.

---

## 12. Relationship to Pulmonary fibrosis

### S2

Dystrophic pulmonary calcification may occur in regions of prior lung injury/fibrosis/scarring.

Pulmonary ossification is a distinct entity.

### Hermes behavior

If:

`Calcification + Pulmonary fibrosis`

are both positive:
- preserve both;
- do not automatically infer dystrophic calcification;
- do not infer pulmonary ossification.

Only relate them when:
- pulmonary localization is established; and
- imaging/context supports a shared process.

---

## 13. Cardiac / vascular localization guardrail

### S3 / S6

Thoracic calcifications can arise outside lung and pleura, including cardiovascular structures.

### Hermes behavior

If `Calcification` coexists with:
- Aortic enlargement;
- Cardiomegaly;

preserve each finding separately.

Do NOT infer:
- aortic calcification;
- coronary artery calcification;
- aortic-valve calcification;
- mitral annular calcification;
- pericardial calcification

unless the structure is explicitly identified by trusted imaging/radiology evidence.

Do not convert a generic Calcification score into cardiovascular disease probability.

---

## 14. Supporting evidence model

### CXR_EVIDENCE
- AI `Calcification`;
- model score;
- bounding box / image-plane location if supplied;
- radiologist interpretation;
- prior comparison.

### LOCALIZATION_EVIDENCE
- compartment;
- specific structure;
- source modality;
- confidence/provenance.

### CT_MORPHOLOGY
Potentially relevant:
- pulmonary vs pleural vs nodal vs cardiovascular;
- nodule-associated vs diffuse;
- calcification pattern;
- plaque morphology;
- associated fibrosis/scarring;
- associated mass/nodule.

### CLINICAL_CONTEXT
Potentially relevant:
- prior granulomatous infection;
- asbestos exposure;
- metabolic/calcium disorder;
- occupational exposure;
- known malignancy;
- prior thoracic injury/therapy.

These affect hypotheses but do not redefine the generic AI finding.

---

## 15. Conflict detection

Examples:
- AI says Calcification but trusted human CXR review says no calcification;
- CXR AI suggests calcification but CT shows no corresponding calcified focus.

Emit:

`EVIDENCE_CONFLICT`

Preserve both.

CT can provide more-specific localization/morphology, but do not erase original AI provenance.

---

## 16. Missing evidence

Potential missing fields:
- true anatomical compartment;
- specific structure;
- CT characterization;
- association with nodule/mass;
- calcification pattern;
- pleural localization;
- nodal localization;
- metabolic context;
- exposure history;
- prior infection history;
- longitudinal stability/change.

Missing evidence is not negative evidence.

---

## 17. Safety policy

Generic Calcification alone is not automatically an emergency.

If an independent high-risk clinical condition is supplied:
- route according to that clinical syndrome;
- emit `HIGH_PRIORITY_CLINICAL_REVIEW` where appropriate.

This is `MEDVISION_SYSTEM_POLICY`.

Do not autonomously order:
- CT;
- biopsy;
- bronchoscopy;
- metabolic workup;
- cardiovascular intervention;
- antimicrobial therapy;
- oncologic treatment.

---

## 18. AI score interpretation

AI score is not automatically:
- probability of benignity;
- probability of malignancy;
- probability of TB;
- probability of granuloma;
- probability of asbestos disease;
- probability of vascular disease;
- amount of calcium.

Keep separate:

```text
image_model_score
calcification_presence
anatomic_localization
morphology
associated_finding
etiology_hypotheses
uncertainty
```

Never convert `0.90` into:
- “90% benign”;
- “90% TB”;
- “90% malignancy”;
- another patient-level disease probability.

---

## 19. Recommended structured output

```yaml
finding: calcification
finding_type: thoracic_radiographic_calcification

image_evidence:
  model_score: null
  bounding_box: unknown
  radiologist_interpretation: unknown

calcification_localization:
  status: unknown
  compartment: unknown
  structure: unknown
  source_modality: unknown

cross_sectional_characterization:
  available: false
  calcification_pattern: unknown
  intranodular: unknown
  pleural: unknown
  nodal: unknown
  cardiac_vascular: unknown
  associated_fibrosis_or_scarring: unknown
  ossification_reported: unknown

context:
  prior_granulomatous_disease: unknown
  active_infection_context: unknown
  asbestos_exposure: unknown
  metabolic_calcium_context: unknown
  malignancy_context: unknown
  prior_injury_or_therapy: unknown

overlap:
  nodule_mass: unknown
  pleural_thickening: unknown
  pulmonary_fibrosis: unknown
  aortic_enlargement: unknown
  cardiomegaly: unknown
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

## 20. Prohibited inferences

Hermes MUST NOT:

1. Equate Calcification with benignity.
2. Treat calcification as excluding malignancy.
3. Equate Calcification with tuberculosis.
4. Equate Calcification with granuloma.
5. Equate Calcification with hamartoma.
6. Equate Calcification with pleural plaque.
7. Equate Calcification with asbestos exposure.
8. Equate Calcification with pulmonary ossification.
9. Equate Calcification with vascular/cardiac calcification.
10. Infer an anatomic compartment from a generic positive class alone.
11. Treat a 2D bounding box as definitive structure-of-origin proof.
12. Infer a calcified pulmonary nodule from Calcification + Nodule/Mass without reliable same-lesion evidence.
13. Infer calcified pleural plaque from Calcification + Pleural thickening without explicit pleural localization.
14. Infer dystrophic calcification from Calcification + Pulmonary fibrosis alone.
15. Infer active TB from calcified nodes or granulomatous history.
16. Infer metastatic pulmonary calcification without pulmonary localization and metabolic context.
17. Convert AI score into disease probability or calcium burden.
18. Treat missing data as negative evidence.
19. Issue autonomous imaging/procedure/treatment orders.
20. Present a compartment-specific etiologic diagnosis without supporting evidence.
21. Add unsourced localization or disease rules.

---

## 21. Evidence gaps for v2

Potential additions:
- coronary/aortic/valvular/pericardial calcification-specific pathways;
- standardized nodule calcification pattern risk modifiers;
- metabolic pulmonary calcification workup;
- granulomatous disease-specific reasoning;
- asbestos/pleural plaque pathway;
- quantitative calcium assessment;
- explicit bbox colocalization algorithm;
- longitudinal stability semantics.

Do not invent these detailed rules in v1.

---

## 22. Bottom line

```text
Calcification AI positive
        ↓
preserve local finding and bbox if supplied
        ↓
is anatomical compartment explicitly known?
├─ no  → localization unknown; stop compartment-specific inference
└─ yes → record pulmonary / pleural / nodal / cardiovascular / other
        ↓
cross-sectional morphology available?
├─ no  → pattern unknown
└─ yes → record actual pattern and associated structure
        ↓
integrate Nodule/Mass / Pleural thickening / Fibrosis only when relationship is supported
        ↓
do not infer benignity, malignancy exclusion, TB, asbestos, ossification, or vascular disease
        ↓
preserve conflicts and missing evidence
        ↓
bounded assessment
        ↓
doctor review required
```
