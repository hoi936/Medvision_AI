# PLEURAL_DISEASE_POLICY.md

## Integration target

Integrate this module under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/pleural_disease/
├── PLEURAL_DISEASE_EVIDENCE.md
├── PLEURAL_DISEASE_POLICY.md
└── references.md
```

Do not create a new top-level pleural-disease skill.

## Progressive-loading trigger

Load this module when at least one of the following is present:

1. Canonical AI findings:
   - `Pleural effusion`
   - `Pleural thickening`
2. Trusted CT/US/human pleural characterization:
   - pleural nodularity;
   - circumferential pleural thickening;
   - mediastinal pleural involvement;
   - pleural plaque;
   - pleural mass;
   - loculated effusion;
   - split-pleura sign;
   - other explicit pleural abnormality.
3. Pleural-fluid/cytology/pathology evidence.
4. Explicit clinician concern for:
   - malignant pleural effusion;
   - pleural malignancy;
   - mesothelioma;
   - pleural infection.
5. `Other lesion` later characterized as a pleural abnormality.

Do NOT activate solely from:
- generic `Calcification`;
- generic `Lung Opacity`;
- unrelated findings.

## Reasoning procedure

### Step 1 — Preserve upstream provenance

Keep the original AI finding labels and scores unchanged.

Do not remap:
- `Other lesion` to Pleural thickening;
- `Calcification` to pleural plaque;
- `Pleural effusion` to malignant pleural effusion.

### Step 2 — Establish modality and lesion correspondence

Capture:
- CXR;
- CT;
- ultrasound;
- pleural-fluid sample;
- cytology;
- pathology.

Do not assume findings across modalities/samples refer to the same lesion unless correspondence is supported.

### Step 3 — Classify broad pleural disease state

Use:

```text
objective pleural abnormality
→ PLEURAL_DISEASE_HYPOTHESIS_SUPPORTED

incomplete/ambiguous evidence
→ PLEURAL_DISEASE_HYPOTHESIS_INDETERMINATE

etiology unclear
→ PLEURAL_ETIOLOGY_UNRESOLVED
```

### Step 4 — Assess malignancy concern

Use imaging + clinical + cytology/pathology together.

```text
suspicious pleural morphology
+ compatible clinical context
→ PLEURAL_MALIGNANCY_CONCERN_SUPPORTED

incomplete morphology/context
→ PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE

trusted contradictory evidence
→ PLEURAL_MALIGNANCY_CONCERN_CONFLICTED
```

Negative CT or negative cytology does not universally exclude malignancy.

### Step 5 — Malignant pleural effusion

Only emit:

`CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION`

when pleural-fluid cytology explicitly identifies malignant cells.

Otherwise:

`MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED`

even if clinical/imaging concern is high.

### Step 6 — Mesothelioma

Use:

`MESOTHELIOMA_CONCERN_SUPPORTED`

for a bounded concern state when risk/context/morphology align.

Only explicit tissue pathology confirming mesothelioma may emit:

`PATHOLOGY_CONFIRMED_MESOTHELIOMA`

Do not diagnose mesothelioma from:
- asbestos exposure;
- pleural plaque;
- unilateral effusion;
- pleural thickening;
- suspicious CT;
- generic malignant cytology without explicit mesothelioma diagnosis.

### Step 7 — Secondary pleural malignancy

If tissue pathology explicitly confirms malignant pleural involvement:
- emit `PATHOLOGY_CONFIRMED_PLEURAL_MALIGNANCY`;
- preserve origin only if explicitly supplied.

Do not infer the primary tumor.

### Step 8 — Infection differential

If fever/inflammatory context plus pleural imaging/fluid/microbiology support infection:

`PLEURAL_INFECTION_CONCERN_SUPPORTED`

Otherwise:
`PLEURAL_INFECTION_NOT_ESTABLISHED`

Do not infer empyema or bacterial cause from effusion or CT morphology alone.

### Step 9 — Asbestos-related pleural disease

Only explicit pleural plaque characterization and/or supplied exposure history may support:

`ASBESTOS_RELATED_PLEURAL_DISEASE_CONCERN`

Do not infer actual occupational exposure from generic calcification/thickening.

### Step 10 — Competing etiologies

Preserve independent evidence for:
- pneumonia;
- heart failure;
- pulmonary malignancy;
- TB/chronic infection;
- autoimmune disease;
- other causes.

No forced winner when evidence is incomplete.

### Step 11 — Safety

Severe respiratory failure, hemodynamic instability, severe sepsis, or another acute pleural emergency may propagate to existing safety logic.

No autonomous diagnostic procedure or treatment action.

### Step 12 — Output

Return:
- broad pleural-disease state;
- effusion/thickening/plaque/nodularity evidence;
- malignancy concern;
- MPE confirmation boundary;
- mesothelioma concern/pathology;
- infection concern;
- asbestos context;
- cytology/pathology provenance;
- competing etiologies;
- conflicts/missing data;
- safety;
- uncertainty;
- doctor review.
