---
name: medvision-other-lesion
description: Conservative evidence-grounded reasoning procedure for the VinBigData Other lesion finding in MedVision Hermes. Preserves this catch-all local radiographic abnormality without inventing morphology, anatomy, or diagnosis; keeps multiple detections and later human/CT characterization separate; and deduplicates specific overlapping findings only when correspondence is supported.
---

# MedVision Other Lesion Skill

## MedVision Metadata

- Version: 1.0.0
- Domain: thoracic-radiology
- Finding: other_lesion
- Requires doctor review: true

## Purpose

Use this skill when the MedVision chest X-ray pipeline reports the canonical VinBigData finding:

`Other lesion`

This is a **catch-all local-finding compatibility skill**.

Unknown/unspecified is an acceptable result.

Do not invent a specific morphology, anatomy, disease, or etiology merely to make the assessment more specific.

## Progressive disclosure

Before applying detailed rules, load:

`skill_view("medvision-other-lesion", "references/references.md")`

When dataset taxonomy, multiple-object semantics, bbox limitations, overlap rules, or external characterization behavior is needed, load:

`skill_view("medvision-other-lesion", "references/OTHER_LESION_EVIDENCE.md")`

Do not invent facts not supported by those references.

## Core semantic rule

`Other lesion` from VinBigData AI is:

`UNSPECIFIED_LOCAL_RADIOGRAPHIC_ABNORMALITY`

Suggested system tag:

`UNSPECIFIED_LOCAL_FINDING`

The tag is `MEDVISION_SYSTEM_POLICY`.

It is NOT automatically:
- `Other diseases`;
- Nodule/Mass;
- tumor/cancer;
- infection/pneumonia;
- tuberculosis;
- fracture;
- cavity;
- cyst;
- another specific morphology.

## Procedure

### Step 1 — Preserve all upstream detections

Record each detection independently:
- canonical label `Other lesion`;
- score;
- bbox/image-plane location;
- detection identifier when available;
- model/version.

If multiple `Other lesion` objects exist:
- preserve all evidence objects;
- selector still invokes this skill once.

Do not collapse distinct objects without evidence.

### Step 2 — Keep Other lesion separate from Other diseases

`Other lesion` is a local finding.

`Other diseases` is a separate global diagnostic label in the original VinDr taxonomy [S1].

Never equate them.

### Step 3 — Allow uncertainty

Default when only generic AI output is known:

```yaml
morphology: unknown
anatomic_compartment: unknown
structure: unknown
etiology: unknown
```

This is valid output.

Do not manufacture specificity.

### Step 4 — Do not reverse-map the catch-all label

Do not convert `Other lesion` automatically into original VinDr local classes omitted from the 14-class competition.

Examples that MUST NOT be inferred without explicit characterization:
- fracture;
- edema;
- emphysema;
- enlarged pulmonary artery;
- lung cavity;
- lung cyst;
- mediastinal shift.

The v1 sources do not provide a deterministic official reverse mapping.

### Step 5 — Bounding-box guardrail

A bbox is image-plane localization [S1][S2].

It is not definitive proof of:
- pulmonary;
- pleural;
- mediastinal;
- cardiac;
- skeletal;
- other anatomical origin.

Only record specific anatomy when supplied by sufficiently specific evidence.

### Step 6 — Preserve later specific characterization

If trusted radiologist/CT/other imaging provides a specific description:
- preserve it separately;
- preserve its modality/source;
- keep original `Other lesion` AI provenance.

Do not claim the AI predicted the later morphology.

Do not silently delete the generic AI finding.

### Step 7 — Do not auto-select another finding skill

If human/CT characterization resembles an existing canonical finding but that AI canonical finding is not POSITIVE:
- record the characterization as evidence;
- do not violate selector contract by invoking the other finding skill.

Finding-specific skill selection remains based on canonical AI `decision == "POSITIVE"`.

### Step 8 — Relationship to specific positive findings

If another canonical finding is also POSITIVE:
- preserve both skills/results.

If correspondence is unknown:
- keep them separate.

If evidence supports that both describe the same abnormality:
- use the specific finding as morphology refinement;
- emit `OVERLAPPING_FINDING_EVIDENCE`;
- avoid double counting.

Do not remove either upstream result.

