# NODULE_MASS_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Nodule/Mass** trong MedVision Hermes.

`Nodule/Mass` trong VinBigData phải được xử lý trước hết như một **radiographic focal pulmonary lesion finding**, không phải là chẩn đoán lung cancer hay malignancy.

Phạm vi v1:
- adult chest-radiograph finding;
- distinction between nodule and mass terminology;
- CT characterization after an indeterminate CXR finding;
- solid / ground-glass / part-solid morphology when CT data are available;
- malignancy-risk reasoning without converting risk into diagnosis;
- prior imaging / growth context;
- Fleischner 2017 scope boundaries;
- BTS / ACCP risk-based context;
- missing evidence, conflict detection, uncertainty, and doctor review.

Không tự mở rộng v1 sang:
- pediatric pulmonary nodules;
- lung-cancer screening workflows;
- immunocompromised-host-specific algorithms;
- known-primary-cancer metastatic workup;
- autonomous biopsy/PET/surgical selection.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society Glossary 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **primary terminology, nodule/mass definitions, morphology, CT characterization language**

### S2 — ACR Appropriateness Criteria
**Incidentally Detected Indeterminate Pulmonary Nodule. American College of Radiology Appropriateness Criteria. Revised 2023.**  
URL: https://acsearch.acr.org/docs/69455/Narrative  
Role: **CXR-to-CT next-imaging pathway for an indeterminate pulmonary nodule**

### S3 — Fleischner Society 2017
**MacMahon H, Naidich DP, Goo JM, et al. Guidelines for Management of Incidental Pulmonary Nodules Detected on CT Images: From the Fleischner Society 2017. Radiology. 2017.**  
PMID: 28240562  
DOI: 10.1148/radiol.2017161659  
Role: **CT-detected incidental pulmonary nodule management framework and malignancy-risk factors**

### S4 — BTS Pulmonary Nodule Guideline 2015
**Callister MEJ, Baldwin DR, Akram AR, et al. British Thoracic Society guidelines for the investigation and management of pulmonary nodules. Thorax. 2015.**  
PMID: 26082159  
DOI: 10.1136/thoraxjnl-2015-207168  
Role: **risk-based nodule evaluation, risk calculators, PET-CT/biopsy/surveillance context**

### S5 — ACCP/CHEST 2013
**Gould MK, Donington J, Lynch WR, et al. Evaluation of individuals with pulmonary nodules: when is it lung cancer? CHEST. 2013.**  
PMID: 23649456  
PMCID: PMC3749714  
DOI: 10.1378/chest.12-2351  
Role: **probability-of-malignancy reasoning, imaging characterization, benefit/harm balancing, patient preferences**

### Source precedence

1. S1 for terminology.
2. S2 for the specific CXR -> next-imaging question.
3. S3 for incidental CT-detected nodule management and risk factors.
4. S4/S5 for broader risk-based clinical management context.

---

## 2. Core semantic rule

A VinBigData `Nodule/Mass` output is:

`RADIOGRAPHIC_EVIDENCE_OF_A_FOCAL_PULMONARY_LESION`

It is NOT automatically:
- lung cancer;
- primary pulmonary malignancy;
- metastatic disease;
- benign granuloma;
- hamartoma;
- infection;
- an indication for PET-CT;
- an indication for biopsy;
- an indication for surgery.

The AI class combines two radiologic terms and therefore does not itself establish whether the lesion is a `nodule` or `mass` by size.

---

## 3. Nodule vs mass terminology

### S1

Fleischner 2024 defines a pulmonary nodule as a circumscribed, typically round opacity with average diameter `<= 30 mm`.

A mass is a circumscribed lesion `> 30 mm` in diameter.

A mass can contain solid, cavitary, cystic, or calcified components, and the term `mass-like` does not itself imply neoplastic etiology.

### Hermes behavior

If CT or trusted imaging provides a measured average lesion diameter:
- `<=30 mm` may be described with nodule terminology;
- `>30 mm` may be described with mass terminology.

Do NOT infer lesion size from:
- the VinBigData class name;
- the AI model score;
- a bounding-box width in pixels unless a validated physical-size conversion exists.

A `mass` is not synonymous with `malignancy`.

---

## 4. CXR finding -> CT characterization

### S2

ACR Variant 1 addresses an adult `>=35 years` with an incidentally detected indeterminate pulmonary nodule on chest radiograph.

In that scenario:
- `CT chest without IV contrast` is rated **Usually Appropriate** as the next imaging study.
- PET/CT and image-guided transthoracic needle biopsy are not rated as appropriate first next-imaging choices for that initial CXR-only variant.

### Hermes behavior

When:
- patient age is `>=35`; and
- the available evidence is only an indeterminate CXR Nodule/Mass finding; and
- no CT characterization is available;

Hermes may identify:

`CT_CHARACTERIZATION_RELEVANT`

as a clinician-facing missing-evidence / next-evaluation consideration.

It must NOT autonomously order CT.

