# ILD_FIBROTIC_POLICY.md

## Integration target

Integrate under existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/ild_fibrotic/
├── ILD_FIBROTIC_EVIDENCE.md
├── ILD_FIBROTIC_POLICY.md
└── references.md
```

Do not create `medvision-ild-disease` or another top-level skill.

## Progressive-loading trigger

Load this module when one or more are present:

1. Canonical AI/imaging:
   - `ILD`
   - `Pulmonary fibrosis`
2. Trusted HRCT/report explicitly describes:
   - fibrotic ILD;
   - UIP/probable UIP;
   - indeterminate-for-UIP;
   - alternative-diagnosis ILD pattern;
   - honeycombing;
   - traction bronchiectasis/bronchiolectasis;
   - reticulation/fibrotic progression.
3. Known/suspected ILD from pulmonology/MDD.
4. Relevant etiologic context:
   - established CTD;
   - meaningful exposure history;
   - drug/toxin context;
   - explicit HP/IPF concern.
5. Longitudinal PFT/HRCT data supplied for progression assessment.

Do not activate solely because:
- generic Lung Opacity is positive;
- generic Infiltration is positive;
- generic Calcification is positive;
- unrelated chest findings are positive.

## Reasoning procedure

### Step 1 — Preserve upstream evidence

Keep canonical AI findings and their finding-skill semantics unchanged.

Do not reinterpret CXR as HRCT.

### Step 2 — Establish modality

Classify available evidence as:
- CXR;
- HRCT/CT;
- pathology;
- MDD/clinician diagnosis;
- PFT;
- exposure/CTD context.

Missing stays unknown.

### Step 3 — Determine ILD/fibrotic-ILD hypothesis

Use bounded states:

```text
objective interstitial evidence + compatible context
→ ILD_HYPOTHESIS_SUPPORTED

objective fibrosis in an ILD context
→ FIBROTIC_ILD_HYPOTHESIS_SUPPORTED

insufficient/incomplete data
→ ILD_HYPOTHESIS_INDETERMINATE

trusted disagreement
→ ILD_HYPOTHESIS_CONFLICTED
```

### Step 4 — HRCT category

Only assign UIP/probable UIP/indeterminate/alternative category from trusted HRCT/source evidence.

If HRCT absent or insufficient:

`HRCT_PATTERN_NOT_ASSESSABLE`

### Step 5 — IPF concern

Require:
- fibrotic ILD;
- compatible HRCT/clinical context;
- meaningful assessment of alternative known causes.

If exclusions are incomplete:

`IPF_NOT_ESTABLISHED`
and `ILD_ETIOLOGY_UNRESOLVED`.

Do not turn UIP into IPF automatically.

### Step 6 — CTD-ILD concern

Use established CTD plus objective ILD evidence.

Positive ANA or nonspecific rheumatologic symptoms alone are insufficient.

### Step 7 — Fibrotic HP concern

Require integration across exposure, HRCT, BAL/pathology and/or trusted MDD evidence.

Exposure or positive serum IgG alone is insufficient.

### Step 8 — PPF assessment

Only assess PPF when:
- ILD is other than IPF;
- radiological fibrosis exists;
- longitudinal data fall within the required past-year window;
- alternative explanations have been considered.

Domains:

```text
SYMPTOMS
PHYSIOLOGY
RADIOLOGY
```

At least two of the three domains are required.

FVC and DLCO changes are both inside the single PHYSIOLOGY domain.

### Step 9 — Cross-disease separation

Acute pneumonia/HF evidence must not be silently converted into ILD progression.

Preserve competing hypotheses and timing.

### Step 10 — Safety

Severe hypoxemia/respiratory failure may propagate to existing safety policy.

No autonomous therapy, imaging, PFT, BAL, biopsy, transplant, or disposition actions.

### Step 11 — Output

Return:
- ILD/fibrotic-ILD state;
- modality evidence;
- HRCT pattern if explicitly supported;
- etiology status;
- IPF/CTD-ILD/HP bounded concern;
- PPF assessability and domains;
- longitudinal evidence;
- competing hypotheses;
- conflicts/missing data;
- safety;
- uncertainty;
- doctor review.
