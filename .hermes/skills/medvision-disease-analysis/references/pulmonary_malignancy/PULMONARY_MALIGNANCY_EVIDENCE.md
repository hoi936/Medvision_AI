# PULMONARY_MALIGNANCY_EVIDENCE.md

## 0. Scope

This document defines MedVision Disease Analysis v2 reasoning for:

**Pulmonary malignancy concern / lung nodule-mass risk reasoning**

This is not:
- a new VinBigData image-finding skill;
- a new top-level Hermes skill;
- an autonomous cancer-diagnosis engine;
- a biopsy/surgery/surveillance engine.

Target flow remains:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ pulmonary-malignancy reference module
```

The central rule is:

```text
Nodule/Mass != Lung Cancer
```

and separately:

```text
Suspicious morphology / growth / risk factors
!=
Pathology-confirmed malignancy
```

---

## 1. Disease-analysis states

MedVision internal system-policy states:

```text
PULMONARY_MALIGNANCY_CONCERN_SUPPORTED
PULMONARY_MALIGNANCY_CONCERN_INDETERMINATE
IMAGING_LESION_WITHOUT_SUFFICIENT_MALIGNANCY_CONTEXT
PULMONARY_MALIGNANCY_CONCERN_CONFLICTED
PULMONARY_MALIGNANCY_NOT_ESTABLISHED
PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY
MALIGNANCY_ORIGIN_UNRESOLVED
```

These are bounded reasoning states. Except for the pathology-confirmed state when explicit pathology is supplied, they are not final cancer diagnoses.

---

## 2. Imaging terminology and modality

### 2.1 Nodule vs mass

The Fleischner Society glossary defines a pulmonary nodule as a circumscribed focal opacity <=30 mm.

A lesion larger than 30 mm is termed a mass.

### Hermes behavior

Only use the nodule-vs-mass distinction when:
- lesion size is reliably supplied;
- modality/measurement quality supports it.

Do not infer `mass` solely from a CXR AI class named `Nodule/Mass`.

Do not infer a precise CT-size category from a chest-radiograph bounding box.

---

## 3. CXR Nodule/Mass output

The existing `Nodule/Mass` skill remains the source of radiographic evidence.

A CXR AI output can support:

```text
FOCAL_PULMONARY_LESION_EVIDENCE
```

but not:
- primary lung cancer;
- metastatic disease;
- benignity;
- histology;
- stage.

If the lesion is only identified on CXR:
- morphology may remain limited;
- CT-specific nodule guidelines must not be applied as if CT characterization exists.

---

## 4. CT characterization

When trusted CT provides specific morphology, preserve:
- solid / part-solid / non-solid;
- size;
- margins;
- spiculation;
- calcification pattern;
- fat;
- location;
- multiplicity;
- temporal behavior;
- cavitation or other supplied descriptors.

CT morphology may increase or decrease concern, but imaging does not equal pathology.

### Suspicious morphology

Examples such as spiculation or other explicitly suspicious morphology can raise malignancy concern in the proper CT context [S1][S2][S3].

Do not convert:

```text
spiculated nodule
```

into:

```text
cancer confirmed
```

---

## 5. Calcification and fat

Generic `Calcification` from the VinBigData classifier does not establish benignity.

Only if trusted CT/radiology explicitly characterizes the same lesion with a recognized benign pattern may concern be reduced.

Examples recognized in lung-screening CT context include:
- complete calcification;
- central calcification;
- popcorn calcification;
- concentric-ring calcification;
- fat-containing nodule.

### Guardrails

Do not:
- infer a benign calcification pattern from a generic Calcification AI class;
- assume calcification and Nodule/Mass refer to the same lesion without correspondence evidence;
- use screening-specific Lung-RADS categories outside screening CT context.

---

## 6. Temporal behavior / growth

True interval growth can increase malignancy concern.

Hermes may use `growth` only when:
- a prior comparable study actually exists;
- the same lesion has been matched with sufficient confidence;
- timing and measurement source are supplied.

Do not infer growth from:
- two unrelated lesions;
- different image-plane boxes without lesion matching;
- one current study;
- vague history such as "previous abnormal CXR" without comparable lesion data.

If prior data are absent:

```text
growth_status: unknown
```

Do not silently convert missing prior imaging into stability.

---

## 7. Stability / decrease

Stability or decrease can lower concern in some lesion types and guideline contexts, but v1 does not encode a universal "stable = benign" rule.

Reason:
- solid and subsolid nodules behave differently;
- duration and modality matter;
- clinical context matters.

Therefore:
- preserve actual duration of stability;
- preserve lesion type;
- do not universally declare benignity.

---

## 8. Clinical risk context

Pulmonary-nodule guidelines assess lesion risk in combination with patient context.

Potentially relevant supplied context can include:
- age;
- smoking history;
- prior malignancy;
- environmental/occupational exposures;
- family history;
- upper-lobe location or suspicious CT morphology;
- prior imaging behavior.

### MedVision v1 policy

Do not assign a numeric malignancy probability from these factors unless:
- a separately validated risk calculator is explicitly implemented;
- all required inputs are present;
- the calculator/model is named and provenance is preserved.

No hidden Brock, Mayo, Herder, or other score is implemented in v1.

If an external clinician provides a malignancy probability:
- preserve it as external evidence;
- do not relabel it as MedVision's own estimate.

---

## 9. Multiple nodules

Multiple nodules do not automatically mean pulmonary metastases.

Possible explanations remain broad.

Hermes must preserve:
- number of lesions;
- size/morphology of each lesion where supplied;
- dominant/most suspicious lesion only if the source explicitly identifies it;
- uncertainty of shared etiology.

Do not infer:
- metastatic disease;
- multifocal primary cancer;
- infection;
- inflammatory disease;

from multiplicity alone.

---

## 10. Other lesion later characterized as pulmonary nodule/mass

If upstream AI says:

```text
Other lesion POSITIVE
```

and a trusted human/CT later identifies that same abnormality as a pulmonary nodule/mass:
- preserve `Other lesion` AI provenance;
- preserve external characterization;
- malignancy module may activate from the external characterization;
- do not claim AI originally predicted Nodule/Mass.

Do not auto-select the Nodule/Mass finding skill unless the canonical AI `Nodule/Mass` decision is POSITIVE.

---

## 11. No Finding CXR + CT nodule

`No finding` from the CXR classifier does not exclude a CT-detected pulmonary nodule.

If CT demonstrates a nodule:
- preserve the CXR No Finding state;
- preserve CT lesion evidence;
- do not create a No Finding contradiction unless a canonical target CXR finding is also POSITIVE under the existing policy;
- allow malignancy concern reasoning from CT.

Different modalities and sensitivity must remain explicit.

---

## 12. Mass lesions

A reliably measured lesion >30 mm can be termed a mass.

A mass has greater clinical concern than a tiny indeterminate nodule, but:

```text
mass != cancer confirmed
```

Do not:
- infer histology;
- infer stage;
- infer resectability;
- infer metastasis.

Pathology or equivalent definitive evidence is required for confirmed malignancy.

---

## 13. Pathology

### Explicit pathology-confirmed malignancy

Only if actual pathology/cytology evidence is supplied and explicitly confirms malignancy may Hermes emit:

`PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY`

Preserve:
- specimen/source;
- date;
- histology if explicitly reported;
- primary vs metastatic origin if explicitly established.

### Origin

If malignancy is confirmed in a pulmonary lesion but origin is not established:

`MALIGNANCY_ORIGIN_UNRESOLVED`

Do not infer:
- primary lung cancer;
- pulmonary metastasis;
- histologic subtype.

If pathology explicitly states lung adenocarcinoma, squamous cell carcinoma, metastatic carcinoma, etc., preserve the supplied diagnosis and provenance.

---

## 14. Pathology-imaging conflict

Examples:
- highly suspicious imaging but biopsy reports benign tissue;
- pathology sample is nondiagnostic;
- radiology lesion and sampled lesion may not correspond.

Do not silently collapse disagreement.

Use:
- `EVIDENCE_CONFLICT` when true conflict exists;
- `PULMONARY_MALIGNANCY_CONCERN_CONFLICTED` when disease-level interpretation remains unresolved.

A nondiagnostic biopsy is not equivalent to benign pathology.

---

## 15. Competing inflammatory/infectious explanations

A focal opacity, mass-like consolidation, or nodule may have infectious/inflammatory mimics.

If pneumonia/infection evidence coexists:
- preserve both hypotheses;
- do not force cancer or pneumonia as the winner without sufficient evidence;
- shared imaging evidence must not be double-counted.

A resolving lesion on appropriate prior imaging may lower concern, but do not invent resolution if not actually supplied.

---

## 16. Screening vs incidental vs symptomatic context

Keep context explicit:

```yaml
detection_context:
  screening_ct: true|false|unknown
  incidental_ct: true|false|unknown
  chest_radiograph: true|false|unknown
  symptomatic_workup: true|false|unknown
