# ACUTE_AORTIC_SYNDROME_EVIDENCE.md

## 0. Scope

This module defines Disease Analysis v2 reasoning for:

**Acute Aortic Syndrome (AAS) concern**

It is not:
- a new image-finding skill;
- a new top-level Hermes skill;
- a treatment/procedure engine.

Target flow:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ acute-aortic-syndrome reference module
```

Central rules:

```text
Aortic enlargement != aneurysm
Aortic enlargement != dissection
Aortic enlargement != AAS
Normal CXR != AAS excluded
```

---

## 1. What AAS means

AAS is a disease-level acute aortic concept that includes acute aortic pathologies such as:
- aortic dissection;
- intramural haematoma;
- penetrating atherosclerotic ulcer;
- closely related acute aortic wall catastrophes depending on source context.

Do not infer a subtype unless definitive imaging or explicit clinician evidence establishes it.

Use:

`AAS_SUBTYPE_UNRESOLVED`

when acute aortic concern is supported but subtype is not established.

---

## 2. Disease-analysis states

```text
ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED
ACUTE_AORTIC_SYNDROME_CONCERN_INDETERMINATE
AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT
ACUTE_AORTIC_SYNDROME_CONCERN_CONFLICTED
ACUTE_AORTIC_SYNDROME_NOT_ESTABLISHED
DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS
AAS_SUBTYPE_UNRESOLVED
MALPERFUSION_CONCERN
```

Only definitive aortic imaging or explicit definitive source evidence may support `DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS`.

---

## 3. CXR / Aortic enlargement

Existing MedVision `Aortic enlargement` remains radiographic evidence only.

A positive class may raise disease concern if compatible acute clinical features exist, but it cannot establish:
- aneurysm;
- dissection;
- intramural haematoma;
- penetrating ulcer;
- rupture.

Plain chest X-ray is not sufficiently sensitive or specific for AAS diagnosis [S2][S3].

Therefore:

```text
Aortic enlargement + acute high-risk syndrome
→ AAS concern may be supported
```

but:

```text
Aortic enlargement alone
→ AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT
```

---

## 4. Normal / No Finding CXR

A normal or No Finding CXR does not exclude AAS.

If acute clinical concern is high:
- preserve AAS concern;
- mark lack of radiographic support;
- do not say dissection excluded.

This is especially important because proximal aortic disease may be missed on chest radiography [S3].

---

## 5. Acute clinical features

Use only supplied data.

Potentially concerning features include:
- abrupt severe chest pain;
- abrupt severe back pain;
- abrupt severe abdominal pain;
- syncope;
- focal neurologic deficit;
- pulse deficit;
- significant inter-arm blood-pressure differential;
- new aortic regurgitation murmur;
- hypotension/shock;
- limb ischemia;
- mesenteric/renal ischemia features;
- known thoracic aortic aneurysm;
- known genetic aortopathy;
- known bicuspid aortic valve with aortopathy;
- recent aortic instrumentation/repair where clinically relevant.

No single symptom establishes AAS.

Do not invent "tearing" pain if the user/source only says severe pain.

---

## 6. Risk scoring

ACC/AHA notes AAD-RS and other scores can aid evaluation, but they are not universally adopted.

MedVision v1 policy:
- do not compute AAD-RS unless a separately validated implementation is explicitly added;
- do not infer missing score variables;
- do not create a hidden risk score.

If an external clinician provides an AAD-RS:
- preserve its value and provenance;
- do not relabel it as a MedVision-generated score.

---

## 7. D-dimer

No biomarker is diagnostic for AAS [S2].

A low D-dimer may help make AAS unlikely only in an appropriately low-pretest-risk context and in conjunction with a validated diagnostic strategy.

Therefore:

```text
low D-dimer alone != AAS excluded
high D-dimer alone != AAS confirmed
```

Do not use a D-dimer result to override strong clinical/imaging concern by itself.

No universal MedVision AAS rule-out algorithm is encoded in v1.

---

## 8. Definitive imaging

Definitive/advanced aortic imaging such as:
- CT/CTA;
- TEE;
- MRI/MRA;

is substantially stronger than CXR for AAS diagnosis [S2].

If definitive imaging explicitly demonstrates:
- dissection;
- intramural haematoma;
- penetrating ulcer;
- rupture/contained rupture;
- other explicit AAS subtype;

Hermes may emit:

`DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS`

and preserve the explicit subtype.

Do not infer subtype if the report only says "acute aortic syndrome".

---

## 9. Malperfusion concern

If actual supplied evidence indicates:
- focal neurologic deficit/stroke from suspected branch involvement;
- limb ischemia;
- renal ischemia;
- mesenteric ischemia;
- coronary involvement;
- shock/tamponade concern;

Hermes may emit:

`MALPERFUSION_CONCERN`

or a corresponding existing safety flag.

Do not infer branch-vessel malperfusion from pain alone.

---

## 10. Pleural effusion / mediastinal findings

Pleural effusion, mediastinal widening, abnormal aortic contour, or other CXR findings may raise suspicion in context.

They do not prove:
- rupture;
- hemothorax;
- dissection;
- AAS subtype.

Do not convert pleural effusion into aortic rupture without explicit evidence.

---

## 11. Aneurysm vs AAS

A known thoracic aortic aneurysm increases clinical concern when acute symptoms occur, but:

```text
known aneurysm != acute dissection
```

Stable chronic aneurysm without acute syndrome evidence should not become AAS.

Use:

`AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT`

or another bounded chronic-aortic state if appropriate.

---

## 12. Competing diagnoses

Acute chest/back pain may also be due to:
- acute coronary syndrome;
- pulmonary embolism;
- pneumothorax;
- pneumonia;
- musculoskeletal pain;
- other causes.

MedVision should preserve competing hypotheses if supported.

Do not force a winner without adequate evidence.

Existing Pneumothorax/Pneumonia/HF modules remain independent.

---

## 13. Evidence-fusion examples

### State A — Aortic enlargement only

```text
Aortic enlargement POSITIVE
no acute symptoms supplied
```

→ `AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT`

### State B — Aortic enlargement + abrupt severe chest/back pain

```text
Aortic enlargement POSITIVE
+ abrupt severe chest/back pain
```

→ `ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED`

Do not output "dissection confirmed".

### State C — No Finding CXR + high-risk acute syndrome

```text
No finding POSITIVE
+ abrupt severe pain
+ pulse/BP/perfusion abnormality
```

→ AAS concern may remain supported or strongly indeterminate.

No Finding does not exclude AAS.

### State D — low D-dimer only

```text
low D-dimer
risk context incomplete
```

→ no rule-out conclusion.

### State E — definitive CTA confirms type A dissection

→ `DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS`
with subtype preserved as explicit source data.

---

## 14. Safety

AAS concern with acute high-risk features should trigger:

`HIGH_PRIORITY_CLINICAL_REVIEW`

under existing MedVision safety policy.

Do not autonomously:
- order CTA/TEE/MRI;
- initiate antihypertensive/anti-impulse therapy;
- transfer to surgery;
- recommend operative/endovascular repair;
- start analgesia;
- make disposition decisions.

This module only produces bounded concern + safety priority + evidence trace.

---

## 15. Recommended output

```yaml
disease_hypothesis:
  name: acute_aortic_syndrome
  status: not_established|indeterminate|concern_supported|conflicted|imaging_confirmed

