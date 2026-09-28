# NO_FINDING_REFERENCES.md

## Source S1

**Title:** VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations  
**Authors:** Nguyen HQ, Lam K, Le LT, et al.  
**Journal:** Scientific Data  
**Year:** 2022  
**PMID:** 35858929  
**PMCID:** PMC9300612  
**DOI:** 10.1038/s41597-022-01498-w  
**URL:** https://www.nature.com/articles/s41597-022-01498-w  
**Evidence type:** Dataset publication  
**Primary use:** Original label taxonomy and annotation consistency.

### Facts used

- VinDr-CXR has 22 local labels and 6 global labels.
- `No finding` is one of the 6 global labels.
- Local labels correspond to findings and are localized with bounding boxes.
- Global labels correspond to radiologist diagnostic impressions.
- VinDr Lab used automatic verification rules to prevent annotators from marking lesions while also selecting `No finding`.
- Training images were independently labeled by 3 radiologists; test images used consensus of 5 radiologists.

### Scope constraint

`No finding` is an annotation/model state, not proof that a patient has no disease.

---

## Source S2

**Title:** VinBigData Chest X-ray Abnormalities Detection — Dataset Description  
**Organization:** Vingroup Big Data Institute / Kaggle  
**Year:** 2020–2021 competition  
**URL:** https://www.kaggle.com/competitions/vinbigdata-chest-xray-abnormalities-detection/data  
**Evidence type:** Official competition specification  
**Primary use:** 14-class semantics.

### Facts used

- Class IDs 0–13 represent the 14 target radiographic findings.
- Class 14 is `No finding`.
- Official documentation states that `No finding` is intended to capture absence of all 14 findings above.
- The task is object detection and classification.
- Images may contain multiple detected objects/findings.

### Scope constraint

The competition definition supports absence of the 14 target findings, not universal exclusion of every possible thoracic disease/pathology.

---

## Source S3

**Title:** Deployment and validation of an AI system for detecting abnormal chest radiographs in clinical settings  
**Authors:** Nguyen NH, Nguyen HQ, Nguyen NT, et al.  
**Journal:** Frontiers in Digital Health  
**Year:** 2022  
**PMID:** 35966141  
**PMCID:** PMC9367219  
**DOI:** 10.3389/fdgth.2022.890759  
**URL:** https://pubmed.ncbi.nlm.nih.gov/35966141/  
**Evidence type:** Prospective clinical deployment / validation study  
**Primary use:** AI-output limitations in real clinical workflow.

### Facts used

- VinDr-CXR was deployed in a real PACS workflow and compared with radiology reports.
- The system included an abnormality classifier and lesion detector.
- Clinical-site abnormality-classifier performance was lower than retrospective/in-lab performance.
- The study frames AI CAD as support for radiologists rather than autonomous definitive diagnosis.

### Scope constraint

A positive or high-score No finding output must remain model evidence and must not be treated as final clinical truth.

---

# MedVision system-policy rules

The following are **MEDVISION_SYSTEM_POLICY**, not source terminology:

- `NO_FINDING_WITHIN_14_CLASS_TAXONOMY`
- `NO_FINDING_CONTRADICTION`
- representing `NO_FINDING_CONTRADICTION` as an `EVIDENCE_CONFLICT` subtype
- preserving all raw AI class outputs during contradiction
- not allowing No finding to suppress positive finding-skill selection
- `no_finding_status: not_established` when neither a positive No finding nor positive target finding establishes the state
- doctor review always required

---

# Source precedence

1. S2 for 14-class competition semantics.
2. S1 for original VinDr label/annotation consistency.
3. S3 for clinical AI limitations.

# Update policy

When changing this policy:

1. never add a No finding skill unless architecture is deliberately redesigned;
2. preserve raw AI provenance;
3. keep No finding bounded to the target taxonomy;
4. preserve contradiction rather than silently resolving it;
5. do not convert model confidence into probability of health or disease absence.