It must NOT jump directly from an indeterminate CXR lesion to:
- PET-CT;
- biopsy;
- surgery.

### Scope boundary

Do not automatically apply the ACR `>=35` CXR variant to patients `<35`.

For younger patients:
- mark age/scope mismatch;
- leave evaluation to clinician-specific context.

---

## 5. CT morphology

### S1

On CT, nodules can be described by:
- attenuation: `solid`, `ground-glass`, `part-solid`;
- shape and margin;
- internal components such as calcium, fat, air/cystic components;
- relationship to fissures/pleura/bronchovascular structures.

Thin-section CT is important for accurate characterization of small nodules.

### Spiculation

S1 includes spiculation as a margin descriptor.

S3 identifies marginal spiculation as a malignancy risk factor.

### Hermes behavior

If CT morphology is explicitly supplied:
record:
- solid / ground-glass / part-solid;
- smooth / irregular / lobulated / spiculated margin if supplied;
- calcification/fat/cystic/cavitary components if supplied;
- location and multiplicity if supplied.

Do NOT infer missing morphology.

A spiculated lesion:
- can increase malignancy concern;
- does NOT establish histologic malignancy.

---

## 6. Fleischner 2017 scope

### S3

Fleischner 2017 applies to **incidentally encountered pulmonary nodules detected on CT** in adults `>=35 years`.

The recommendations are not intended for:
- lung cancer screening examinations;
- patients with known primary cancer at risk for metastasis;
- immunocompromised patients;
- adults younger than 35 years.

Management varies by:
- lesion size;
- solid vs subsolid morphology;
- multiplicity;
- patient/lesion risk factors;
- patient preferences.

### Hermes guardrail

Do NOT apply a Fleischner follow-up table when:
- there is only a CXR AI class and no CT characterization;
- lesion size is unknown;
- CT attenuation type is unknown where required;
- the patient falls outside guideline scope.

If not evaluable:

`fleischner_ct_guidance_evaluable: false`

and explain why.

---

## 7. Malignancy-risk reasoning

### S3 / S4 / S5

Pulmonary-nodule evaluation uses a combination of:
- lesion size;
- morphology;
- location;
- change/growth on prior imaging;
- patient clinical risk factors.

S3 specifically notes size and morphology as important risk factors and identifies spiculation as associated with malignancy.

S5 emphasizes:
- estimating probability of malignancy;
- imaging to characterize the lesion;
- weighing benefits and harms of surveillance, nonsurgical biopsy, and surgical approaches;
- incorporating patient preferences.

BTS provides risk calculators and a risk-based framework for investigation/management.

### Hermes behavior

Maintain a separate field:

`malignancy_risk_hypothesis`

Do NOT collapse it into:

`lung_cancer_diagnosis`

Use qualitative status unless an externally validated risk calculator is explicitly implemented with all required inputs.

Do not invent a malignancy percentage.

---

## 8. Prior imaging / growth

### S3 / S5

Prior imaging is clinically relevant because interval change/growth influences nodule assessment and management.

### Hermes behavior

If prior measurements are available:
- preserve date, modality, and size as supplied;
- identify documented growth/change without inventing a growth rate.

If no comparable prior imaging exists:
add:

`prior_imaging: missing`

Do NOT:
- assume stability;
- infer growth from separate AI scores;
- compare CXR pixel dimensions with CT millimeters as if equivalent.

---

## 9. Benign-appearing morphology guardrail

S1 recognizes that nodules may contain:
- calcification;
- fat;
- other complex components.

These characteristics matter for characterization.

### Hermes behavior

Record calcification/fat morphology when explicitly supplied.

Do NOT automatically label:
- every calcified nodule as benign;
- every fat-containing lesion as a specific benign diagnosis;

unless the trusted radiology interpretation or an applicable rule in the source pack supports that conclusion.

This v1 intentionally avoids encoding detailed calcification-pattern algorithms.

---

## 10. Multiple nodules

### S3 / S4

Guideline management differs between solitary and multiple nodules.

### Hermes behavior

If multiplicity is available:
- record the number/distribution if supplied;
- do not apply solitary-nodule logic blindly.

If the VinBigData `Nodule/Mass` class is positive but multiplicity is not supplied:
- mark multiplicity `unknown`.

Do not infer metastatic disease from multiplicity alone.

---

## 11. Supporting evidence model

### CXR_IMAGE_EVIDENCE
- VinBigData `Nodule/Mass`;
- model score;
- radiologist/manual interpretation;
- side/lobe if explicitly supplied;
- prior CXR if available.

### CT_CHARACTERIZATION
Potentially relevant:
- lesion diameter in mm;
- solid / ground-glass / part-solid;
- margins;
- location;
- multiplicity;
- calcification/fat/cavitation/cystic components;
- interval growth/change.

### CLINICAL_RISK_CONTEXT
Potentially relevant:
- age;
- smoking history;
- prior malignancy;
- family/risk history where supplied;
- immunocompromised status;
- symptoms.

