# HEART_FAILURE_POLICY.md

## Integration target

Integrate this module under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/heart_failure/
├── HEART_FAILURE_EVIDENCE.md
├── HEART_FAILURE_POLICY.md
└── references.md
```

Do not create `medvision-heart-failure`.

## Progressive-loading trigger

Load this module when at least one of the following is present:

1. Relevant AI/imaging findings:
   - Cardiomegaly
   - Pleural effusion
   - Lung Opacity
   - Infiltration
   - Consolidation
2. Trusted report explicitly describes:
   - pulmonary vascular congestion
   - pulmonary edema
   - interstitial edema
   - systemic congestion
3. Clinical context raises HF:
   - dyspnea/orthopnea/PND
   - edema/JVP/S3
   - known HF/cardiomyopathy
4. Supporting cardiac evidence:
   - elevated BNP/NT-proBNP
   - abnormal echocardiography
   - elevated filling pressures

Do not activate only because an unrelated finding is positive.

## Reasoning procedure

### Step 1 — Gather clinical syndrome

Use only supplied symptoms/signs. Missing stays unknown.

### Step 2 — Gather radiographic evidence

Preserve upstream CXR finding semantics. Do not relabel generic opacity/consolidation as edema.

### Step 3 — Gather objective cardiac evidence

Prioritize:
- echocardiographic structure/function;
- filling pressures/hemodynamics;
- trusted specific congestion imaging;
- natriuretic-peptide context.

Preserve modality and timing.

### Step 4 — Interpret natriuretic peptides contextually

Elevated NP supports but does not confirm HF.

Known modifiers include age, obesity, kidney dysfunction, AF, alternative cardiac disease, pulmonary disease, and critical illness.

Low/normal NP does not universally exclude HF.

### Step 5 — Assign bounded hypothesis state

```text
compatible HF syndrome
+ objective cardiac/congestion corroboration
→ HEART_FAILURE_HYPOTHESIS_SUPPORTED

explicit congestion pattern
+ compatible cardiac/clinical support
→ CARDIOGENIC_CONGESTION_HYPOTHESIS_SUPPORTED

CXR findings only / clinical support missing
→ IMAGING_FINDINGS_WITHOUT_SUFFICIENT_HF_CLINICAL_SUPPORT

compatible HF syndrome + objective cardiac support
but no CXR congestion
→ HEART_FAILURE_POSSIBLE_WITHOUT_RADIOGRAPHIC_CONGESTION
   or HEART_FAILURE_HYPOTHESIS_SUPPORTED when total evidence is sufficient

trusted unresolved contradiction
→ HEART_FAILURE_HYPOTHESIS_CONFLICTED

insufficient evidence
→ HEART_FAILURE_HYPOTHESIS_NOT_ESTABLISHED
```

### Step 6 — Phenotype

Only assign HF phenotype from adequate cardiac imaging plus supported HF syndrome.

If insufficient:
`HF_PHENOTYPE_UNRESOLVED`.

Use current 2026 terminology for new inference while preserving historical clinician labels with provenance.

### Step 7 — Competing diseases

If pneumonia or another disease is also plausible:
- preserve both;
- do not force a winner;
- identify supporting/contradictory evidence for each;
- avoid double counting shared evidence.

### Step 8 — Safety

Propagate severe respiratory failure, shock, hypoperfusion, or severe congestion concern to the existing safety layer.

No autonomous treatment, imaging order, procedure, or disposition.

### Step 9 — Output

Return:
- HF hypothesis;
- congestion hypothesis;
- clinical evidence;
- imaging evidence;
- biomarker interpretation;
- cardiac structure/function;
- phenotype if justified;
- competing hypotheses;
- conflicts/missing data;
- safety;
- uncertainty;
- doctor review.
