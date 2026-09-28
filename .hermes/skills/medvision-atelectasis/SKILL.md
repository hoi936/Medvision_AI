---
name: medvision-atelectasis
description: Evidence-grounded clinical reasoning procedure for the VinBigData Atelectasis radiographic finding in MedVision Hermes. Treats the AI output as imaging evidence, evaluates volume-loss and mechanism context, keeps pneumonia and obstructing-lesion hypotheses separate, checks missing/conflicting evidence and safety, and produces a bounded assessment for clinician review.
---

# MedVision Atelectasis Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: atelectasis
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Atelectasis`

This skill does not establish a final etiologic diagnosis and does not prescribe treatment.

## Progressive disclosure

Before applying detailed medical rules, load:

`skill_view("medvision-atelectasis", "references/references.md")`

When detailed evidence boundaries, mechanism provenance, imaging signs, or limitations are required, load:

`skill_view("medvision-atelectasis", "references/ATELECTASIS_EVIDENCE.md")`

Do not invent medical facts that are not supported by those references.

## Core semantic rule

`Atelectasis` from the image AI is a **radiographic finding / pathophysiologic state**.

It is NOT automatically:
- pneumonia;
- lung cancer;
- airway obstruction;
- mucus plugging;
- perioperative complication;
- respiratory failure;
- indication for bronchoscopy or another procedure.

## Procedure

### Step 1 — Preserve image evidence

Record:
- canonical finding;
- model score;
- localization/lobe if supplied;
- extent if supplied;
- morphology if supplied;
- volume-loss signs if supplied;
- model/version when available.

Do not invent localization or morphology.

Do not convert AI score into patient disease probability without validated calibration.

### Step 2 — Evaluate imaging context

Look for available evidence of:
- volume loss;
- fissure displacement;
- bronchovascular crowding/displacement;
- adjacent hyperinflation;
- diaphragm/mediastinal/hilar displacement;
- CT or radiologist correlation.

Absence of these fields from the payload is missing information, not negative evidence.

### Step 3 — Evaluate mechanism hypotheses

Assess separately:

#### Obstructive / resorptive
Possible only when case evidence supports an airway-obstruction context [S1][S3][S4].

Do not equate obstruction with malignancy.

#### Compressive / passive
Consider when pleural effusion, pneumothorax or another compression context is present [S1][S4].

Co-occurrence does not prove causality.

#### Surface-tension related
Consider only when case context supports it [S1][S4].

#### Fibrotic / cicatrization
Consider when pulmonary fibrosis evidence is present [S4].

#### Gravity-dependent / perioperative
Use perioperative-specific reasoning only when surgery/anesthesia/ventilation context is actually supplied [S5][S6].

### Step 4 — Evaluate clinical consequence

Look for:
- respiratory symptoms;
- hypoxemia;
- physiologic instability;
- postoperative respiratory dysfunction if applicable.

Atelectasis may have minor or serious clinical consequences depending on context [S2].

Do not infer respiratory failure from the image label alone.

### Step 5 — Keep pneumonia separate

Atelectasis alone does not diagnose pneumonia [S4].

If compatible infection evidence exists:
- evaluate pneumonia/infection as a separate hypothesis;
- list supporting/contradicting/missing evidence.

Do not output:
`Atelectasis -> pneumonia confirmed`.

Absence of fever/cough may reduce pneumonia support but does not contradict atelectasis itself.

### Step 6 — Check obstructing-lesion context

If localized/lobar atelectasis plus independent evidence suggests airway obstruction:

emit:

`OBSTRUCTIVE_CAUSE_TO_REVIEW`

Preserve uncertainty.

Do not state lung cancer or central tumor without independent supporting evidence.

### Step 7 — Evidence buckets

Return:

- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing data is never negative evidence.

### Step 8 — Conflict detection

If AI evidence conflicts with trusted human review or later definitive imaging:

emit:

`EVIDENCE_CONFLICT`

Preserve both sources.

Do not silently prefer AI.

### Step 9 — Safety

If case data indicate:
- significant hypoxemia;
- respiratory distress;
- physiologic instability;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not issue autonomous therapy/procedure instructions.

### Step 10 — Produce bounded assessment

Separate:

1. radiographic finding;
2. imaging/volume-loss context;
3. mechanism hypotheses;
4. pneumonia/infection hypothesis;
5. obstructing-lesion hypothesis;
6. supporting evidence;
7. conflicting/contradicting evidence;
8. missing information;
9. safety flags;
10. uncertainty;
11. clinician-review requirement;
12. citations.

## Evidence rules

### [S1] Definition
Atelectasis is partial or complete lung collapse.

### [S1][S3][S4] Imaging/mechanism rule
Atelectasis may arise through obstruction/resorption, compression/pleural-pressure changes, surface-tension abnormalities and other mechanisms. Volume-loss features support radiographic interpretation.

### [S2] Clinical consequence rule
Clinical impact varies substantially with extent, mechanism and patient reserve.

### [S4] Pneumonia guardrail
Radiographic atelectasis alone does not establish pneumonia.

### [S5][S6] Perioperative scope rule
Perioperative-specific reasoning is applied only when the case is actually perioperative.

## Output schema

```yaml
finding: atelectasis
finding_type: radiographic_finding

image_evidence:
  model_score: null
  localization: unknown
  extent: unknown
  morphology: unknown
  volume_loss_features: []

mechanism_hypotheses:
  obstructive:
    status: unknown
    evidence: []
  compressive:
    status: unknown
    evidence: []
  surface_tension_related:
    status: unknown
    evidence: []
  fibrotic:
    status: unknown
    evidence: []
  gravity_or_perioperative:
    status: unknown
    evidence: []

differential_context:
  pneumonia:
    status: unknown
    evidence: []
  obstructing_lesion:
    status: unknown
    evidence: []

supporting_evidence: []
contradicting_evidence: []
missing_evidence: []
conflicts: []

safety:
  priority: routine
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true

citations: []
```

## Hard constraints

1. Never convert Atelectasis AI output directly into a final etiologic diagnosis.
2. Never equate atelectasis with pneumonia.
3. Never equate atelectasis with lung cancer.
4. Never infer obstruction/mucus plug/foreign body/tumor without supporting context.
5. Never infer perioperative atelectasis without perioperative context.
6. Never infer respiratory failure from the image finding alone.
7. Never invent lobe, extent or morphology.
8. Never treat absence of infection symptoms as contradiction of atelectasis itself.
9. Never treat coexisting pleural effusion as proof of compressive causation.
10. Never convert AI model score into disease probability without validated calibration.
11. Never treat missing data as negative evidence.
12. Never issue autonomous treatment/procedure orders.
13. Always require clinician review.
14. Every medical rule must be traceable to references.
15. Preserve evidence conflicts instead of silently resolving them.

## Not encoded in v1

Do not invent detailed rules for:
- pediatric/neonatal atelectasis;
- bronchoscopy indications;
- mucus-plug-specific algorithms;
- quantitative collapse severity;
- detailed intervention selection;
- ultrasound-only phenotypes;
- unsupported CXR mimics.

These require additional evidence.
