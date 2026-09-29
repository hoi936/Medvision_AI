# ILD_FIBROTIC_EVIDENCE.md

## Scope

Disease Analysis v2 module for **Interstitial Lung Disease / Fibrotic ILD / IPF concern / Progressive Pulmonary Fibrosis (PPF)**.

It is not a new VinBigData finding skill, not a new top-level Hermes skill, and not a treatment engine.

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ ild_fibrotic reference module
```

Core boundaries:

```text
ILD finding != ILD diagnosis
Pulmonary fibrosis finding != IPF
Fibrosis != UIP
UIP pattern != IPF automatically
CXR != HRCT pattern classification
Single study != PPF
```

## Disease-analysis states

```text
ILD_HYPOTHESIS_SUPPORTED
FIBROTIC_ILD_HYPOTHESIS_SUPPORTED
ILD_HYPOTHESIS_INDETERMINATE
ILD_HYPOTHESIS_CONFLICTED
ILD_HYPOTHESIS_NOT_ESTABLISHED

HRCT_PATTERN_UIP
HRCT_PATTERN_PROBABLE_UIP
HRCT_PATTERN_INDETERMINATE_FOR_UIP
HRCT_PATTERN_ALTERNATIVE_DIAGNOSIS
HRCT_PATTERN_NOT_ASSESSABLE

IPF_CONCERN_SUPPORTED
IPF_NOT_ESTABLISHED
ILD_ETIOLOGY_UNRESOLVED

FIBROTIC_HP_CONCERN_SUPPORTED
CTD_ILD_CONCERN_SUPPORTED

PPF_CRITERIA_MET
PPF_CRITERIA_NOT_MET
PPF_NOT_ASSESSABLE
```

These are MedVision system-policy states, not final multidisciplinary diagnoses.

## Upstream image findings

Relevant finding-level evidence may include:
- `ILD`
- `Pulmonary fibrosis`
- `Lung Opacity`
- `Infiltration`
- other supplied findings

Existing finding skills remain authoritative.

`ILD POSITIVE` means radiographic evidence compatible with an interstitial pattern. It does not establish IPF, UIP, NSIP, CTD-ILD, HP, sarcoidosis, pneumoconiosis, or drug-induced ILD.

`Pulmonary fibrosis POSITIVE` means radiographic evidence compatible with chronic fibrotic/scarring change. It does not establish IPF, UIP, PPF, or etiology.

## CXR versus HRCT

Chest radiography is insufficient for detailed HRCT pattern classification.

Hermes MUST NOT infer from CXR alone:
- honeycombing;
- traction bronchiectasis/bronchiolectasis;
- UIP/probable UIP;
- NSIP pattern;
- three-density pattern;
- specific fibrotic-HP pattern.

If trusted HRCT explicitly supplies these features, preserve them as HRCT evidence.

## HRCT categories

The ATS/ERS/JRS/ALAT framework uses four categories:

```text
UIP
probable UIP
indeterminate for UIP
alternative diagnosis
```

Map only when explicitly supported:

```text
explicit HRCT UIP
→ HRCT_PATTERN_UIP

explicit probable UIP
→ HRCT_PATTERN_PROBABLE_UIP

explicit indeterminate for UIP
→ HRCT_PATTERN_INDETERMINATE_FOR_UIP

