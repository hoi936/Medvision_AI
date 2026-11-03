# INFILTRATION_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Infiltration** trong MedVision Hermes.

`Infiltration` là canonical VinBigData/VinDr-CXR label phải được bảo toàn cho provenance/audit, nhưng trong thuật ngữ thoracic imaging hiện đại, `infiltrate` là một từ **nonspecific, imprecise, obsolete/nonrecommended**.

Phạm vi v1:
- adult chest-radiograph reasoning;
- compatibility giữa canonical dataset label `Infiltration` và terminology hiện đại;
- tách finding khỏi disease diagnosis;
- semantic overlap với `Lung Opacity`, `Consolidation`, `Atelectasis`, và các finding cụ thể hơn;
- focal/diffuse và clinical context nếu thật sự được cung cấp;
- acute respiratory illness context chỉ khi phù hợp;
- immunocompromised context chỉ khi phù hợp;
- conflict detection, missing evidence, uncertainty, doctor review.

Skill này **không** trở thành một disease engine cho pneumonia, infection, ILD, edema, malignancy hay TB.

---

## 1. Evidence hierarchy

### S1 — Fleischner Society 2024
**Bankier AA, MacMahon H, Colby T, et al. Fleischner Society: Glossary of Terms for Thoracic Imaging. Radiology. 2024.**  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
Role: **primary terminology: infiltrate is obsolete/nonrecommended; opacity is the preferred nonspecific descriptor**

### S2 — VinDr-CXR dataset paper 2022
**Nguyen HQ, Lam K, Le LT, et al. VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations. Scientific Data. 2022.**  
PMID: 35858929  
PMCID: PMC9300612  
DOI: 10.1038/s41597-022-01498-w  
Role: **dataset semantics: `Infiltration` and `Lung opacity` are distinct local labels; disease labels are separate global labels**

### S3 — Patterson & Sponaugle 2005
**Patterson HS, Sponaugle DN. Is infiltrate a useful term in the interpretation of chest radiographs? Physician survey results. Radiology. 2005.**  
PMID: 15798161  
DOI: 10.1148/radiol.2351020759  
Role: **direct evidence that `infiltrate` is interpreted inconsistently and is nonspecific/imprecise**

### S4 — ACR Acute Respiratory Illness in Immunocompetent Patients
**American College of Radiology. ACR Appropriateness Criteria — Acute Respiratory Illness in Immunocompetent Patients. Revised 2024.**  
URL: https://acsearch.acr.org/docs/69446/Narrative/  
Role: **acute respiratory illness imaging context only**

### S5 — ACR Acute Respiratory Illness in Immunocompromised Patients
**American College of Radiology. ACR Appropriateness Criteria — Acute Respiratory Illness in Immunocompromised Patients.**  
URL: https://acsearch.acr.org/docs/69447/Narrative/  
Role: **immunocompromised acute respiratory illness context only**

### Source precedence

1. S1 for modern terminology.
2. S2 for canonical dataset-label behavior.
3. S3 for ambiguity/imprecision of the term `infiltrate`.
4. S4/S5 only within their matching clinical scenarios.

---

## 2. Core semantic rule

### S1 / S3

Modern thoracic-imaging terminology should not treat `infiltrate` as a precise radiographic diagnosis.

Fleischner 2024 describes `infiltrate` as obsolete/nonrecommended terminology historically used in relation to opacity.

Patterson & Sponaugle found wide variation in physician interpretation and concluded that `infiltrate` is a nonspecific and imprecise chest-radiograph descriptor.

### Hermes interpretation

A VinBigData `Infiltration` output is:

`LEGACY_NONSPECIFIC_RADIOGRAPHIC_LABEL`

It is NOT automatically:
- pneumonia;
- bacterial infection;
- viral infection;
- consolidation;
- interstitial lung disease;
- pulmonary edema;
- pulmonary hemorrhage;
- tuberculosis;
- lung cancer;
- any etiologic diagnosis.

---

## 3. Preserve canonical label for provenance

### S2

VinDr-CXR explicitly contains `Infiltration` and `Lung opacity` as separate local annotation labels.

### MedVision rule

Do NOT rewrite the upstream canonical label at ingestion.

Preserve:

```text
finding = "Infiltration"
```

for:
- audit;
- model provenance;
- reproducibility;
- selector behavior.

Hermes may explain that the term is legacy/nonrecommended, but must not mutate the upstream result into a different canonical class.

---

## 4. Finding != disease

### S2

VinDr-CXR separates local radiographic labels from global suspected-disease labels.

Therefore an `Infiltration` local finding is not equivalent to:
- Pneumonia;
- Tuberculosis;
- Lung tumor;
- COPD;
- another disease-level label.

### Hermes behavior

Keep:

`radiographic_finding`

separate from:

`disease_hypothesis`

Do not promote an imaging label to a final clinical diagnosis.

---

## 5. Relationship to Lung Opacity

### S1

