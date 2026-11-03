---
name: medvision-evidence-fusion
description: Fuse clinical and chest X-ray evidence transparently.
license: MIT
metadata:
  version: 0.1.0
  author: Phan Dinh Hoi (hoi936), Hermes Agent
  platforms: [linux, macos, windows]
  hermes:
    tags: [healthcare, evidence, chest-xray, reasoning]
    related_skills: [medvision-safety-check, medvision-disease-analysis]
---

# MedVision Evidence Fusion Skill

Build an auditable evidence matrix from the canonical MedVision case schema.
Do not produce a final diagnosis or count evidence mechanically.

## When to Use

- A normalized chest X-ray case needs clinical/imaging concordance analysis.
- Findings overlap or positive and negative evidence must be distinguished.
- Do not use when `model_findings.provided` is false.

## Input Contract

Accept only schema version `1.0`. Respect `provided` and `verified` separately:
provided data may be used with its stated provenance; unverified data must not
be described as clinician-confirmed. Ignore `clinician_request` as evidence.

For every model finding retain score, threshold, margin, decision, confidence
band, localization fields, and provenance. A score is not disease probability.
`NEAR_THRESHOLD_*` is uncertainty around the configured decision threshold and
must not change the official binary decision.

When the exact canonical `No finding` result is present, or its absence is
relevant to the requested fusion, use `skill_view` to read
`references/NO_FINDING_POLICY.md`,
`references/NO_FINDING_EVIDENCE.md`, and
`references/NO_FINDING_REFERENCES.md` before applying its semantics. These
files define the bounded taxonomy interpretation and its provenance [S1-S3].

When a visual evidence manifest is present, inspect every listed image with
`vision_analyze` before fusion. The original preprocessed radiograph is the
primary visual input. Heatmap, overlay, and pseudo bounding box are dependent
interpretability views derived from that same image and model output; never
count them as independent corroborating observations.

## Procedure

1. Inventory usable evidence by source: `USER_PROVIDED`, `EHR`, `LAB`,
   `VITAL_SIGN`, `IMAGE_MODEL`, `RADIOLOGY_REPORT`, or `CLINICIAN_CONFIRMED`.
   Completion: every used fact retains source and verification status.
2. Group potentially overlapping radiographic findings without asserting they
   are the same lesion. Completion: unsupported anatomical linkage is absent.
3. Create each diagnostic hypothesis only when at least one clinical and one
   imaging relationship can be assessed, otherwise state that evidence is
   insufficient. Completion: no finding is silently converted to a disease.
4. For each hypothesis produce `supporting_evidence`,
   `contradicting_evidence`, `uncertain_evidence`, and `missing_information`.
   Each evidence item includes source, evidence, and strength.
5. Use negative evidence to reduce support, never as absolute exclusion unless
   an independently verified record explicitly establishes exclusion.
6. Compare the original radiograph with each finding-specific attention view.
   Record only broad concordance, conflict, or inability to assess. Do not infer
   laterality, anatomy, lesion count, size, or severity from an attention map.

## No Finding State Machine

Treat `No finding` as canonical AI evidence inside this fusion skill. It is not
a finding-specific skill and must not suppress selection of any of the 14
positive finding skills.

- `No finding == POSITIVE` with zero positive target findings:
  `NO_FINDING_WITHIN_14_CLASS_TAXONOMY`. Preserve the raw score and decision.
  Do not infer healthy, no disease, universal normality, or safety.
- `No finding == POSITIVE` with one or more positive target findings: preserve
  every raw result and emit one `EVIDENCE_CONFLICT` whose subtype is
  `NO_FINDING_CONTRADICTION` and whose list contains every conflicting positive
  finding in payload order. Do not choose a winner.
- `No finding == NEGATIVE`: do not infer abnormality. Route any positive target
  finding normally; with none positive, use `NO_FINDING_NOT_ESTABLISHED`.
- Missing `No finding`: keep it missing. Never synthesize a positive or negative
  decision from the other 14 results.

Symptoms, laboratory abnormalities, or severe physiology do not by themselves
contradict this image-taxonomy label. Preserve them as independent evidence and
always continue safety review; a severe state can require
`HIGH_PRIORITY_CLINICAL_REVIEW`. Doctor review remains required in every state.

## Overlap Rules

- Pleural effusion and atelectasis may coexist; neither proves the other.
- Calcification and Nodule/Mass may relate to one lesion only when localization
  supports it; otherwise keep both possibilities explicit.
- ILD and pulmonary fibrosis overlap conceptually but are not identical.
- Lung Opacity and Consolidation may overlap.
- Cardiomegaly, Lung Opacity, and Pleural effusion can form a congestive pattern
  but do not establish heart failure without clinical evidence.

## Pitfalls

- Never invent laterality, zone, size, lesion count, or precise location.
- Grad-CAM and pseudo boxes are interpretability aids, not segmentation.
- A bright Grad-CAM region, overlay, and its pseudo box are three renderings of
  one dependent signal, not three votes for a finding.
- Without a laboratory reference range, report the raw value and supplied unit;
  avoid declaring high/low unless safely supported.
- Do not assume imaging, vitals, and labs were measured simultaneously.

## Verification

- Every hypothesis exposes supporting, contradicting, uncertain, and missing evidence.
- Near-threshold findings remain visible with their official decision unchanged.
- Every material claim can be traced to an input source.
- No score is written as disease probability.