subtype:
  status: unresolved|explicit
  value: null
  source: null

aortic_evidence:
  cxr_findings: []
  definitive_imaging: []
  prior_aortic_disease: []

clinical_support:
  pain_features: []
  neurologic_features: []
  perfusion_features: []
  hemodynamic_features: []
  examination_features: []

risk_context:
  known_aneurysm: unknown
  genetic_aortopathy: unknown
  bicuspid_aortic_valve_aortopathy: unknown
  prior_aortic_intervention: unknown
  external_risk_score: null

biomarkers:
  d_dimer: unknown
  interpretation: unknown

malperfusion:
  concern: false
  territories: []

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

## 16. Hard constraints

Hermes MUST NOT:

1. Convert Aortic enlargement directly into aneurysm.
2. Convert Aortic enlargement directly into dissection/AAS.
3. Exclude AAS because CXR is normal or No Finding.
4. Diagnose AAS from mediastinal widening alone.
5. Diagnose rupture from pleural effusion alone.
6. Infer a specific AAS subtype without definitive evidence.
7. Compute hidden AAD-RS/AORTAs scores.
8. Treat low D-dimer alone as universal AAS exclusion.
9. Treat high D-dimer alone as AAS confirmation.
10. Infer malperfusion from pain alone.
11. Equate chronic aneurysm with acute dissection.
12. Convert AI score into AAS probability.
13. Drop conflicting definitive imaging/clinical evidence.
14. Force AAS over ACS/PE/pneumothorax/other causes without evidence.
15. Issue autonomous imaging, medication, procedure, surgery, or disposition recommendations.
16. Omit doctor review.