`Opacity` is the preferred broad nonspecific descriptor.

`Infiltrate` is obsolete/nonrecommended terminology that has historically been used in overlapping ways.

### S2

Despite this terminology issue, VinDr-CXR contains both:
- `Infiltration`;
- `Lung opacity`.

### Hermes behavior

When both are positive:
- preserve both upstream model outputs;
- identify high semantic overlap;
- do not treat them as two independent disease-confirming pieces of evidence.

Emit where appropriate:

`OVERLAPPING_FINDING_EVIDENCE`

This is `MEDVISION_SYSTEM_POLICY`.

Do NOT remap the selector so that both classes resolve to one skill.

Do NOT delete one finding from the audit trail.

---

## 6. Relationship to Consolidation

`Consolidation` is a more specific imaging descriptor than the vague legacy term `infiltrate`.

### Hermes behavior

When:

`Infiltration + Consolidation`

are positive:
- preserve both;
- let Consolidation provide the more-specific morphology where appropriate;
- identify possible overlap;
- do not infer pneumonia merely from coexistence.

Do NOT count the two labels as independent confirmation of infection when they plausibly represent the same radiographic process.

---

## 7. Relationship to Atelectasis and other findings

An opacity-like legacy label may overlap spatially/semantically with more specific radiographic findings.

Potential co-findings:
- Atelectasis;
- Lung Opacity;
- Consolidation;
- ILD;
- Pulmonary fibrosis;
- Nodule/Mass;
- Pleural effusion;
- other canonical findings.

### Hermes behavior

Preserve all upstream positives.

If multiple labels plausibly describe the same radiographic region/process:
- use the more-specific finding for morphology;
- use `OVERLAPPING_FINDING_EVIDENCE`;
- avoid semantic double counting.

Do NOT infer etiology from overlap alone.

---

## 8. Infection / pneumonia guardrail

### S3

Physicians may associate `infiltrate` with pneumonia, but the term is interpreted as multiple different pathophysiologic processes and does not itself imply a single etiology.

### Hermes behavior

If fever, cough, sputum, inflammatory markers, microbiology, or clinician-documented infectious syndrome are available:
- infection/pneumonia may be evaluated as a separate hypothesis.

But:

`Infiltration -> pneumonia`

is prohibited.

Absence of fever/cough:
- may reduce support for an infection hypothesis;
- does NOT contradict the upstream `Infiltration` finding itself.

Do not infer pathogen.

---

## 9. Focal / diffuse / temporal characterization

Although `infiltrate` is imprecise, if the payload provides:
- focal vs multifocal vs diffuse;
- unilateral vs bilateral;
- lobe/zone;
- acute/subacute/chronic context;

record those values exactly as supplied.

Do not invent distribution or chronology.

Distribution and time course may guide which more-specific reasoning layer becomes relevant, but do not establish etiology alone.

---

## 10. Acute respiratory illness context — immunocompetent

### S4

ACR 2024 structures imaging appropriateness for acute respiratory illness according to:
- physical examination;
- vital signs;
- risk factors;
- initial imaging;
- the clinical question.

### Hermes behavior

Only use S4 when the case actually represents acute respiratory illness in an immunocompetent adult.

Do NOT create a universal rule:

`Infiltration -> CT`

or:

`Infiltration -> pneumonia`

Do not autonomously order imaging.

---

## 11. Acute respiratory illness context — immunocompromised

### S5

ACR addresses separate imaging scenarios in immunocompromised patients.

For example:
- when initial CXR is normal/equivocal/nonspecific, CT chest without IV contrast is rated Usually Appropriate as next imaging;
- when CXR shows multiple/diffuse/confluent opacities, CT chest without IV contrast is rated Usually Appropriate as next imaging.

### Hermes behavior

Only apply this reasoning when:
- immunocompromised status is actually supplied; and
- the case matches the relevant acute respiratory illness scenario.

Then Hermes may identify:

`CT_CHARACTERIZATION_RELEVANT`

as a clinician-facing evaluation consideration.

Do NOT autonomously order CT.

Do NOT generalize the immunocompromised pathway to all patients with `Infiltration`.

---

## 12. Triple-overlap example

When:

```text
Infiltration POSITIVE
Lung Opacity POSITIVE
Consolidation POSITIVE
```

Hermes should preserve all three upstream outputs.

Possible reasoning:

```text
Infiltration = legacy nonspecific label
Lung Opacity = broad nonspecific modern descriptor
Consolidation = more-specific pattern
```

If the findings plausibly refer to the same region/process:

emit:

`OVERLAPPING_FINDING_EVIDENCE`

and do not triple-count the evidence.

This is `MEDVISION_SYSTEM_POLICY`.

Do NOT infer:

`three positive labels -> stronger proof of pneumonia`

without independent clinical evidence.

---

## 13. Supporting evidence model

