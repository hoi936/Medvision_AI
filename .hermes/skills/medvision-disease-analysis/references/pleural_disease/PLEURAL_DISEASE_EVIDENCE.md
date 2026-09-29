# PLEURAL_DISEASE_EVIDENCE.md

## 0. Scope

Disease Analysis v2 module for:

**Pleural Disease / Pleural Malignancy Concern / Malignant Pleural Effusion / Mesothelioma Concern / Pleural Infection Differential**

This is not:
- a new VinBigData finding skill;
- a new top-level Hermes skill;
- a treatment, drainage, biopsy, oncology, or surgery engine.

Target flow remains:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ pleural_disease reference module
```

Core boundaries:

```text
Pleural effusion != malignant pleural effusion
Pleural thickening != pleural malignancy
Pleural calcification != asbestos exposure
Pleural plaque != mesothelioma
Asbestos exposure != mesothelioma
Negative cytology != malignancy universally excluded
```

---

## 1. Disease-analysis states

MedVision internal states:

```text
PLEURAL_DISEASE_HYPOTHESIS_SUPPORTED
PLEURAL_DISEASE_HYPOTHESIS_INDETERMINATE
PLEURAL_ETIOLOGY_UNRESOLVED

PLEURAL_MALIGNANCY_CONCERN_SUPPORTED
PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE
PLEURAL_MALIGNANCY_CONCERN_CONFLICTED
PLEURAL_MALIGNANCY_NOT_ESTABLISHED

MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED
CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION
PATHOLOGY_CONFIRMED_PLEURAL_MALIGNANCY

MESOTHELIOMA_CONCERN_SUPPORTED
MESOTHELIOMA_NOT_ESTABLISHED
PATHOLOGY_CONFIRMED_MESOTHELIOMA

PLEURAL_INFECTION_CONCERN_SUPPORTED
PLEURAL_INFECTION_NOT_ESTABLISHED