```

Do not:
- apply Lung-RADS to nonscreening CT;
- apply Fleischner CT tables directly to CXR AI output;
- apply incidental-nodule pathways when known active cancer or another exclusion makes the source guideline inapplicable.

If guideline applicability is uncertain:
- preserve scope limitation;
- do not fabricate a management category.

---

## 17. Disease-state examples

### State A — CXR lesion only

```text
Nodule/Mass POSITIVE
no CT
no prior imaging
no risk context
```

Output:

`IMAGING_LESION_WITHOUT_SUFFICIENT_MALIGNANCY_CONTEXT`

### State B — suspicious CT lesion + risk context

```text
CT pulmonary nodule
+ suspicious morphology
+ true interval growth
+ relevant clinical risk context
```

Output may be:

`PULMONARY_MALIGNANCY_CONCERN_SUPPORTED`

This is not cancer confirmation.

### State C — indeterminate lesion

```text
CT nodule
morphology incomplete
growth unknown
risk context incomplete
```

Output:

`PULMONARY_MALIGNANCY_CONCERN_INDETERMINATE`

### State D — benign-pattern characterization

```text
same lesion on CT
explicit complete/central/popcorn/concentric-ring calcification
or fat-containing morphology
```

Concern may be lower.

Do not infer this pattern from generic AI calcification.

### State E — pathology confirms malignancy

Actual pathology confirming malignancy:

`PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY`

Only pathology-confirmed state may be represented as confirmed malignancy.

---

## 18. AI score semantics

Never convert:

```text
Nodule/Mass score = 0.92
```

into:

```text
92% probability of lung cancer
```

The AI score is an image-model output, not a patient-level malignancy probability.

---

## 19. Safety and action boundary

Pulmonary malignancy concern is generally a diagnostic-review issue, not an autonomous emergency state.

If independent evidence shows:
- acute respiratory compromise;
- hemoptysis with instability;
- another high-risk syndrome;

existing safety policy may emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do not autonomously:
- order CT/PET;
- recommend biopsy;
- schedule bronchoscopy;
- recommend surgery;
- start oncology treatment;
- stage cancer;
- make surveillance intervals.

Those are clinician decisions outside this disease-analysis v1 module.

---

## 20. Recommended output

```yaml
disease_hypothesis:
  name: pulmonary_malignancy
  status: not_established|indeterminate|concern_supported|conflicted|pathology_confirmed