### DEFINITIVE_EVIDENCE
Potentially relevant:
- pathology;
- clinician-confirmed diagnosis;
- longitudinal definitive imaging assessment.

---

## 12. Contradicting and conflicting evidence

### Not contradiction by itself
- no respiratory symptoms;
- no smoking history;
- younger age;
- normal routine labs.

These may alter malignancy risk but do not automatically negate the image finding.

### Direct evidence conflict

Examples:
- AI says `Nodule/Mass` while trusted human CXR review says no focal lesion;
- later definitive imaging shows that the apparent CXR lesion was not a pulmonary nodule/mass.

Emit:

`EVIDENCE_CONFLICT`

and preserve both sources.

### CXR-vs-CT discordance

If CXR AI is positive but CT reports no corresponding pulmonary lesion:
- preserve CXR AI evidence;
- treat CT as stronger lesion-characterization evidence;
- report discordance;
- do not silently continue treating cancer risk as if CT confirmed the lesion.

---

## 13. Missing evidence

Potential missing fields:
- patient age;
- CT characterization;
- lesion size;
- solid/subsolid type;
- margins;
- location;
- multiplicity;
- prior imaging;
- growth/change;
- smoking history;
- prior malignancy;
- immune status;
- pathology if a diagnosis is being claimed.

Missing data is not negative evidence.

---

## 14. Safety policy

A pulmonary nodule/mass by itself is not automatically an acute emergency.

If case data show an independent acute safety issue such as:
- severe respiratory compromise;
- major hemoptysis;
- physiological instability;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`, not a statement that all nodules/masses are emergent.

Do not autonomously order:
- CT;
- PET-CT;
- biopsy;
- bronchoscopy;
- surgery;
- oncologic treatment.

---

## 15. AI score interpretation

AI model score is not automatically:
- malignancy probability;
- lung-cancer probability;
- lesion size;
- growth rate;
- stage;
- urgency.

Keep separate:

```text
image_model_score
radiographic_focal_lesion
ct_characterization
malignancy_risk_hypothesis
definitive_diagnosis
uncertainty
```

Never convert `0.94` into:
- “94% probability of lung cancer”;
- “94% probability this lesion is malignant”;
- a calibrated patient-level disease probability

unless a separately validated calibration/risk model explicitly supports that interpretation.

---

## 16. Recommended structured output

```yaml
finding: nodule_mass
finding_type: radiographic_focal_lesion

cxr_evidence:
  model_score: null
  localization: unknown
  radiologist_interpretation: unknown

ct_characterization:
  available: false
  size_mm: null
  terminology: unknown
  attenuation: unknown
  margin: unknown
  location: unknown
  multiplicity: unknown
  internal_components: []
  prior_growth: unknown

scope:
  age: unknown
  acr_cxr_variant_evaluable: false
  fleischner_ct_guidance_evaluable: false
  known_primary_cancer: unknown
  immunocompromised: unknown
  screening_context: unknown

malignancy_risk_hypothesis:
  status: unknown
  supporting: []
  reducing: []
  quantitative_probability: null

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

1. Equate `Nodule/Mass` with lung cancer.
2. Equate `mass >30 mm` with malignancy.
3. Equate spiculation with histologic cancer.
4. Invent nodule/mass size from the AI class or score.
5. Apply Fleischner 2017 CT tables to an uncharacterized CXR AI finding.
6. Apply Fleischner 2017 outside its scope without explicit qualification.
7. Jump directly from a CXR-only indeterminate lesion to PET/biopsy/surgery.
8. Infer metastasis from multiple nodules alone.
9. Infer benignity from any calcification/fat mention without appropriate characterization.
10. Infer growth from changes in AI score.
11. Convert model score into malignancy/cancer probability.
12. Treat missing data as negative evidence.
13. Issue autonomous imaging/procedure/treatment orders.
14. Present a risk hypothesis as pathology-confirmed diagnosis.
15. Add unsourced medical rules.

---

## 18. Evidence gaps for v2

Potential additions:
- validated Brock/Mayo/Herder calculator implementation;
- Lung-RADS / screening-specific workflow;
- detailed benign calcification-pattern rules;
- detailed PET-CT interpretation;
- tissue-sampling approach selection;
- persistent subsolid-nodule algorithms;
- oncology-patient/metastatic workup;
- immunocompromised-host nodule differential;
- pediatric pulmonary nodules;
- automated volumetry/growth-rate rules.

Do not invent these detailed rules in v1.

---

## 19. Bottom line

```text
Nodule/Mass AI finding on CXR
        ↓
preserve as focal-lesion evidence
        ↓
check age / scope / prior imaging
        ↓
CT available?
├─ no  → incomplete characterization
│        CT_CHARACTERIZATION_RELEVANT when applicable
└─ yes → size + attenuation + margin + location + multiplicity + growth
        ↓
separate nodule/mass terminology
        ↓
estimate malignancy concern qualitatively
        ↓
do NOT convert concern to lung-cancer diagnosis
        ↓
identify missing/conflicting evidence
        ↓
bounded assessment
        ↓
doctor review required
```
