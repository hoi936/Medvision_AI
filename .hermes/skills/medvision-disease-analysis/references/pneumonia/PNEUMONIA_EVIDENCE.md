# PNEUMONIA_EVIDENCE.md

## Scope

This is the first Disease Analysis v2 module for MedVision Hermes: **Pneumonia / Community-Acquired Pneumonia (CAP) hypothesis reasoning**.

It is not a new VinBigData finding skill and does not change the 14 finding mappings.

Target flow:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ pneumonia/CAP reference module
```

The disease layer must keep:

```text
RADIOGRAPHIC_FINDING != PNEUMONIA_DIAGNOSIS
```

## Core source-backed semantics

ATS/IDSA 2019 focuses on adults with a pneumonia syndrome plus radiographic confirmation and notes that clinical signs/symptoms alone are inaccurate for CAP diagnosis. The IDSA CAP pathway defines CAP as pneumonia acquired outside the hospital and excludes major immunocompromising conditions from its pathway scope. ACR 2024 supports that a negative/indeterminate CXR does not always end evaluation when clinical concern remains. Fleischner 2024 keeps consolidation/opacity as imaging descriptors rather than etiologic diagnoses.

## MedVision disease states

Internal system-policy labels:

```text
PNEUMONIA_HYPOTHESIS_SUPPORTED
PNEUMONIA_HYPOTHESIS_POSSIBLE_BUT_NOT_RADIOGRAPHICALLY_SUPPORTED
IMAGING_FINDING_WITHOUT_SUFFICIENT_CLINICAL_SUPPORT
PNEUMONIA_HYPOTHESIS_CONFLICTED
PNEUMONIA_HYPOTHESIS_NOT_ESTABLISHED
CAP_GUIDELINE_SCOPE_LIMITATION
SEVERE_CAP_CRITERIA_MET
```

These are bounded reasoning states, not final physician diagnoses.

## Acquisition context

Only set `community_acquired: true` when acquisition outside the hospital is actually supported.

If hospital acquisition is known:
- retain broader pneumonia hypothesis;
- set `community_acquired: false`.

If acquisition context is missing:
- keep `community_acquired: unknown`.

## Population scope

If major immunocompromise is known, emit `CAP_GUIDELINE_SCOPE_LIMITATION`. The broader pneumonia hypothesis may still be discussed, but the adult immunocompetent CAP pathway must not be treated as fully applicable.

## Imaging evidence

Potentially compatible VinBigData findings:
- Consolidation
- Lung Opacity
- Infiltration

Guardrails:
- Consolidation alone does not prove pneumonia.
- Lung Opacity is broad/nonspecific.
- Infiltration is a legacy/nonspecific label.
- Pleural effusion may coexist with pneumonia but does not prove parapneumonic effusion or empyema.
- Atelectasis may coexist with or mimic airspace disease; do not force resolution toward pneumonia.

If CXR has No finding or no compatible positive class but the clinical syndrome is strongly suggestive:
- keep pneumonia unresolved/possible;
- mark lack of radiographic support;
- do not say pneumonia is excluded;
- do not autonomously order CT.

## Clinical syndrome

Use only supplied data. Examples of supportive features include:
- cough
- fever
- sputum
- pleuritic chest pain
- dyspnea
- abnormal respiratory examination
- hypoxemia

None is individually diagnostic. Missing symptom data stays missing.

## Basic fusion states

### A. Compatible imaging + compatible acute clinical syndrome

Example:

```text
Consolidation POSITIVE + acute cough + fever
```

Output:
`PNEUMONIA_HYPOTHESIS_SUPPORTED`

Do not output:
- pneumonia confirmed
- bacterial pneumonia confirmed
- pathogen identified

### B. Compatible imaging + insufficient clinical context

Example:

```text
Consolidation POSITIVE
symptoms missing
```

Output:
`IMAGING_FINDING_WITHOUT_SUFFICIENT_CLINICAL_SUPPORT`

### C. Compatible clinical syndrome + no radiographic support

Example:

```text
fever + cough + dyspnea
No finding POSITIVE
```

Output:
`PNEUMONIA_HYPOTHESIS_POSSIBLE_BUT_NOT_RADIOGRAPHICALLY_SUPPORTED`

### D. Explicit trusted conflict

Example:

```text
AI: focal opacity
CT: no corresponding airspace abnormality
```

Output can include:
`PNEUMONIA_HYPOTHESIS_CONFLICTED`
and `EVIDENCE_CONFLICT`.

Preserve both sources.

## Labs

WBC, CRP and similar inflammatory markers are nonspecific supportive context.

A low procalcitonin must not independently:
- exclude bacterial pneumonia;
- erase otherwise compatible imaging/clinical evidence;
- determine antibiotic treatment.

Do not convert any lab into a pneumonia probability.

## Etiology guardrails

Pneumonia hypothesis does not automatically mean:
- bacterial
- viral
- aspiration
- TB
- fungal
- MRSA
- Pseudomonas
- any specific organism

Specific etiology requires independent microbiological/epidemiological evidence.

## Severe CAP criteria

When adult CAP scope is sufficiently applicable and required variables are actually supplied:

```text
>=1 major criterion OR >=3 minor criteria
→ SEVERE_CAP_CRITERIA_MET
```

Major:
1. septic shock requiring vasopressors
2. respiratory failure requiring mechanical ventilation

Minor:
1. respiratory rate >=30/min
2. PaO2/FiO2 <=250
3. multilobar infiltrates
4. confusion/disorientation
5. BUN >=20 mg/dL
6. WBC <4,000/µL due to infection
7. platelets <100,000/µL
8. core temperature <36°C
9. hypotension requiring aggressive fluid resuscitation

Do not:
- count missing variables as negative;
- infer multilobar disease from multiple AI class labels;
- infer infection-attributable leukopenia unless attribution is actually supported;
- infer shock from isolated hypotension;
- turn severe-CAP criteria into autonomous ICU/admission/treatment decisions.

## Overlap/de-duplication

If Lung Opacity + Infiltration + Consolidation plausibly represent the same airspace process:
- preserve all upstream findings;
- apply existing overlap/de-duplication policy;
- do not count them as three independent confirmations of pneumonia.

## No Finding interaction

`No finding POSITIVE` plus symptoms is not by itself an image contradiction.

Clinical symptoms can keep pneumonia unresolved, while No Finding continues to mean no modeled target finding identified on that CXR output.

## Safety

Independent severe hypoxemia, respiratory failure, shock, or severe-CAP criteria may support `HIGH_PRIORITY_CLINICAL_REVIEW`.

No autonomous:
- antibiotics
- CT
- admission/ICU disposition
- intubation
- vasopressors
- pleural drainage
- other treatment/procedure

Doctor review remains required.

## Recommended output

```yaml
disease_hypothesis:
  name: pneumonia
  status: not_established|possible|supported|conflicted

