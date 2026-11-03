# references.md — Other Lesion

## Source S1

**Title:** VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations  
**Authors:** Nguyen HQ, Lam K, Le LT, et al.  
**Journal:** Scientific Data  
**Year:** 2022  
**PMID:** 35858929  
**PMCID:** PMC9300612  
**DOI:** 10.1038/s41597-022-01498-w  
**URL:** https://pubmed.ncbi.nlm.nih.gov/35858929/  
**Supplementary label-definition source:** https://storage.googleapis.com/kaggle-media/competitions/VinBigData/VinDr_CXR_data_paper.pdf  
**Evidence type:** Dataset publication + supplementary label definitions  
**Primary use:** Canonical semantics.

### Facts used
- VinDr-CXR has 22 local finding labels and 6 global diagnostic-impression labels.
- Local findings are marked with bounding boxes.
- `Other lesion` is local label #22.
- `Other diseases` is a separate global label.
- The supplementary definition of `Other lesion` is: “Other lesions that are not on the list of findings or abnormalities mentioned above.”
- The dataset label list was selected by experienced radiologists and intended to cover prevalent findings that can be differentiated on CXR.

### Scope constraint
`Other lesion` is intentionally nonspecific. The source does not justify assigning a particular morphology, anatomy, disease, or etiology without additional evidence.

---

## Source S2

**Title:** VinBigData Chest X-ray Abnormalities Detection — competition data specification  
**Organization:** VinBigData / Kaggle competition  
**URL:** https://www.kaggle.com/competitions/vinbigdata-chest-xray-abnormalities-detection/data  
**Evidence type:** Official competition dataset specification  
**Primary use:** 14-class detector semantics.

### Facts used
- The competition lists 14 radiographic finding classes.
- `9 - Other lesion`.
- `14 - No finding` is intended to capture absence of all 14 findings.
- `train.csv` has one row per object with class and bounding box.
- Some images contain multiple objects.
- Metadata includes radiologist ID and bounding-box coordinates.

### Scope constraint
The competition specification does not establish that `Other lesion` deterministically corresponds to one specific omitted VinDr local class.

---

## Source S3

**Title:** Fleischner Society: Glossary of Terms for Thoracic Imaging  
**Authors:** Bankier AA, MacMahon H, Colby T, et al.  
**Journal:** Radiology  
**Year:** 2024  
**PMID:** 38411514  
**PMCID:** PMC10902601  
**DOI:** 10.1148/radiol.232558  
**URL:** https://pubmed.ncbi.nlm.nih.gov/38411514/  
**Evidence type:** Thoracic-imaging terminology glossary  
**Primary use:** Specific terminology only after morphology/location is actually supplied.

### Facts used
- The glossary promotes precise standardized thoracic-imaging terminology.
- It distinguishes descriptors, imaging diagnoses, and location/distribution terminology.
- Imaging cannot always establish exact structure of origin even when a lesion abuts pleura or another structure.

### Scope constraint
Do not use Fleischner terms to invent a specific morphology from `Other lesion`. Apply terminology only to actual supplied imaging characterization.

---

## Source S4

**Title:** Deployment and validation of an AI system for detecting abnormal chest radiographs in clinical settings  
**Authors:** Nguyen NH, Nguyen HQ, Nguyen NT, et al.  
**Journal:** Frontiers in Digital Health  
**Year:** 2022  
**PMID:** 35966141  
**PMCID:** PMC9367219  
**DOI:** 10.3389/fdgth.2022.890759  
**URL:** https://pubmed.ncbi.nlm.nih.gov/35966141/  
**Evidence type:** Prospective clinical-deployment/validation study  
**Primary use:** AI-result provenance and clinical-workflow limits.

### Facts used
- The deployed VinDr-CXR system included a lesion detector.
- The system returned abnormality probability and lesion locations.
- The clinical study compared AI results against radiology reports in a real workflow.
- CAD was framed as support/second opinion rather than autonomous final clinical diagnosis.
- Real-world performance differed from retrospective/in-lab performance.

### Scope constraint
A high detector score or localized box is not a final diagnosis.

---

# Important non-rule: omitted original VinDr labels

The original 22 local labels include:
- Clavicle fracture
- Edema
- Emphysema
- Enlarged PA
- Lung cavity
- Lung cyst
- Mediastinal shift
- Rib fracture

These are not separate classes in the 14-class competition.

**v1 does not encode an official deterministic reverse mapping from `Other lesion` to these labels.**

A third-party model paper may merge rare classes into an `Other lesion` category for its own preprocessing, but that is not sufficient to define canonical MedVision semantics.

If an official transformation specification is later obtained, it can be evaluated for v2.

---

# MedVision system-policy note

The following are **MEDVISION_SYSTEM_POLICY**, not named medical-guideline terms:

- `UNSPECIFIED_LOCAL_FINDING`
- `OVERLAPPING_FINDING_EVIDENCE`
- `EVIDENCE_CONFLICT`
- `HIGH_PRIORITY_CLINICAL_REVIEW`
- preservation of every upstream detection for provenance
- one skill selection with multiple evidence objects for multiple same-class detections
- no automatic cross-skill activation from later human/CT characterization
- clinician review always required

---

# Citation policy

Every dataset/medical/terminology rule added to `SKILL.md` must be traceable to:
- `[S1]`
- `[S2]`
- `[S3]`
- `[S4]`

If no source supports a proposed medical/taxonomy rule:
- do not add it as fact;
- mark `EVIDENCE_GAP`;
- or label it `MEDVISION_SYSTEM_POLICY`.

# Source precedence

1. S1 for original VinDr label semantics.
2. S2 for 14-class competition/object behavior.
3. S3 for actual supplied thoracic-imaging terminology.
4. S4 for AI clinical-workflow limitations.

# Update policy

When new evidence is added:
1. preserve the catch-all nature of the label;
2. preserve finding-vs-disease separation;
3. never infer morphology merely to eliminate uncertainty;
4. preserve each upstream detection;
5. distinguish later characterization from the original AI prediction.
