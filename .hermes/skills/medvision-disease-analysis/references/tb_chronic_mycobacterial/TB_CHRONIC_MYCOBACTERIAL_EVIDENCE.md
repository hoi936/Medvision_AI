# TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md

## 0. Scope

Disease Analysis v2 module for:

**Pulmonary Tuberculosis / Pleural Tuberculosis / Chronic Mycobacterial Thoracic Infection Concern**

This is not:
- a new VinBigData finding skill;
- a new top-level Hermes skill;
- a treatment, isolation, contact-tracing, or drug-resistance management engine.

Target flow remains:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ tb_chronic_mycobacterial reference module
```

Core boundaries:

```text
Calcification != active TB
Pulmonary fibrosis != prior or active TB
Pleural effusion != tuberculous pleuritis
Upper-lobe opacity != TB
Cavity != TB
Positive IGRA/TST != active TB
Exposure history != active TB
AFB smear positive != M. tuberculosis confirmed
Negative smear/NAAT != universal TB exclusion
Granulomatous inflammation != TB etiology automatically
```

---

## 1. Disease-analysis states

MedVision internal states:

```text
PULMONARY_TB_CONCERN_SUPPORTED
PULMONARY_TB_CONCERN_INDETERMINATE
PULMONARY_TB_NOT_ESTABLISHED

PLEURAL_TB_CONCERN_SUPPORTED
PLEURAL_TB_CONCERN_INDETERMINATE
PLEURAL_TB_NOT_ESTABLISHED

MICROBIOLOGICALLY_CONFIRMED_TB
PATHOLOGY_SUPPORTED_TB
TB_ACTIVITY_UNRESOLVED
TB_SITE_UNRESOLVED

AFB_DETECTED_SPECIES_UNRESOLVED

NTM_PULMONARY_DISEASE_CONCERN_SUPPORTED
NTM_PULMONARY_DISEASE_NOT_ESTABLISHED

