# OTHER_LESION_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Other lesion** trong MedVision Hermes.

`Other lesion` là canonical VinBigData/VinDr-CXR local finding dùng cho một bất thường khu trú không thuộc các finding/abnormality đã liệt kê trong taxonomy nguồn.

Đây phải là skill **bảo thủ nhất** trong nhóm 14 finding skills.

Triết lý trung tâm:

```text
UNSPECIFIED IS A VALID STATE
        ↓
PRESERVE THE LOCAL ABNORMALITY
        ↓
DO NOT INVENT MORPHOLOGY / ANATOMY / ETIOLOGY
        ↓
USE BETTER HUMAN / CT / OTHER EVIDENCE IF AVAILABLE
```

Phạm vi v1:
- adult PA chest-radiograph reasoning consistent with VinDr/VinBigData source semantics;
- canonical label provenance;
- bounding-box/image-plane localization;
- multiple `Other lesion` detections;
- distinction from `Other diseases`;
- relation to more-specific canonical findings;
- preservation of later radiologist/CT characterization;
- overlap/de-duplication only when same-abnormality correspondence is actually supported;
- conflict, missing evidence, uncertainty, doctor review.

Không tự mở rộng v1 thành:
- a generic differential-diagnosis engine;
- tumor/cancer inference;
- fracture/cavity/cyst/edema/emphysema inference;
- automatic reverse-mapping to VinDr local classes omitted from the 14-class competition;
- autonomous CT/biopsy/procedure/treatment ordering.

---

## 1. Evidence hierarchy

### S1 — VinDr-CXR dataset paper + supplementary label definition
**Nguyen HQ, Lam K, Le LT, et al. VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations. Scientific Data. 2022.**  
PMID: 35858929  
PMCID: PMC9300612  
DOI: 10.1038/s41597-022-01498-w  
Primary paper URL: https://pubmed.ncbi.nlm.nih.gov/35858929/  
Supplementary material: https://storage.googleapis.com/kaggle-media/competitions/VinBigData/VinDr_CXR_data_paper.pdf  
Role: **primary semantics: Other lesion is a local label; supplementary definition is catch-all for lesions outside the listed findings/abnormalities**

### S2 — Official VinBigData Chest X-ray Abnormalities Detection competition specification
**VinBigData Chest X-ray Abnormalities Detection — Kaggle competition data specification.**  
URL: https://www.kaggle.com/competitions/vinbigdata-chest-xray-abnormalities-detection/data  
Role: **14-class competition semantics, class 9 Other lesion, object/bbox rows, No finding = absence of the 14 findings**

### S3 — Fleischner Society 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **standardized thoracic-imaging terminology when a later source actually characterizes morphology/location**

### S4 — VinDr-CXR clinical deployment 2022
**Nguyen NH, Nguyen HQ, Nguyen NT, et al. Deployment and validation of an AI system for detecting abnormal chest radiographs in clinical settings. Front Digit Health. 2022.**  
PMID: 35966141  
PMCID: PMC9367219  
DOI: 10.3389/fdgth.2022.890759  
Role: **AI output as abnormality/lesion-location support in a clinical workflow, not autonomous final diagnosis**

### Source precedence

1. S1 for the meaning of `Other lesion` in the original VinDr taxonomy.
2. S2 for 14-class competition/object semantics.
3. S3 only when a specific morphology/location has actually been supplied by a trusted imaging source.
4. S4 for AI-workflow/provenance limitations.

---

## 2. Primary label semantics

### S1

VinDr-CXR separates:
- 22 local labels marked with bounding boxes; and
- 6 global labels reflecting radiologist diagnostic impressions.

`Other lesion` is local label #22.

The supplementary label definition describes it as:

> “Other lesions that are not on the list of findings or abnormalities mentioned above.”

### Hermes interpretation

A VinBigData `Other lesion` output is:

`UNSPECIFIED_LOCAL_RADIOGRAPHIC_ABNORMALITY`

or, as a MedVision system tag:

`UNSPECIFIED_LOCAL_FINDING`

The tag is **MEDVISION_SYSTEM_POLICY**, not a formal radiology term.

It is NOT automatically:
- tumor;
- cancer;
- Nodule/Mass;
- infection;
- tuberculosis;
- fracture;
- cavity;
- cyst;
- edema;
- emphysema;
- mediastinal disease;
- pleural disease;
- a disease-level diagnosis.

---

## 3. Other lesion != Other diseases

### S1

VinDr-CXR explicitly separates:
- `Other lesion` among local labels; and
- `Other diseases` among global diagnostic-impression labels.

### Hermes behavior

Never equate:

```text
Other lesion
=
Other diseases
```

`Other lesion` remains a local radiographic abnormality.

`Other diseases` is a different global label with disease-level semantics in the original VinDr taxonomy.

---

## 4. 14-class competition semantics

### S2

The VinBigData competition uses 14 radiographic finding classes:
- class 9 = `Other lesion`;
- class 14 = `No finding`.