ASBESTOS_RELATED_PLEURAL_DISEASE_CONCERN
```

These are bounded reasoning states, not final clinician diagnoses unless explicit pathology/cytology confirmation is supplied.

---

## 2. Upstream image findings

Relevant VinBigData finding evidence may include:
- `Pleural effusion`
- `Pleural thickening`
- `Calcification`
- `Other lesion`
- associated `Lung Opacity` / `Consolidation` when relevant to infection differential

Existing finding skills remain authoritative.

### Guardrails

`Pleural effusion POSITIVE` does not establish:
- heart failure;
- parapneumonic effusion;
- empyema;
- malignant pleural effusion;
- hemothorax;
- transudate/exudate.

`Pleural thickening POSITIVE` does not establish:
- asbestos exposure;
- pleural plaque;
- mesothelioma;
- metastatic pleural malignancy;
- prior TB or infection.

Generic `Calcification POSITIVE` does not establish pleural localization.

---

## 3. Pleural effusion disease reasoning

Pleural effusion is a finding with broad differential diagnosis.

Etiologic reasoning may use supplied:
- clinical context;
- serum/pleural-fluid studies;
- cytology;
- microbiology;
- CT/US morphology;
- pathology;
- known cardiac, infectious, malignant, hepatic, renal, or autoimmune disease.

If these are incomplete:

`PLEURAL_ETIOLOGY_UNRESOLVED`

Do not force a single etiology from CXR appearance alone.

---

## 4. Malignant pleural effusion boundary

A pleural effusion becomes disease-level malignant only when explicit source evidence supports pleural malignancy.

### Allowed confirmed state

If pleural-fluid cytology explicitly reports malignant cells in the pleural fluid:

`CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION`

Preserve:
- specimen source;
- date;
- tumor type if explicitly reported;
- whether origin is known or unknown.

### Not enough for confirmation

Do not diagnose MPE from:
- unilateral effusion;
- recurrent effusion;
- large effusion;
- bloody appearance alone;
- CT pleural thickening/nodularity alone;
- known cancer alone without pleural involvement evidence;
- elevated serum/pleural biomarkers alone.

If concern is present but confirmation is absent:

`MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED`

and possibly:

`PLEURAL_MALIGNANCY_CONCERN_SUPPORTED`

or:

`PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE`

---

## 5. Negative cytology

BTS 2023 explicitly notes that negative pleural-fluid cytology does not exclude pleural malignancy and may require further diagnostic consideration.

MedVision behavior:

```text
negative cytology
!=
malignancy excluded
```

If imaging/clinical concern remains:
- preserve negative cytology;
- preserve ongoing concern;
- do not silently resolve the case as benign.

For mesothelioma specifically, cytology can be falsely negative and tissue diagnosis is often required.

---

## 6. Pleural CT morphology

Trusted CT/US may provide pleural morphology such as:
- pleural nodularity;
- circumferential pleural thickening;
- mediastinal pleural involvement;
- focal pleural mass;
- enhancing pleural thickening;
- loculation;
- visceral pleural thickening / split-pleura sign;
- extrapleural fat changes.

### Malignancy concern

Features such as pleural nodularity, circumferential thickening, and mediastinal pleural involvement may raise concern for malignancy in context.

They do not prove:
- mesothelioma;
- metastatic disease;
- a specific histology.

### Infection concern

Features such as:
- lentiform pleural collection;
- visceral pleural thickening / split-pleura sign;
- extrapleural fat hypertrophy/density change;
- accompanying consolidation;

may support pleural infection concern.

These imaging signs have overlap and limited sensitivity.

Do not convert them directly into empyema or bacterial etiology without broader evidence.

---

## 7. Pleural thickening

Pleural thickening has multiple possible causes.

Potential supplied contexts include:
- chronic/recurrent pleural irritation;
- prior effusion;
- prior pneumothorax;
- infection;
- asbestos exposure;
- metastatic disease;
- lymphoma;
- mesothelioma.

Generic CXR pleural thickening is therefore nonspecific.

If CT explicitly characterizes malignant-appearing morphology:

`PLEURAL_MALIGNANCY_CONCERN_SUPPORTED`

may be appropriate.

If CT characterization is incomplete:

`PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE`

---

## 8. Pleural plaques and asbestos-related pleural disease

Fleischner 2024 describes pleural plaques as focal fibrohyaline parietal-pleural lesions, often partially calcified, and usually associated with prior exposure to fibrous silicates such as asbestos.

### MedVision rule

Only use `pleural plaque` when explicitly characterized by trusted imaging/human source.

If pleural plaques are explicitly identified:

`ASBESTOS_RELATED_PLEURAL_DISEASE_CONCERN`

may be supported when exposure context is compatible.

However:

```text
pleural plaque != mesothelioma
```

and:

```text
asbestos exposure != mesothelioma
```

Generic `Calcification` or `Pleural thickening` from CXR must not be relabeled as plaque.

---

## 9. Mesothelioma concern

Mesothelioma requires disease-specific diagnostic evaluation and commonly tissue pathology with immunohistochemistry.

### Concern may be raised by combinations such as

- unilateral pleural thickening;
- pleural effusion;
- pleural nodularity/mass;
- known occupational asbestos exposure;
- compatible CT morphology;
- persistent unexplained unilateral pleural disease.

These can support:

`MESOTHELIOMA_CONCERN_SUPPORTED`

but not a confirmed diagnosis.

### Confirmed state

Only explicit pathology confirming malignant pleural mesothelioma may emit:

`PATHOLOGY_CONFIRMED_MESOTHELIOMA`

Preserve:
- histologic subtype if explicitly reported;
- IHC/pathology provenance;
- specimen/date.

Do not infer mesothelioma from:
- asbestos exposure alone;
- pleural plaques alone;
- calcified plaques alone;
- unilateral effusion alone;
- suspicious CT alone.

---

## 10. Secondary pleural malignancy

If pathology explicitly confirms malignant pleural involvement from another primary tumor:

`PATHOLOGY_CONFIRMED_PLEURAL_MALIGNANCY`

Preserve primary origin only if explicitly established.

Do not infer:
- lung primary from pleural metastasis alone;
- mesothelioma from pleural malignancy alone.

If origin is uncertain, keep:

`PLEURAL_ETIOLOGY_UNRESOLVED`

or a source-specific unresolved-origin field.

---

## 11. Other lesion and pleural characterization

If canonical AI says:

```text
Other lesion POSITIVE
```

and a trusted CT/radiologist later characterizes the same abnormality as a pleural mass/nodule/thickening:
- preserve `Other lesion` AI provenance;
- preserve external pleural characterization;
- allow this pleural disease module to activate;
- do not retroactively change the AI class.

Do not auto-select `Pleural thickening` unless the canonical AI `Pleural thickening` decision is POSITIVE.

---

## 12. No Finding CXR + CT pleural disease

A CXR `No finding` state does not exclude CT-detected pleural disease.

If CT shows pleural nodularity/thickening or a small effusion:
- preserve CXR No Finding;
- preserve CT evidence;
- disease reasoning may proceed from CT;
- do not rewrite the prior CXR output.

Symptoms alone do not create a No Finding contradiction.

---

## 13. Pleural infection

Pleural infection requires integrated evidence.

Potentially relevant supplied evidence:
- fever/inflammatory syndrome;
- pneumonia;
- pleural loculation;
- split-pleura sign;
- purulent pleural fluid;
- positive pleural-fluid microbiology;
- other clinician-documented infection evidence.

`PLEURAL_INFECTION_CONCERN_SUPPORTED` may be used when multiple domains align.

Do not infer:
- empyema from effusion alone;
- bacterial infection from imaging alone;
- drainage requirement.

If evidence is insufficient:

`PLEURAL_INFECTION_NOT_ESTABLISHED`

---

## 14. Pneumonia + pleural effusion

If pneumonia hypothesis and pleural effusion coexist:
- preserve both;
- do not automatically call parapneumonic effusion;
- do not automatically call complicated parapneumonic effusion;
- do not automatically call empyema.

These labels require additional pleural-fluid/imaging/clinical evidence.

---

## 15. Heart failure + pleural effusion

Existing Heart Failure disease reasoning remains independent.

Pleural effusion with HF evidence may support a cardiogenic cause, but:
- unilateral effusion is not automatically malignant;
- bilateral effusion is not automatically HF;
- effusion alone is not HF confirmation.

Preserve competing etiologies when data are incomplete.

---

## 16. Pulmonary malignancy + pleural abnormality

Existing Pulmonary Malignancy Concern module remains independent.

If pulmonary malignancy and pleural disease coexist:
- preserve both;
- do not infer pleural metastasis without direct evidence;
- do not infer malignant pleural effusion without cytology/pathology/equivalent source evidence.

---

## 17. Pleural-fluid biochemical categories

Do not classify transudate/exudate unless the necessary pleural/serum measurements and a validated rule are explicitly implemented and complete.

This v1 module does not silently compute Light's criteria.

If an external clinician/lab report explicitly states transudate/exudate:
- preserve the result and provenance.

Do not infer malignancy from exudate alone.

---

## 18. Autoimmune / TB pleural disease

BTS 2023 includes specific tests for selected scenarios, but MedVision v1 does not autonomously diagnose TB or lupus pleuritis from one biomarker.

Examples:
- elevated ADA alone does not universally confirm TB;
- pleural-fluid ANA alone does not establish lupus pleuritis;
- TB pleural disease requires broader clinical/microbiological/tissue context.

A future TB/chronic-infection disease module should own the detailed TB reasoning.

---

## 19. Pathology/cytology conflict

Examples:
- suspicious CT but negative cytology;
- malignant cytology but imaging subtle;
- benign biopsy with uncertain lesion correspondence;
- nondiagnostic biopsy.

Preserve:
- source;
- specimen;
- date;
- lesion correspondence;
- diagnostic certainty.

Use:

`PLEURAL_MALIGNANCY_CONCERN_CONFLICTED`

when evidence remains genuinely unresolved.

A nondiagnostic biopsy is not benign pathology.

---

## 20. AI score semantics

Never convert:

```text
Pleural thickening score = 0.90
Pleural effusion score = 0.95
```

into:
- 90% probability of mesothelioma;
- 95% probability of malignant pleural effusion;
- asbestos-exposure probability.

Image-model scores remain model outputs only.

---

## 21. Safety

Independent severe evidence such as:
- respiratory failure;
- hemodynamic instability;
- severe sepsis;
- tension physiology from another pleural emergency;

may propagate to existing:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do not autonomously:
- order thoracentesis;
- order CT/PET;
- perform pleural biopsy;
- place chest tube/IPC;
- prescribe antibiotics;
- perform pleurodesis;
- refer to oncology/surgery;
- start cancer treatment.

---

## 22. Recommended output

```yaml
disease_hypothesis:
  name: pleural_disease
  status: not_established|indeterminate|supported|conflicted