CHRONIC_THORACIC_INFECTION_CONCERN_SUPPORTED
CHRONIC_INFECTION_ETIOLOGY_UNRESOLVED
```

These are bounded reasoning states. `MICROBIOLOGICALLY_CONFIRMED_TB` is allowed only when an explicit M. tuberculosis-complex-specific molecular or culture result is supplied.

---

## 2. Upstream image findings

Relevant VinBigData findings may include:
- `Infiltration`
- `Lung Opacity`
- `Consolidation`
- `Nodule/Mass`
- `Pulmonary fibrosis`
- `Calcification`
- `Pleural effusion`
- `Pleural thickening`
- `Other lesion`

Existing finding skills remain authoritative.

No VinBigData class is itself a TB diagnosis.

---

## 3. Chest radiography and CT

CXR abnormalities can suggest TB but cannot definitively diagnose TB.

Trusted CT/human reports may describe:
- cavity/cavitation;
- tree-in-bud nodularity;
- centrilobular nodules;
- upper-lobe predominant abnormalities;
- necrotic nodes;
- chronic fibrocavitary change;
- pleural disease.

These descriptors may raise concern but remain nonspecific.

Hermes MUST NOT convert:
- upper-lobe opacity;
- cavity;
- fibrosis;
- calcified node;
- tree-in-bud;
- pleural effusion;

directly into TB.

---

## 4. No Finding / normal CXR

A CXR `No finding` state does not universally exclude TB disease.

This is especially important when:
- microbiology is positive;
- the patient is immunocompromised;
- extrapulmonary disease is suspected;
- symptoms/risk context remain concerning.

Preserve modality and disease-site context.

Do not create a No Finding contradiction from symptoms alone.

---

## 5. TB infection tests: IGRA / TST

WHO states that TST/IGRA detect immune sensitization and cannot by themselves distinguish TB infection from TB disease.

Therefore:

```text
positive IGRA/TST
!= active TB
```

and:

```text
negative IGRA/TST
!= active TB universally excluded
```

Use infection-test results only as contextual evidence.

Do not infer active pulmonary or pleural TB from infection testing alone.

---

## 6. AFB smear

AFB smear is not species-specific.

M. tuberculosis complex is one possible acid-fast organism; NTM can also produce AFB-positive specimens.

Therefore:

```text
AFB smear positive
→ AFB_DETECTED_SPECIES_UNRESOLVED
```

unless a separate M. tuberculosis-specific result is provided.

A negative smear does not exclude TB.

Do not convert smear grade into probability of TB disease.

---

## 7. Molecular tests / NAAT

A WHO-recommended molecular test explicitly detecting M. tuberculosis complex in an appropriate specimen can support:

`MICROBIOLOGICALLY_CONFIRMED_TB`

Preserve:
- assay name if supplied;
- specimen;
- site;
- date;
- resistance markers if explicitly reported.

Do not invent resistance if not tested.

A negative NAAT does not universally exclude TB, especially where sensitivity is limited by specimen/site/disease burden.

For extrapulmonary specimens, interpret negative results in clinical context.

---

## 8. Culture

Culture explicitly identifying M. tuberculosis complex is strong microbiologic confirmation.

Use:

`MICROBIOLOGICALLY_CONFIRMED_TB`

when the source explicitly identifies M. tuberculosis complex.

Culture that reports only `mycobacteria` or AFB without species identification is not enough to label TB.

If an NTM species is identified, do not relabel it as M. tuberculosis.

---

## 9. Pathology / granulomatous inflammation

Granulomatous inflammation can occur in TB but is not TB-specific.

Possible alternatives include:
- NTM;
- fungal infection;
- sarcoidosis;
- other inflammatory conditions.

Therefore:

```text
granuloma
!= TB confirmed
```

Caseating/necrotizing granulomatous inflammation may increase TB concern in compatible context, but absent M. tuberculosis-specific evidence it should remain:

`PATHOLOGY_SUPPORTED_TB`

or:

`CHRONIC_INFECTION_ETIOLOGY_UNRESOLVED`

depending on source wording and competing diagnoses.

If pathology explicitly reports M. tuberculosis identified by validated molecular/culture testing, microbiologic confirmation may also be represented.

---

## 10. Pulmonary TB concern

`PULMONARY_TB_CONCERN_SUPPORTED` may be emitted when several supplied domains align, for example:
- chronic compatible respiratory/systemic syndrome;
- compatible CT/human imaging;
- epidemiologic risk or exposure;
- microbiology/pathology supportive evidence.

It is not a substitute for microbiologic confirmation.

If evidence is incomplete:

`PULMONARY_TB_CONCERN_INDETERMINATE`

If current evidence does not establish TB:

`PULMONARY_TB_NOT_ESTABLISHED`

---

## 11. Pleural TB

Pleural effusion alone does not establish tuberculous pleuritis.

Potentially relevant evidence:
- compatible epidemiology;
- exudative pleural context if explicitly supplied;
- elevated pleural ADA or IFN-gamma;
- pleural-tissue histology;
- pleural-fluid/tissue NAAT;
- pleural-fluid/tissue culture;
- clinician/MDD diagnosis.

### ADA

Pleural ADA is supportive and prevalence/context dependent.

Therefore:

```text
elevated ADA alone
!= pleural TB confirmed
```

Do not encode a universal ADA cutoff in this v1 module.

### Confirmed pleural TB

If M. tuberculosis complex is explicitly detected from pleural fluid/tissue by validated molecular test or culture:
- `MICROBIOLOGICALLY_CONFIRMED_TB`;
- pleural site may be marked supported/confirmed according to source.

If pathology is compatible but microbiology absent:
- `PATHOLOGY_SUPPORTED_TB`;
- `PLEURAL_TB_CONCERN_SUPPORTED` may be used if broader evidence aligns.

---

## 12. Calcification

Generic thoracic calcification does not establish:
- active TB;
- prior treated TB;
- healed TB;
- granulomatous disease.

Even calcified lymph nodes are not evidence of active TB by themselves.

Use localization and explicit historical/source evidence only.

If a clinician documents prior healed TB, preserve that diagnosis and provenance rather than deriving it from calcification.

---

## 13. Fibrosis / scarring

Pulmonary fibrosis/scarring does not prove prior TB and does not establish active TB.

If prior TB is explicitly documented:
- preserve history;
- distinguish residual structural change from active disease.

Use:

`TB_ACTIVITY_UNRESOLVED`

when historical TB and current imaging abnormalities exist but present activity is not established.

Do not interpret chronic scar as recurrence without current evidence.

---

## 14. Exposure and epidemiology

Known household/contact exposure, prior high-incidence residence, occupational risk, incarceration/congregate exposure, immunosuppression, or other supplied epidemiology can modify concern.

But:

```text
TB exposure != active TB
```

Do not convert epidemiologic risk into disease confirmation or a numeric probability.

---

## 15. Immunocompromised hosts

In immunocompromised patients:
- chest imaging may be atypical or subtle;
- infection tests may be less reliable;
- extrapulmonary/disseminated disease may be more relevant.

Therefore:
- preserve uncertainty;
- do not use normal CXR or negative IGRA/TST as universal exclusion;
- preserve site-specific microbiology.

No separate treatment logic is introduced.

---

## 16. Chronic symptoms

Potential supplied symptoms include:
- cough;
- sputum;
- hemoptysis;
- fever;
- night sweats;
- weight loss;
- fatigue;
- pleuritic pain.

Symptoms are nonspecific.

No symptom cluster alone confirms TB.

Do not infer chronicity if duration is missing.

---

## 17. NTM differential

AFB-positive or chronic cavitary/nodular-bronchiectatic disease may represent NTM rather than TB.

The ATS/ERS/ESCMID/IDSA framework requires clinical + radiographic + microbiologic criteria.

A single positive sputum NTM culture does not automatically establish NTM pulmonary disease.

The standard sputum-culture criterion generally requires:
- the same NTM species in at least two separate expectorated sputum cultures;

or another accepted microbiologic pathway such as:
- one positive bronchial wash/lavage;
- compatible biopsy plus microbiologic evidence.

Therefore:

```text
single NTM sputum culture
→ NTM_PULMONARY_DISEASE_NOT_ESTABLISHED
```

When full supplied criteria are met:

`NTM_PULMONARY_DISEASE_CONCERN_SUPPORTED`

Do not infer treatment need.

---

## 18. TB vs NTM

If AFB smear is positive but species-specific testing is absent:

`AFB_DETECTED_SPECIES_UNRESOLVED`

Do not force TB over NTM.

If M. tuberculosis-specific NAAT/culture is positive:
- TB confirmation may be represented.

If NTM species is repeatedly isolated with full disease criteria:
- preserve NTM disease concern independently.

---

## 19. TB vs pneumonia

Acute pneumonia and pulmonary TB may overlap in:
- cough;
- fever;
- consolidation/opacity.

Preserve both when supported.

Do not convert acute consolidation into TB without additional evidence.

Do not erase microbiologically confirmed TB because pneumonia evidence also exists.

---

## 20. TB vs pulmonary malignancy

Cavitary or mass-like lesions may have infectious or malignant causes.

If pulmonary malignancy concern coexists:
- preserve both hypotheses;
- do not force a winner;
- use pathology/microbiology/temporal evidence.

A lesion can also have more than one process.

---

## 21. TB vs ILD/fibrosis

Fibrotic changes may be postinfectious, unrelated ILD, or another chronic process.

Do not:
- label fibrosis as old TB;
- count TB-related acute abnormalities as ILD progression without evidence;
- infer IPF exclusion from TB history alone.

Preserve longitudinal and etiologic uncertainty.

---

## 22. TB vs pleural malignancy/infection

Pleural TB, bacterial pleural infection, and pleural malignancy can overlap clinically.

Preserve:
- ADA;
- microbiology;
- cytology/pathology;
- CT/US morphology;
- epidemiology.

Do not let one biomarker dominate the entire differential.

---

## 23. Site and activity

TB can be:
- pulmonary;
- pleural;
- nodal;
- other extrapulmonary;
- multi-site.

Only assign site when source evidence supports it.

If M. tuberculosis is confirmed but disease site is not clear:

`TB_SITE_UNRESOLVED`

If prior TB history exists but active disease status is unclear:

`TB_ACTIVITY_UNRESOLVED`

---

## 24. AI score semantics

Never convert image-model scores such as:

```text
Infiltration score = 0.93
Calcification score = 0.89
```

into:
- TB probability;
- active-disease probability;
- infectiousness;
- prior-TB probability.

Scores remain image-model outputs only.

---

## 25. Safety boundary

Potentially transmissible or severe TB concern may justify:

`HIGH_PRIORITY_CLINICAL_REVIEW`

under existing safety policy when supported by supplied data.

Do not autonomously:
- order sputum/NAAT/culture;
- order bronchoscopy;
- order pleural biopsy;
- initiate respiratory isolation;
- start anti-TB treatment;
- recommend a regimen;
- perform contact tracing;
- make admission/disposition decisions.

Those remain clinician/public-health decisions outside this module.

---

## 26. Recommended output

```yaml
disease_hypothesis:
  name: tuberculosis
  status: not_established|indeterminate|concern_supported|microbiologically_confirmed