The competition states that `No finding` captures absence of all 14 listed findings.

Training metadata uses one row per detected object and includes:
- class;
- bounding box;
- radiologist identifier;
- image identifier.

An image may contain multiple objects.

### Hermes behavior

`Other lesion` is therefore still an object/local-finding class in the 14-class detector setting.

Do not reinterpret it as:
- an image-level global diagnosis;
- `No finding`;
- `Other diseases`.

---

## 5. Do not reverse-map hidden morphology

The original 22-label VinDr taxonomy contains local findings that are not separate classes in the 14-class competition, such as:
- clavicle fracture;
- edema;
- emphysema;
- enlarged PA;
- lung cavity;
- lung cyst;
- mediastinal shift;
- rib fracture.

However, the official sources used in v1 do **not** establish a deterministic rule:

```text
Other lesion
-> one of those omitted labels
```

### Hermes behavior

Do NOT reverse-map `Other lesion` into any omitted original local label unless a trusted human/imaging source explicitly characterizes the abnormality.

Do not use third-party dataset preprocessing/merging choices as canonical MedVision semantics.

---

## 6. Bounding box / localization semantics

### S1 / S2

`Other lesion` is localized with bounding boxes in the source datasets/competition.

### Hermes behavior

Preserve:
- every detection;
- bounding box;
- image-plane position;
- model score;
- detection identifier if available.

But:

```text
2D bounding box
!=
definitive anatomical structure
```

A bbox alone does not establish:
- pulmonary origin;
- pleural origin;
- mediastinal origin;
- osseous origin;
- a specific organ;
- a specific named lesion.

Use:

```yaml
anatomic_characterization:
  status: unknown
  compartment: unknown
  structure: unknown
```

unless stronger evidence is supplied.

---

## 7. Morphology must come from actual evidence

### S3

Fleischner terminology exists to standardize specific thoracic imaging descriptors and locations.

### Hermes behavior

Do not infer from `Other lesion` alone:
- nodule;
- mass;
- opacity;
- consolidation;
- cavity;
- cyst;
- plaque;
- thickening;
- fibrosis;
- calcification;
- fracture;
- another named morphology.

If a radiologist, CT, MRI, or other trusted source supplies a specific characterization:
- preserve that terminology;
- preserve its modality;
- preserve the original AI `Other lesion` provenance separately.

Do not silently rewrite or delete the AI result.

---

## 8. Relationship to more-specific canonical findings

If `Other lesion` coexists with a specific positive canonical finding such as:
- Nodule/Mass;
- Lung Opacity;
- Consolidation;
- Atelectasis;
- Calcification;
- Pleural thickening;
- ILD;
- Pulmonary fibrosis;
- another mapped finding;

preserve every upstream AI result.

### No proven correspondence

If localization/identity correspondence is not established:
- do NOT assume they describe the same lesion;
- do NOT emit overlap as certainty.

### Proven/plausible same abnormality

If bounding-box correspondence plus trusted characterization, or another sufficiently specific evidence source, supports that they represent the same abnormality:
- preserve both upstream labels;
- let the specific finding provide better morphology;
- emit `OVERLAPPING_FINDING_EVIDENCE` when appropriate;
- do not count the generic and specific label as two independent disease-confirming evidences.

This is `MEDVISION_SYSTEM_POLICY`.

---

## 9. Different regions must stay separate

Example:

```text
Other lesion bbox: right upper chest
Nodule/Mass: left lower lung
```

Hermes must:
- preserve both;
- keep them distinct;
- not force semantic overlap;
- not merge evidence.

Image-plane regions alone may still be imperfect anatomical localization, but clearly noncorresponding detections must not be merged.

---

## 10. Later radiologist / CT characterization

Example:

```text
AI:
Other lesion POSITIVE

Radiologist:
specific abnormality X

CT:
specific morphology Y
```

### Hermes behavior

Preserve:

```yaml
upstream_ai:
  finding: Other lesion

specific_characterization:
  source: radiologist_or_ct
  morphology: X_or_Y
```

Do NOT:
- erase `Other lesion`;
- claim the AI originally detected X/Y;
- create a new canonical AI result that was not present.

If the characterized abnormality is outside the 14-class taxonomy:
- record the external characterization;
- do not invent a new finding skill or mapping.

If the characterization corresponds to an existing 14-class finding but that canonical AI class was not POSITIVE:
- record it as human/CT evidence;
- do not violate the frozen selector contract by auto-selecting that finding skill.

---

## 11. Multiple Other lesion detections

### S2

Competition metadata can contain multiple objects per image.

### Hermes behavior

If there are multiple `Other lesion` detections:

```text
Other lesion bbox A
Other lesion bbox B
...
```

the selector still selects:

`medvision-other-lesion`

once.

But the skill must preserve each detection as a separate evidence object unless evidence establishes that they are duplicate annotations of the same abnormality.

Suggested structure:

```yaml
detections:
  - detection_id: 1
    bbox: ...
    score: ...
  - detection_id: 2
    bbox: ...
    score: ...
```