explicit alternative-diagnosis pattern
→ HRCT_PATTERN_ALTERNATIVE_DIAGNOSIS
```

If HRCT is absent or insufficient:

`HRCT_PATTERN_NOT_ASSESSABLE`

Do not reconstruct an HRCT category from a CXR or incomplete descriptors.

## UIP pattern versus IPF

UIP is a radiologic/histopathologic pattern and is not unique to IPF.

```text
UIP pattern != IPF automatically
```

IPF requires compatible clinical context and exclusion of other known ILD causes such as:
- environmental/occupational exposure;
- connective-tissue disease;
- drug toxicity;
- other identifiable etiologies.

If UIP/probable UIP is present but alternative causes are incompletely assessed:

`IPF_NOT_ESTABLISHED`
and/or
`ILD_ETIOLOGY_UNRESOLVED`.

A trusted multidisciplinary diagnosis of IPF may be preserved with provenance.

## IPF concern

`IPF_CONCERN_SUPPORTED` may be used only when multiple domains align:
- fibrotic ILD is objectively established;
- HRCT is appropriately compatible;
- major alternative causes have been meaningfully assessed;
- clinical context is compatible;
- trusted clinician/MDD evidence supports IPF concern.

Do not infer IPF from fibrosis alone, older age alone, smoking alone, or a positive `ILD` class.

## CTD-ILD

Potentially relevant supplied context includes established systemic sclerosis, rheumatoid arthritis, inflammatory myopathy, Sjögren disease, mixed connective-tissue disease, systemic lupus erythematosus, or another explicitly diagnosed CTD.

```text
established CTD
+ objective ILD evidence
→ CTD_ILD_CONCERN_SUPPORTED
```

when the relationship is clinically supported.

Do not infer CTD-ILD from positive ANA alone, nonspecific arthralgia alone, or ILD finding alone.

If autoimmune evidence is incomplete:

`ILD_ETIOLOGY_UNRESOLVED`.

## Hypersensitivity pneumonitis / fibrotic HP

HP diagnosis integrates:
1. exposure identification;
2. HRCT pattern;
3. BAL lymphocytosis and/or histopathology.

No single feature is sufficient in isolation.

A plausible exposure raises concern but does not confirm HP. Positive serum IgG supports prior exposure/sensitization, not causality. Exposure may also be unidentified in fibrotic HP.

`FIBROTIC_HP_CONCERN_SUPPORTED` may be used only when multiple supplied domains align.

Do not infer HP from exposure alone, serum IgG alone, fibrosis alone, or BAL lymphocytosis alone.

## Progressive Pulmonary Fibrosis (PPF)

The 2022 PPF definition applies to:
- ILD other than IPF;
- radiological pulmonary fibrosis;
- progression without an alternative explanation.

At least **two of three** domains must occur within the past year:

1. worsening respiratory symptoms;
2. physiological progression;
3. radiological progression.

### Physiological domain

Either:
- absolute FVC decline >=5 percentage points predicted within 1 year; or
- absolute Hb-corrected DLCO decline >=10 percentage points predicted within 1 year.

Use comparable actual values and dates. Do not substitute relative decline.

### Radiological domain

At least one explicitly documented comparable change:
- increased traction bronchiectasis/bronchiolectasis;
- new GGO with traction bronchiectasis;
- new fine reticulation;
- increased/coarser reticulation;
- new/increased honeycombing;
- increased lobar volume loss.

### Symptom domain

Count only actual longitudinal worsening with no better alternative explanation.

### PPF outputs

If prerequisites and >=2 domains are met:

`PPF_CRITERIA_MET`

If longitudinal data are adequate but fewer than 2 domains are met:

`PPF_CRITERIA_NOT_MET`

If timing, comparability, prerequisites, or data are insufficient:

`PPF_NOT_ASSESSABLE`

## PPF hard boundaries

Do NOT:
- apply PPF criteria to IPF;
- infer PPF from one CT;
- infer PPF from fibrosis severity alone;
- count FVC and DLCO as two separate domains;
- infer radiological progression without comparable prior imaging;
- treat missing data as stable;
- ignore alternative explanations.

Example:

```text
FVC decline >=5 points
+ DLCO decline >=10 points
```

is still one **physiological** domain.

## Longitudinal evidence

Progression requires actual longitudinal evidence.

Preserve study/PFT dates, modality, same-lesion/process comparability, and source interpretation.

Missing prior data means:

```text
progression_status: unknown
```

not stable.

## ILD + Pulmonary fibrosis overlap

If both findings plausibly describe the same process:
- preserve both;
- apply overlap/de-duplication;
- do not count two independent disease confirmations.

They may jointly support `FIBROTIC_ILD_HYPOTHESIS_SUPPORTED` when broader evidence is compatible.

## Fibrosis + Calcification

Do not infer a specific cause from `Pulmonary fibrosis + Calcification`.

Do not invent pulmonary ossification, pneumoconiosis, asbestos-related disease, or healed granulomatous disease without localization/morphology evidence.

## No Finding CXR + HRCT ILD

CXR `No finding` does not exclude HRCT-detected ILD.

Preserve both modality-specific results. Disease reasoning may proceed from HRCT without rewriting the earlier CXR output.

## Pneumonia versus ILD

If acute infection evidence and ILD evidence coexist:
- preserve both hypotheses;
- use timing and morphology;
- do not force a winner;
- do not count an acute opacity as fibrotic progression without evidence.

## Heart failure versus ILD

If congestion/HF evidence coexists:
- preserve both;
- do not label edema as fibrosis;
- do not count acute congestion as PPF radiological progression.

## Histopathology / MDD

If pathology or ILD multidisciplinary discussion supplies UIP, NSIP, HP, CTD-ILD, IPF, or unclassifiable ILD, preserve the exact source diagnosis/pattern with date.

```text
histologic UIP != IPF automatically
```

## Unclassifiable ILD

When data remain insufficient or conflicting, use bounded uncertainty:

- `ILD_HYPOTHESIS_INDETERMINATE`
- `ILD_ETIOLOGY_UNRESOLVED`
- `EVIDENCE_CONFLICT` where applicable

Do not manufacture a subtype.

## AI score semantics

Never convert image-model scores into disease or progression probabilities.

## Safety

Independent severe hypoxemia, acute respiratory failure, or rapid clinical deterioration may propagate to `HIGH_PRIORITY_CLINICAL_REVIEW`.

Do not autonomously prescribe antifibrotics, steroids/immunosuppression, oxygen, or order HRCT/PFT/BAL/biopsy/transplant evaluation.

## Recommended output

```yaml
disease_hypothesis:
  name: interstitial_lung_disease
  status: not_established|indeterminate|supported|conflicted