site:
  pulmonary: unknown|possible|supported
  pleural: unknown|possible|supported
  other_sites: []
  unresolved: false

activity:
  status: unknown|inactive_history|active_concern|microbiologically_supported

imaging_support:
  cxr_findings: []
  ct_findings: []
  cavitation: unknown
  tree_in_bud: unknown
  fibrosis_or_scarring: unknown
  calcification: unknown

clinical_support:
  symptoms: []
  duration: unknown
  epidemiologic_risk: []
  immunocompromised_context: []

infection_tests:
  igra: unknown
  tst: unknown
  interpretation: unknown

microbiology:
  afb_smear: unknown
  molecular_test: unknown
  culture: unknown
  species: unknown
  specimen_sites: []
  resistance_markers: []

pleural_tb:
  concern: not_established|indeterminate|supported
  ada: unknown
  interferon_gamma: unknown
  tissue_histology: unknown

pathology:
  granulomatous_inflammation: unknown
  necrosis: unknown
  organism_identified: unknown
  interpretation: unknown

ntm:
  species: unknown
  culture_count: unknown
  disease_criteria_met: unknown
  concern: not_established|possible|supported

competing_hypotheses: []
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
```

---

## 27. Hard constraints

Hermes MUST NOT:

1. Convert Calcification into active or prior TB.
2. Convert Pulmonary fibrosis into prior TB or active TB.
3. Convert Pleural effusion into pleural TB.
4. Convert upper-lobe opacity/cavity/tree-in-bud into TB automatically.
5. Convert positive IGRA/TST into active TB.
6. Exclude active TB from negative IGRA/TST.
7. Convert AFB smear positive into M. tuberculosis confirmation.
8. Exclude TB from a negative smear alone.
9. Exclude TB universally from a negative NAAT/culture, especially extrapulmonary disease.
10. Encode a universal pleural-ADA cutoff.
11. Confirm pleural TB from ADA alone.
12. Convert granulomatous inflammation directly into TB.
13. Infer active recurrence from old scars/fibrosis.
14. Treat a single positive NTM sputum culture as NTM pulmonary disease.
15. Force TB over NTM when AFB species is unresolved.
16. Force TB over pneumonia/malignancy/other chronic infection without adequate evidence.
17. Treat No Finding CXR as universal TB exclusion.
18. Infer site or activity when source evidence is missing.
19. Convert AI score into TB probability.
20. Issue autonomous testing, isolation, treatment, contact-tracing, procedure, or disposition actions.
21. Omit doctor review.