subtype:
  community_acquired: true|false|unknown

scope:
  adult: true|false|unknown
  immunocompromised: true|false|unknown
  cap_guideline_scope_applicable: true|false|unknown

imaging_support:
  compatible_findings: []
  associated_findings: []
  radiographic_support: present|absent|indeterminate|unknown
  overlap_notes: []

clinical_support:
  symptoms: []
  signs: []
  missing: []

laboratory_support:
  findings: []
  missing: []

etiology:
  status: unknown
  hypotheses: []
  confirmed_organism: null

severity:
  severe_cap_assessed: false
  major_criteria_present: []
  minor_criteria_present: []
  severe_cap_criteria_met: false

conflicts: []
missing_evidence: []

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
1. Convert Consolidation/Lung Opacity/Infiltration directly into pneumonia.
2. Diagnose bacterial pneumonia from imaging or inflammatory labs alone.
3. Use low procalcitonin as a standalone exclusion rule.
4. Call pneumonia community-acquired when acquisition context is unknown/hospital-acquired.
5. Apply immunocompetent CAP scope without flagging known major immunocompromise.
6. Infer empyema/parapneumonic effusion from pleural effusion alone.
7. Infer a pathogen without specific evidence.
8. Treat No Finding as universal pneumonia exclusion.
9. Triple-count overlapping airspace labels.
10. Infer multilobar disease from multiple class labels.
11. Treat missing severity data as negative.
12. Convert severe-CAP criteria into autonomous disposition/treatment.
13. Convert AI score into pneumonia probability.
14. Drop conflicts.
15. Omit doctor review.