lesion_evidence:
  source_modalities: []
  lesions: []
  # each:
  # - id:
  #   size:
  #   morphology:
  #   location:
  #   calcification_pattern:
  #   fat:
  #   growth_status:
  #   prior_comparison:
  #   source:

risk_context:
  age: unknown
  smoking_history: unknown
  prior_malignancy: unknown
  exposures: []
  family_history: unknown
  external_risk_estimate: null

guideline_context:
  screening_ct: unknown
  incidental_ct: unknown
  cxr_only: unknown
  guideline_scope_notes: []

pathology:
  available: false
  result: unknown
  histology: unknown
  origin: unknown
  specimen_source: unknown

competing_hypotheses: []
supporting_evidence: []
contradicting_evidence: []
missing_evidence: []
conflicts: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true
```

---

## 21. Hard constraints

Hermes MUST NOT:

1. Convert Nodule/Mass directly into lung cancer.
2. Convert a mass >30 mm directly into cancer.
3. Convert spiculation directly into cancer.
4. Convert growth directly into cancer.
5. Infer growth without true comparable prior imaging and lesion matching.
6. Infer stability when prior imaging is missing.
7. Infer benignity from generic Calcification.
8. Assume Calcification and Nodule/Mass are the same lesion without correspondence evidence.
9. Apply Lung-RADS outside lung-cancer screening CT.
10. Apply Fleischner CT tables directly to a CXR bounding box.
11. Infer metastases from multiple nodules.
12. Infer primary lung cancer from pathology-confirmed malignancy when origin is not established.
13. Treat nondiagnostic biopsy as benign pathology.
14. Calculate a hidden malignancy probability.
15. Convert AI score into cancer probability.
16. Erase CXR No Finding because CT later detects a nodule.
17. Auto-select Nodule/Mass skill from external characterization alone.
18. Force pneumonia-vs-malignancy winner without evidence.
19. Issue autonomous CT/PET/biopsy/bronchoscopy/surgery/surveillance/treatment instructions.
20. Omit doctor review.
