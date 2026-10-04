# TB_CHRONIC_MYCOBACTERIAL_POLICY.md

## Integration target

Integrate this module under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/tb_chronic_mycobacterial/
├── TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md
├── TB_CHRONIC_MYCOBACTERIAL_POLICY.md
└── references.md
```

Do not create a new top-level TB or chronic-infection skill.

## Progressive-loading trigger

Load this module when at least one of the following is present:

1. Explicit clinician/radiologist concern for:
   - pulmonary TB;
   - pleural TB;
   - chronic mycobacterial infection;
   - NTM pulmonary disease.
2. Trusted CT/human report describing potentially compatible chronic infection morphology:
   - cavity/cavitation;
   - tree-in-bud;
   - centrilobular nodules;
   - chronic fibrocavitary change;
   - necrotic nodes;
   - pleural abnormalities in TB context.
3. Microbiology:
   - AFB smear;
   - M. tuberculosis-specific molecular test/NAAT;
   - mycobacterial culture;
   - NTM species identification.
4. TB infection/risk context:
   - IGRA/TST;
   - known exposure/contact;
   - immunocompromised context;
   - previous documented TB.
5. Pleural TB context:
   - pleural ADA/IFN-gamma;
   - pleural-fluid/tissue NAAT/culture;
   - pleural granulomatous histology.
6. Pathology suggesting granulomatous/mycobacterial disease.

Do NOT activate solely because one of the following generic image findings is positive:
- `Calcification`
- `Pulmonary fibrosis`
- `Infiltration`
- `Lung Opacity`
- `Pleural effusion`

unless explicit clinical/microbiologic/CT/TB context is also present.

## Reasoning procedure

### Step 1 — Preserve upstream finding semantics

Do not reinterpret:
- Calcification as healed TB;
- Pulmonary fibrosis as prior TB;
- Infiltration as active TB;
- Pleural effusion as tuberculous pleuritis.

### Step 2 — Separate infection from disease

IGRA/TST indicate immune sensitization/infection context.

They do not establish active TB disease.

### Step 3 — Separate AFB detection from species identification

```text
AFB smear positive
+ no M. tuberculosis-specific test
→ AFB_DETECTED_SPECIES_UNRESOLVED
```

Do not force TB over NTM.

### Step 4 — Check TB-specific microbiology

If a validated M. tuberculosis-complex-specific molecular assay or culture explicitly detects M. tuberculosis complex:

`MICROBIOLOGICALLY_CONFIRMED_TB`

Preserve specimen/site/date and resistance markers if explicitly supplied.

### Step 5 — Assess pulmonary TB concern

Combine:
- clinical syndrome and duration;
- imaging;
- epidemiology;
- immune status;
- microbiology/pathology.

Use bounded concern states when confirmation is absent.

### Step 6 — Assess pleural TB

Use:
- pleural context;
- epidemiology;
- ADA/IFN-gamma;
- tissue histology;
- pleural-fluid/tissue molecular/culture results.

ADA alone is supportive, not definitive.

### Step 7 — Assess pathology

Granulomatous/necrotizing inflammation may support TB concern but is not TB-specific.

If organism not identified:
- `PATHOLOGY_SUPPORTED_TB` where appropriate;
- preserve competing NTM/fungal/inflammatory etiologies.

### Step 8 — Assess NTM differential

A single positive sputum NTM culture does not establish NTM pulmonary disease.

Use the supplied clinical, radiographic, and microbiologic criteria. Require the standard repeated-sputum or alternate accepted microbiologic pathway before `NTM_PULMONARY_DISEASE_CONCERN_SUPPORTED`.

### Step 9 — Resolve site/activity conservatively

If TB is confirmed but site is unclear:
`TB_SITE_UNRESOLVED`.

If prior TB exists but current activity is unclear:
`TB_ACTIVITY_UNRESOLVED`.

### Step 10 — Preserve competing hypotheses

Keep independent:
- Pneumonia;
- Pulmonary Malignancy;
- ILD/Fibrotic disease;
- Pleural Disease;
- NTM;
- other chronic infection.

No forced winner without adequate evidence.

### Step 11 — Safety

Potentially transmissible/severe TB concern may propagate to existing high-priority review policy.

Do not autonomously issue:
- sputum/NAAT/culture orders;
- bronchoscopy/biopsy orders;
- respiratory-isolation instructions;
- anti-TB treatment;
- contact tracing;
- disposition.

### Step 12 — Output

Return:
- TB concern/confirmation state;
- disease site/activity;
- CXR/CT evidence;
- symptoms/duration;
- epidemiology/immune context;
- IGRA/TST;
- AFB smear;
- molecular/culture evidence;
- pleural TB evidence;
- pathology;
- NTM differential;
- conflicts/missing data;
- competing hypotheses;
- safety;
- uncertainty;
- doctor review.