### IMAGE_EVIDENCE
- AI `Infiltration`;
- model score;
- localization/bounding box if supplied;
- focal/diffuse pattern if supplied;
- radiologist/manual interpretation;
- prior imaging if available.

### MORE_SPECIFIC_IMAGE_EVIDENCE
Potentially relevant:
- Lung Opacity;
- Consolidation;
- Atelectasis;
- ILD;
- Pulmonary fibrosis;
- Nodule/Mass;
- CT morphology.

### CLINICAL_EVIDENCE
Potentially relevant:
- fever;
- cough/sputum;
- dyspnea;
- hypoxemia;
- immune status;
- symptom duration;
- disease-specific clinical/lab context.

These modify disease hypotheses but do not redefine the upstream label.

---

## 14. Conflict detection

If AI reports `Infiltration` but:
- trusted human CXR review explicitly reports no corresponding abnormality; or
- later definitive imaging indicates no corresponding lesion/process;

emit:

`EVIDENCE_CONFLICT`

Preserve both sources.

Do not silently prefer AI.

---

## 15. Missing evidence

Potential missing fields:
- localization;
- focal vs diffuse;
- time course;
- more-specific co-findings;
- clinical symptoms;
- immune status;
- radiologist interpretation;
- CT characterization when clinically relevant;
- physiologic stability.

Missing data is not negative evidence.

---

## 16. Safety policy

`Infiltration` itself is not automatically an emergency.

If independent case data show:
- severe respiratory distress;
- significant hypoxemia;
- physiological instability;
- another acute high-risk syndrome;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

This is `MEDVISION_SYSTEM_POLICY`.

Do not autonomously prescribe:
- antibiotics;
- antivirals;
- steroids;
- diuretics;
- CT;
- bronchoscopy;
- biopsy;
- other treatment/procedure.

---

## 17. AI score interpretation

The model score is not automatically:
- probability of pneumonia;
- probability of infection;
- probability of ILD;
- probability of malignancy;
- disease severity;
- treatment urgency.

Keep separate:

```text
image_model_score
legacy_radiographic_label
more_specific_imaging_evidence
disease_hypotheses
overlap_flags
uncertainty
```

Never convert `0.84` into:
- “84% probability of pneumonia”;
- “84% probability of infection”;
- another patient-level disease probability.

---

## 18. Recommended structured output

```yaml
finding: infiltration
finding_type: legacy_nonspecific_radiographic_label

image_evidence:
  model_score: null
  localization: unknown
  distribution: unknown
  focality: unknown
  radiologist_interpretation: unknown

terminology:
  preferred_modern_descriptor: opacity_like
  canonical_label_preserved: true
  legacy_term_note: true

specific_pattern_context:
  lung_opacity: unknown
  consolidation: unknown
  atelectasis: unknown
  ild_or_fibrosis: unknown
  nodule_mass: unknown
  other: []

overlap:
  detected: false
  flags: []
  notes: []

clinical_context:
  acute_respiratory_illness: unknown
  immunocompromised: unknown
  infection_hypothesis: unknown

ct_characterization:
  available: false
  morphology: unknown

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

1. Equate `Infiltration` with pneumonia.
2. Equate `Infiltration` with infection.
3. Equate `Infiltration` with Consolidation.
4. Equate `Infiltration` with ILD.
5. Equate `Infiltration` with pulmonary edema.
6. Equate `Infiltration` with lung cancer.
7. Treat `Infiltration + Lung Opacity` as two independent disease-confirming evidences by default.
8. Treat `Infiltration + Lung Opacity + Consolidation` as triple independent proof of disease.
9. Delete or rename the canonical upstream label in the audit trail.
10. Infer etiology from focal/diffuse distribution alone.
11. Apply immunocompromised imaging rules to an immunocompetent/unknown patient.
12. Automatically recommend CT for every Infiltration finding.
13. Convert AI score into underlying-disease probability.
14. Treat missing data as negative evidence.
15. Issue autonomous imaging/procedure/treatment orders.
16. Present the finding as a final physician diagnosis.
17. Add unsourced disease-specific rules.

---

## 20. Evidence gaps for v2

Potential additions:
- explicit bbox-overlap matching with Lung Opacity/Consolidation;
- quantitative evidence de-duplication;
- projection/technical artifact handling;
- longitudinal change semantics;
- dedicated pneumonia/infection skill interaction;
- pediatric terminology;
- disease-specific immunocompromised pathways.

Do not invent these detailed rules in v1.

---

## 21. Bottom line

```text
Infiltration AI finding
        ↓
preserve canonical upstream label
        ↓
recognize legacy / nonspecific terminology
        ↓
look for Lung Opacity and more-specific findings
        ↓
OVERLAPPING_FINDING_EVIDENCE where appropriate
        ↓
do not double/triple count
        ↓
integrate clinical / immune / CT context
        ↓
keep disease hypotheses separate
        ↓
identify missing/conflicting evidence
        ↓
bounded assessment
        ↓
doctor review required
```