pleural_findings:
  effusion: unknown|absent|present
  thickening: unknown|absent|present
  plaque: unknown|absent|present
  nodularity_or_mass: unknown|absent|present
  calcification_localization: unknown|pleural|nonpleural

etiology:
  status: unresolved|supported
  candidate: null
  evidence: []

malignancy:
  concern: not_established|indeterminate|supported|conflicted
  malignant_pleural_effusion: not_established|cytology_confirmed
  pathology_confirmed_pleural_malignancy: false
  origin: unknown

mesothelioma:
  concern: not_established|possible|supported
  pathology_confirmed: false
  histology: unknown

infection:
  concern: not_established|possible|supported
  microbiology: []
  fluid_features: []
  imaging_features: []

asbestos_context:
  exposure_history: unknown
  pleural_plaque: unknown
  asbestos_related_pleural_disease_concern: false

cytology:
  status: not_done|negative|nondiagnostic|malignant
  source: null

pathology:
  status: not_done|negative|nondiagnostic|malignant
  source: null

supporting_evidence: []
contradicting_evidence: []
missing_evidence: []
conflicts: []
competing_hypotheses: []

safety:
  priority: routine|elevated|high
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true
```

---

## 23. Hard constraints

Hermes MUST NOT:

1. Convert Pleural effusion directly into malignant pleural effusion.
2. Convert Pleural thickening directly into pleural malignancy.
3. Convert generic Calcification into pleural calcification.
4. Infer pleural plaque from Calcification/Pleural thickening alone.
5. Infer asbestos exposure from generic pleural findings alone.
6. Convert pleural plaque directly into mesothelioma.
7. Convert asbestos exposure directly into mesothelioma.
8. Exclude pleural malignancy because CT is negative.
9. Exclude pleural malignancy because cytology is negative.
10. Treat nondiagnostic cytology/biopsy as benign.
11. Diagnose mesothelioma from cytology/imaging alone unless explicit source diagnosis establishes it.
12. Infer pleural metastasis from pulmonary malignancy without direct evidence.
13. Infer empyema/parapneumonic effusion from effusion alone.
14. Infer bacterial infection from CT signs alone.
15. Infer transudate/exudate without complete validated fluid data or explicit external interpretation.
16. Infer TB/lupus pleuritis from one biomarker alone.
17. Rewrite CXR No Finding because CT later shows pleural disease.
18. Auto-select Pleural thickening skill from external CT characterization alone.
19. Convert AI score into malignancy/infection probability.
20. Issue autonomous imaging, drainage, biopsy, medication, oncology, surgery, or disposition actions.
21. Omit doctor review.
