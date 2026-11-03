# PNEUMONIA_POLICY.md

## Integration target

Integrate under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/pneumonia/
├── PNEUMONIA_EVIDENCE.md
├── PNEUMONIA_POLICY.md
└── references.md
```

Do NOT create a new top-level `medvision-pneumonia` skill.

## Progressive-loading trigger

Load this module when at least one condition is true:

1. AI/human imaging contains:
   - Consolidation
   - Lung Opacity
   - Infiltration
2. A clinician/radiologist explicitly raises pneumonia.
3. An acute respiratory infectious syndrome is supplied even if CXR is negative/indeterminate.

Do not load solely for unrelated chest findings.

## Reasoning procedure

### 1. Establish scope
Capture:
- adult status;
- immunocompromised status;
- acquisition context;
- timing.

Missing stays unknown.

### 2. Gather imaging support
Preserve upstream findings and overlap metadata.

Compatible:
- Consolidation
- Lung Opacity
- Infiltration

Associated:
- Pleural effusion

No compatible finding does not automatically exclude pneumonia.

### 3. Gather clinical support
Use only supplied symptoms/signs:
- cough;
- fever;
- sputum;
- pleuritic pain;
- dyspnea;
- respiratory findings;
- hypoxemia.

### 4. Gather labs
Use actual values only. Inflammatory markers are supportive/nonspecific. Low procalcitonin does not independently erase compatible evidence.

### 5. Assign bounded hypothesis state

```text
compatible imaging + compatible acute clinical syndrome
→ PNEUMONIA_HYPOTHESIS_SUPPORTED

compatible imaging + insufficient clinical information
→ IMAGING_FINDING_WITHOUT_SUFFICIENT_CLINICAL_SUPPORT

compatible acute syndrome + no radiographic support
→ PNEUMONIA_HYPOTHESIS_POSSIBLE_BUT_NOT_RADIOGRAPHICALLY_SUPPORTED

trusted conflicting evidence
→ PNEUMONIA_HYPOTHESIS_CONFLICTED

otherwise
→ PNEUMONIA_HYPOTHESIS_NOT_ESTABLISHED
```

These states are not final physician diagnoses.

### 6. Assign CAP subtype
Only set `community_acquired: true` when outside-hospital acquisition is supported.

Hospital acquisition -> false.
Unknown -> unknown.

### 7. Etiology
Do not infer bacterial/viral/aspiration/TB/fungal/pathogen etiology from image morphology alone.

### 8. Severe CAP
When in scope and data are present:

```text
1 major OR >=3 minor
→ SEVERE_CAP_CRITERIA_MET
```

Do not infer missing criteria.

### 9. Safety
Propagate supported respiratory failure, shock, severe hypoxemia, or severe-CAP criteria to the existing safety logic.

No autonomous imaging, treatment, procedure, or disposition.

### 10. Output
Return:
- hypothesis state;
- CAP subtype;
- scope limitations;
- supporting/contradicting evidence;
- missing data;
- etiology status;
- severe-CAP criteria;
- safety;
- uncertainty;
- doctor review;
- citations.
