# PULMONARY_MALIGNANCY_POLICY.md

## Integration target

Integrate this module under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/pulmonary_malignancy/
├── PULMONARY_MALIGNANCY_EVIDENCE.md
├── PULMONARY_MALIGNANCY_POLICY.md
└── references.md
```

Do not create `medvision-pulmonary-malignancy`.

## Progressive-loading trigger

Load this module when at least one of the following is present:

1. Canonical AI finding:
   - `Nodule/Mass`
2. Trusted human/CT characterization:
   - pulmonary nodule;
   - pulmonary mass;
   - suspicious focal pulmonary lesion;
   - spiculation or other suspicious nodule morphology.
3. `Other lesion` later characterized as a pulmonary nodule/mass.
4. CT-detected pulmonary nodule/mass despite negative/no-finding CXR.
5. Explicit pathology/cytology involving a pulmonary lesion.
6. Explicit clinician/radiologist malignancy concern.

Do not load solely because:
- generic Calcification is positive;
- Pleural thickening is positive;
- Lung Opacity is positive;
- an unrelated chest finding is positive.

## Reasoning procedure

### Step 1 — Identify lesion provenance

Capture:
- source modality;
- canonical AI finding;
- external report;
- lesion identity;
- size/morphology/location if actually supplied.

Do not fuse lesions by assumption.

### Step 2 — Establish modality/context

Determine:
- CXR only;
- incidental CT;
- screening CT;
- symptomatic diagnostic CT;
- unknown.

Guideline scope follows modality/context.

### Step 3 — Preserve morphology

Use supplied CT/radiology descriptors.

Do not invent:
- spiculation;
- solid component;
- benign calcification pattern;
- fat;
- cavitation;
- upper-lobe location.

### Step 4 — Evaluate temporal evidence

Only assign growth/stability when:
- comparable prior imaging exists;
- same lesion correspondence is supported;
- dates/measurements are sufficient.

Otherwise:
`growth_status: unknown`.

### Step 5 — Gather clinical risk context

Preserve supplied:
- age;
- smoking;
- prior malignancy;
- exposure/family history;
- external clinician risk estimate.

Do not generate hidden malignancy probability.

### Step 6 — Assign bounded state

```text
CXR Nodule/Mass only
+ insufficient characterization/risk context
→ IMAGING_LESION_WITHOUT_SUFFICIENT_MALIGNANCY_CONTEXT

CT lesion
+ incomplete morphology/growth/risk context
→ PULMONARY_MALIGNANCY_CONCERN_INDETERMINATE

suspicious CT morphology and/or true growth
+ compatible risk context
→ PULMONARY_MALIGNANCY_CONCERN_SUPPORTED

trusted conflict
→ PULMONARY_MALIGNANCY_CONCERN_CONFLICTED

insufficient evidence for concern
→ PULMONARY_MALIGNANCY_NOT_ESTABLISHED

explicit pathology confirms pulmonary malignancy
→ PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY
```

### Step 7 — Resolve origin conservatively

If pathology confirms malignancy but primary-vs-metastatic origin is not explicitly established:

`MALIGNANCY_ORIGIN_UNRESOLVED`

Do not infer primary lung cancer.

### Step 8 — Handle competing disease hypotheses

If pneumonia/inflammatory disease is also plausible:
- preserve both;
- avoid double counting shared imaging evidence;
- do not force a winner.

### Step 9 — Keep action boundary

No autonomous:
- CT/PET ordering;
- biopsy;
- bronchoscopy;
- surgery;
- surveillance interval;
- oncology treatment.

### Step 10 — Output

Return:
- malignancy concern state;
- lesion provenance;
- modality/context;
- morphology;
- temporal behavior;
- risk context;
- guideline scope notes;
- pathology;
- competing hypotheses;
- conflicts/missing data;
- uncertainty;
- doctor review.
