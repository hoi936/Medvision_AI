# references.md — Pulmonary Malignancy Concern / Lung Nodule Disease Analysis v1

## S1 — ACR Appropriateness Criteria 2023

**ACR Appropriateness Criteria® Incidentally Detected Indeterminate Pulmonary Nodule.** Revised 2023.  
American College of Radiology.  
URL: https://acsearch.acr.org/docs/69455/Narrative/

### Used for
- Adult indeterminate pulmonary nodule evaluation context.
- For adults >=35 with an indeterminate pulmonary nodule on chest radiograph, CT chest without IV contrast is the usual next characterization study.
- CT size/morphology and patient risk context matter.
- Suspicious morphology and upper-lobe location can increase concern in appropriate CT contexts.

### Scope constraint
This is imaging-management guidance, not a MedVision malignancy diagnosis rule. MedVision does not autonomously order CT.

---

## S2 — Fleischner Society 2017 incidental CT nodule guideline

MacMahon H, Naidich DP, Goo JM, et al.  
**Guidelines for Management of Incidental Pulmonary Nodules Detected on CT Images: From the Fleischner Society 2017.**  
Radiology. 2017;284(1):228-243.  
PMID: 28240562  
DOI: 10.1148/radiol.2017161659  
URL: https://pubmed.ncbi.nlm.nih.gov/28240562/

### Used for
- Incidental pulmonary nodules detected on CT.
- Separate reasoning for solid, subsolid, and multiple nodules.
- Management depends on nodule size/morphology and individual risk context.

### Scope constraint
These are CT-specific incidental-nodule recommendations. They must not be applied directly to a CXR AI bounding box. The guideline has population/context exclusions and does not constitute a cancer diagnosis.

---

## S3 — ACCP/CHEST pulmonary nodule guideline

Gould MK, Donington J, Lynch WR, et al.  
**Evaluation of individuals with pulmonary nodules: when is it lung cancer? Diagnosis and management of lung cancer, 3rd ed: American College of Chest Physicians evidence-based clinical practice guidelines.**  
Chest. 2013;143(5 Suppl):e93S-e120S.  
PMID: 23649456  
PMCID: PMC3749714  
DOI: 10.1378/chest.12-2351  
URL: https://pubmed.ncbi.nlm.nih.gov/23649456/

### Used for
- Pulmonary-nodule evaluation requires estimation of malignancy probability, lesion characterization, consideration of imaging/tests and risks/benefits, and patient preferences.
- Solid, small, and subsolid nodules require context-specific evaluation.

### Scope constraint
MedVision v1 does not implement an autonomous malignancy-probability calculator or management recommendation.

---

## S4 — British Thoracic Society pulmonary nodule guideline

Callister MEJ, Baldwin DR, Akram AR, et al.  
**British Thoracic Society guidelines for the investigation and management of pulmonary nodules.**  
Thorax. 2015;70(Suppl 2):ii1-ii54.  
PMID: 26082159  
DOI: 10.1136/thoraxjnl-2015-207168  
URL: https://pubmed.ncbi.nlm.nih.gov/26082159/

### Used for
- Single and multiple pulmonary nodules require structured risk/context assessment.
- CT morphology, nodule behavior over time, and clinical risk information contribute to evaluation.
- Multiple nodules are not automatically metastatic disease.

### Scope constraint
This guideline informs risk reasoning; MedVision does not autonomously execute biopsy/surgery/surveillance decisions.

---

## S5 — Fleischner Society thoracic-imaging glossary 2024

Bankier AA, MacMahon H, Colby T, et al.  
**Fleischner Society: Glossary of Terms for Thoracic Imaging.**  
Radiology. 2024;310(2):e232558.  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC10902601/

### Used for
- Standardized thoracic-imaging terminology.
- Pulmonary nodule: circumscribed focal opacity <=30 mm.
- Larger focal lesions are termed masses.
- CT morphology terminology should be preserved as imaging evidence rather than silently converted to pathology.

---

## S6 — ACR Lung-RADS v2022 (screening-specific)

**Lung-RADS® v2022.** American College of Radiology.  
URL: https://www.acr.org/-/media/ACR/Files/RADS/Lung-RADS/Lung-RADS-2022.pdf

### Used for
- Screening-specific examples of benign imaging features such as complete, central, popcorn, or concentric-ring calcification and fat-containing nodules.
- Screening categories separate lesion morphology/behavior from confirmed malignancy.
- Current Lung-RADS removed generic malignancy-percentage columns because lesion-specific risk is variable.

### Scope constraint
Lung-RADS applies to lung-cancer screening CT, not arbitrary chest radiographs or incidental nonscreening CT. Do not apply its categories outside that context.

---

# MedVision system-policy labels

The following are internal MedVision labels, not guideline terminology:

```text
PULMONARY_MALIGNANCY_CONCERN_SUPPORTED
PULMONARY_MALIGNANCY_CONCERN_INDETERMINATE
IMAGING_LESION_WITHOUT_SUFFICIENT_MALIGNANCY_CONTEXT
PULMONARY_MALIGNANCY_CONCERN_CONFLICTED
PULMONARY_MALIGNANCY_NOT_ESTABLISHED
PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY
MALIGNANCY_ORIGIN_UNRESOLVED
```

`EVIDENCE_CONFLICT`, `OVERLAPPING_FINDING_EVIDENCE`, `HIGH_PRIORITY_CLINICAL_REVIEW`, and doctor-review requirements remain existing MedVision system policy.