fibrotic_ild:
  status: unknown|absent|possible|supported

hrct_pattern:
  status: not_assessable|uip|probable_uip|indeterminate_for_uip|alternative_diagnosis
  source: null

etiology:
  status: unresolved|supported
  candidate: null
  evidence: []

ipf:
  concern: not_established|possible|supported
  alternative_causes_assessed: []
  missing_exclusions: []

ctd_ild:
  concern: not_established|possible|supported
  ctd_source: null

hypersensitivity_pneumonitis:
  concern: not_established|possible|supported
  exposure_evidence: []
  hrct_evidence: []
  bal_pathology_evidence: []

progression:
  ppf_assessable: false
  time_window_valid: false
  symptoms_domain: unknown|absent|present
  physiology_domain: unknown|absent|present
  radiology_domain: unknown|absent|present
  ppf_status: not_assessable|criteria_not_met|criteria_met

longitudinal_data: []
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

## Hard constraints

Hermes MUST NOT:

1. Convert `ILD` directly into a named ILD.
2. Convert `Pulmonary fibrosis` directly into IPF.
3. Convert fibrosis directly into UIP.
4. Infer HRCT pattern from CXR.
5. Invent honeycombing/traction bronchiectasis from generic CXR fibrosis.
6. Convert UIP pattern directly into IPF.
7. Diagnose IPF without considering alternative known causes.
8. Infer CTD-ILD from positive ANA alone.
9. Infer HP from exposure or serum IgG alone.
10. Treat absent identified exposure as exclusion of fibrotic HP.
11. Apply PPF criteria to IPF.
12. Diagnose PPF from one study.
13. Count FVC and DLCO as two PPF domains.
14. Infer radiological progression without comparable prior imaging.
15. Count missing data as stability.
16. Count acute edema/infection as fibrotic progression without evidence.
17. Infer etiology from fibrosis + calcification alone.
18. Treat No Finding CXR as exclusion of HRCT ILD.
19. Convert AI score into disease probability.
20. Issue autonomous treatment/testing/procedure/disposition instructions.
21. Omit doctor review.
