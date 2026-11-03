---
name: medvision-pneumothorax
description: Evidence-grounded clinical reasoning procedure for the VinBigData Pneumothorax radiographic finding in MedVision Hermes. Treats the AI output as imaging evidence, checks clinical context, missing data, conflicts, safety signals, and produces a bounded assessment for physician review.
---

# MedVision Pneumothorax Skill

## Purpose

Use this skill when MedVision receives a `pneumothorax` finding from the chest X-ray AI service or when pneumothorax is otherwise present in the case evidence.

This skill does **not** make a final diagnosis and does **not** prescribe treatment.

## MedVision Metadata

- Version: `1.0.0`
- Domain: `thoracic-radiology`
- Finding: `pneumothorax`
- Doctor review required: `true`

## Authoritative references

Read `references.md` before adding or modifying medical reasoning rules.
When you need to use the medical rules, you MUST call the skills tool:
`skill_view("medvision-pneumothorax", "references/references.md")`
When deeper provenance or limitations are needed, call:
`skill_view("medvision-pneumothorax", "references/PNEUMOTHORAX_EVIDENCE.md")`
Source precedence:
1. Current BTS 2023 / ERS-EACTS-ESTS 2024 clinical guidance.
2. Fleischner 2024 for imaging terminology.
3. ERS 2015 for supporting PSP context.
4. BTS 2010 for historical context only.

## Core semantic rule

`pneumothorax` from the AI image service is **RADIOGRAPHIC EVIDENCE**.

It is NOT automatically:
- final diagnosis,
- primary spontaneous pneumothorax,
- secondary spontaneous pneumothorax,
- tension pneumothorax,
- clinical instability,
- indication for a specific intervention.

## Procedure

### Step 1 — Preserve image evidence

Record:
- finding name;
- model score;
- laterality/localization if available;
- AI model/version if supplied.

Never rewrite the model score as a patient disease probability unless explicit model calibration supports that interpretation.

### Step 2 — Check scope/classification context

Determine whether the case provides:
- trauma history;
- recent thoracic/medical procedure;
- known underlying lung disease;
- previous pneumothorax;
- smoking history.

If unavailable, mark these as missing/unknown.

Do not label the event `primary spontaneous pneumothorax` without sufficient context.

### Step 3 — Check symptoms and physiology

Look for:
- breathlessness/dyspnoea;
- chest pain;
- available indicators of physiological compromise or instability.

Important:
- absence of symptoms is NOT hard contradictory evidence;
- asymptomatic/minimally symptomatic PSP exists [S2][S3];
- management context depends on symptoms and stability, not image magnitude alone [S2][S3][S4].

### Step 4 — Build evidence buckets

Return four explicit buckets:

#### Supporting
Evidence consistent with the finding/context.

#### Contradicting
Only use when there is a genuine conflicting source.

Do not mark absence of chest pain or dyspnoea as contradiction by itself.

#### Missing
Data required to interpret the finding safely but not supplied.

#### Unknown
Information that cannot be inferred from the case.

### Step 5 — Check conflict

If AI pneumothorax evidence conflicts with a trusted human interpretation or later definitive imaging result, emit:

`EVIDENCE_CONFLICT`

This is a MedVision evidence-consistency policy.

Do not silently choose the AI result over the human/definitive evidence.

### Step 6 — Safety check

If the case contains evidence of:
- significant respiratory symptoms,
- physiological compromise/instability,
- possible tension-pneumothorax context,

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

and explain the triggering evidence.

Do NOT issue autonomous procedure/treatment orders.

### Step 7 — Identify missing data

Prefer explicit missing-data output such as:

- respiratory symptoms not provided;
- physiological status not provided;
- trauma/procedure history not provided;
- underlying lung disease status unknown;
- previous pneumothorax history unknown.

Missing data is not negative evidence.

### Step 8 — Produce bounded assessment

Assessment should separate:

1. `Radiographic finding`
2. `Clinical consistency`
3. `Conflicting evidence`
4. `Missing information`
5. `Safety flags`
6. `Uncertainty`
7. `Doctor review requirement`
8. `Citations`

Use cautious language:
- "The image model identified..."
- "Clinical information is consistent with..."
- "Available evidence is insufficient to classify..."
- "Additional clinical review is required..."

Avoid:
- "The patient definitely has..."
- "This is certainly..."
- treatment orders.

## Evidence rules

### [S1] Imaging terminology
Pneumothorax is air in the pleural space.

### [S2][S3][S4] Clinical-context rule
Symptoms and physiological stability are central to clinical assessment.

### [S2][S3] Mild-presentation rule
A spontaneous pneumothorax may be asymptomatic/minimally symptomatic and clinically stable.

Therefore absence of symptoms does not automatically contradict the image finding.

### [S2][S3][S4] Size/score safety rule
Do not use radiographic size or an AI model score alone to determine clinical urgency/management.

## Not encoded in v1

Do not invent:
- complete radiographic mimic lists;
- traumatic pneumothorax management;
- pediatric pneumothorax rules;
- ventilated-patient rules;
- detailed tension-pneumothorax diagnostic criteria.

These require dedicated evidence sources.

## Output schema

```yaml
finding: pneumothorax
finding_type: radiographic_finding

image_evidence:
  model_score: null
  localization: null

supporting_evidence: []
contradicting_evidence: []
missing_evidence: []
unknown_information: []

classification_context:
  trauma_or_procedure: unknown
  underlying_lung_disease: unknown
  previous_pneumothorax: unknown
  spontaneous_classification: unknown

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

1. Never convert the AI finding directly into a final diagnosis.
2. Never infer tension pneumothorax from the AI label alone.
3. Never infer clinical stability when vital/clinical information is absent.
4. Never treat missing evidence as negative evidence.
5. Never interpret model score as disease probability without validated calibration.
6. Never issue autonomous treatment orders.
7. Always require physician review.
8. Every medical rule must be traceable to `references.md`.
9. If evidence is insufficient, say so.
10. If sources conflict, preserve the disagreement instead of silently resolving it.