Do not collapse distinct detections into one lesion.

---

## 12. AI output is not final diagnosis

### S4

The deployed VinDr-CXR pipeline returned:
- probability that a CXR was abnormal; and
- locations of lesion classes.

The clinical-deployment study evaluated performance against radiology reports and framed CAD as support/second opinion rather than autonomous definitive diagnosis.

### Hermes behavior

Treat `Other lesion` as machine-generated image evidence.

Doctor/radiologist review remains required.

Do not infer clinical diagnosis solely because:
- the detector is positive;
- the model score is high;
- the bbox is large.

---

## 13. Disease guardrails

Never infer from `Other lesion` alone:
- malignancy;
- lung tumor;
- infection;
- pneumonia;
- tuberculosis;
- benignity;
- severity;
- acuity;
- chronicity.

If independent clinical/imaging/pathology evidence supports a disease hypothesis:
- keep the disease hypothesis separate from the original local finding.

---

## 14. AI score interpretation

The AI score is not automatically:
- probability of cancer;
- probability of tumor;
- probability of serious disease;
- probability of a particular morphology;
- severity.

Never convert:

```text
score = 0.93
```

into:

```text
93% probability of cancer
```

or another patient-level disease probability.

Keep:

```text
image_model_score
unspecified_local_finding
specific_characterization
disease_hypotheses
uncertainty
```

separate.

---

## 15. Conflict detection

Examples:
- AI says `Other lesion`, while trusted radiologist review explicitly reports no corresponding abnormality;
- later CT shows no corresponding lesion in the marked region.

Emit:

`EVIDENCE_CONFLICT`

Preserve both sources.

Do not silently prefer AI.

If later imaging characterizes an actual abnormality differently, this may be refinement/characterization rather than conflict.

Do not label every refinement as contradiction.

---

## 16. Missing evidence

Potential missing fields:
- true anatomical compartment;
- named morphology;
- relation to any other positive finding;
- radiologist interpretation;
- cross-sectional imaging;
- prior imaging;
- disease-specific clinical context.

Missing data is not negative evidence.

It is acceptable for final structured reasoning to retain:

```text
morphology: unknown
anatomical_structure: unknown
etiology: unknown
```

---

## 17. Safety policy

`Other lesion` alone is not automatically an emergency.

If independent clinical evidence establishes:
- severe respiratory distress;
- hemodynamic instability;
- another acute high-risk syndrome;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not autonomously order:
- CT/MRI/PET;
- biopsy;
- bronchoscopy;
- surgery;
- antimicrobial treatment;
- oncologic treatment;
- another procedure/therapy.

---

## 18. Recommended structured output

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
  priority: routine|elevated|high
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true

citations: []
```

---

## 19. Prohibited inferences

Hermes MUST NOT:

1. Equate `Other lesion` with `Other diseases`.
2. Equate `Other lesion` with cancer.
3. Equate `Other lesion` with tumor.
4. Equate `Other lesion` with Nodule/Mass.
5. Equate `Other lesion` with infection/pneumonia.
6. Equate `Other lesion` with tuberculosis.
7. Infer a specific morphology from the generic label.
8. Infer a specific anatomical compartment from the generic label or bbox alone.
9. Reverse-map `Other lesion` automatically to omitted VinDr local classes.
10. Assume `Other lesion` and another positive finding are the same abnormality without correspondence evidence.
11. Count generic + specific labels as independent disease evidence when they are shown to represent the same abnormality.
12. Merge clearly separate detections.
13. Delete the upstream label after later characterization.
14. Claim the AI predicted a morphology supplied only by radiologist/CT.
15. Auto-select another finding skill merely because human/CT characterization resembles that finding.
16. Convert AI score into disease probability/severity.
17. Treat missing characterization as a negative finding.
18. Issue autonomous imaging/procedure/treatment orders.
19. Present the generic label as a final diagnosis.
20. Add unsourced differential rules.

---

## 20. Evidence gaps for v2

Potential additions:
- explicit bounding-box matching across finding classes;
- detector-level duplicate suppression provenance;
- taxonomy bridge for non-14-class human findings;
- structured extraction from radiologist free-text;
- longitudinal lesion matching;
- exact handling of original 22-class vs competition 14-class transformations if an official mapping specification becomes available.

Do not invent these rules in v1.

---

## 21. Bottom line

```text
Other lesion AI positive
        ↓
preserve each local detection + bbox + score
        ↓
UNSPECIFIED_LOCAL_FINDING
        ↓
do we have trustworthy specific characterization?
├─ no  → morphology / anatomy / etiology remain unknown
└─ yes → preserve characterization separately
        ↓
does another finding refer to same abnormality?
├─ unknown → keep separate
└─ supported → OVERLAPPING_FINDING_EVIDENCE; no double count
        ↓
do not invent cancer / tumor / infection / omitted taxonomy class
        ↓
preserve conflict and uncertainty
        ↓
doctor review required
```