### Step 9 — Different regions remain distinct

If detections clearly occupy different regions:
- do not merge;
- do not mark same-lesion overlap.

### Step 10 — Disease guardrail

Never infer directly from `Other lesion`:
- cancer/tumor;
- benignity;
- infection;
- TB;
- severity;
- acuity/chronicity.

Disease hypotheses require independent evidence and remain separate.

### Step 11 — Score semantics

Preserve score as model output.

Do not convert score into:
- cancer probability;
- serious-disease probability;
- morphology probability;
- clinical severity.

### Step 12 — Evidence buckets

Return:
- `supporting_evidence`
- `contradicting_evidence`
- `missing_evidence`
- `unknown_information`

Missing characterization is not a negative finding.

### Step 13 — Conflict detection

If AI conflicts with trusted human review or later imaging:

emit:

`EVIDENCE_CONFLICT`

Preserve both.

Specific characterization of a real abnormality is not automatically a conflict; it may simply refine the generic label.

### Step 14 — Safety

`Other lesion` alone is not automatically an emergency.

If independent evidence shows a severe acute syndrome:

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

where appropriate.

Do not issue autonomous imaging/procedure/treatment orders.

### Step 15 — Produce bounded assessment

Separate:
1. generic upstream label;
2. every detection/bbox;
3. anatomic characterization;
4. specific later characterization;
5. relation to specific positive AI findings;
6. overlap/de-duplication;
7. disease hypotheses from independent evidence;
8. supporting/contradicting evidence;
9. missing evidence;
10. conflicts;
11. safety;
12. uncertainty;
13. clinician review;
14. citations.

## Evidence rules

### [S1] Catch-all rule
`Other lesion` means lesions outside the listed findings/abnormalities and is a local, bbox-annotated label.

### [S1] Other lesion vs Other diseases
The two are separate local-vs-global labels.

### [S2] Object rule
The 14-class competition uses `Other lesion` as class 9; object metadata may contain multiple objects per image.

### [S3] Terminology rule
Apply specific thoracic-imaging terminology only when the actual morphology/location is supplied.

### [S4] AI workflow rule
AI lesion/location output is support evidence rather than autonomous final diagnosis.

## Output schema

```yaml
finding: other_lesion
finding_type: unspecified_local_radiographic_finding

upstream:
  canonical_label: Other lesion
  model_version: unknown

detections:
  - detection_id: unknown
    model_score: null
    bounding_box: unknown
    image_plane_location: unknown

anatomic_characterization:
  status: unknown
  compartment: unknown
  structure: unknown

specific_characterization:
  available: false
  source: unknown
  modality: unknown
  morphology: unknown
  description: unknown

relationship_to_specific_findings:
  matched_findings: []
  unmatched_findings: []
  overlap_flags: []
  notes: []

disease_hypotheses: []

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

1. Never equate Other lesion with Other diseases.
2. Never equate Other lesion with cancer/tumor.
3. Never equate Other lesion with Nodule/Mass.
4. Never equate Other lesion with infection/pneumonia.
5. Never equate Other lesion with tuberculosis.
6. Never infer a specific morphology from the generic label.
7. Never infer a specific anatomical compartment from the label/bbox alone.
8. Never automatically reverse-map Other lesion to omitted original VinDr local classes.
9. Never assume another positive finding is the same lesion without correspondence evidence.
10. Never double count generic + specific labels when they are shown to represent one abnormality.
11. Never merge clearly separate detections.
12. Never erase upstream AI provenance after later characterization.
13. Never claim AI predicted morphology supplied only by radiologist/CT.
14. Never auto-select another finding skill from human/CT characterization alone.
15. Never convert AI score into disease probability/severity.
16. Never treat missing specificity as negative evidence.
17. Never issue autonomous imaging/procedure/treatment orders.
18. Always require clinician review.
19. Every taxonomy/medical terminology rule must be traceable to references.
20. Preserve evidence conflicts and refinements distinctly.

## Not encoded in v1

Do not invent:
- a hidden disease differential for `Other lesion`;
- mapping to omitted 22-class VinDr labels;
- automatic anatomy assignment;
- bbox colocalization algorithm;
- treatment/follow-up decisions.

These require separate evidence or a future taxonomy specification.
