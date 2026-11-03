# references.md — Longitudinal / Temporal Reasoning v1

## S1 — RSNA Quality Improvement: Comparison to Prior Relevant Imaging Studies

Gilman MD, Kazerooni EA.  
**Utilization of Comparison to Prior Relevant Imaging Studies.**  
Radiological Society of North America quality-improvement resource.  
URL: https://www.rsna.org/uploadedfiles/rsna/content/science_and_education/quality/utilization%20of%20comparison%20to%20prior%20relevant%20imaging%20studies.pdf

### Used for
- Comparison with prior relevant imaging is a core part of interpreting interval change.
- Reports should document the comparison study date/type when relevant and whether interval change is present.
- Longitudinal interpretation depends on actual prior studies, not assumed history.

---

## S2 — Fleischner Society Pulmonary Nodule Guideline (2017)

MacMahon H, Naidich DP, Goo JM, et al.  
**Guidelines for Management of Incidental Pulmonary Nodules Detected on CT Images: From the Fleischner Society 2017.**  
Radiology. 2017;284(1):228-243.  
PMID: 28240562  
DOI: 10.1148/radiol.2017161659  
URL: https://pubmed.ncbi.nlm.nih.gov/28240562/

### Used for
- Prior imaging should be reviewed when available to assess possible nodule growth or stability.
- Differences in scanning technique can make longitudinal comparison less accurate.
- Nodule-growth assessment requires true lesion correspondence and comparable imaging.
- Volumetric growth assessment is sensitive to software/technical differences.

### Scope constraint
This source applies to incidental pulmonary nodules on CT. MedVision uses the comparison principles across its temporal layer but does not apply Fleischner management tables outside their scope.

---

## S3 — ATS/ERS/JRS/ALAT IPF/PPF Guideline (2022)

Raghu G, Remy-Jardin M, Richeldi L, et al.  
**Idiopathic Pulmonary Fibrosis (an Update) and Progressive Pulmonary Fibrosis in Adults.**  
Am J Respir Crit Care Med. 2022;205(9):e18-e47.  
PMID: 35486072  
PMCID: PMC9851481  
DOI: 10.1164/rccm.202202-0399ST  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC9851481/

### Used for
- Progression requires longitudinal comparison rather than severity on a single study.
- PPF requires at least 2 of 3 progression domains within the past year, with no alternative explanation.
- Radiologic progression is assessed by comparing baseline and follow-up HRCT.
- Physiologic progression requires actual serial FVC/DLCO values with timing and attribution.

### Scope constraint
PPF-specific thresholds remain owned by the existing ILD/Fibrotic-ILD module.

---

## S4 — Existing MedVision disease-analysis modules

The following frozen modules are authoritative for disease-specific temporal semantics:

- Pneumonia/CAP
- Heart Failure/Cardiogenic Congestion
- Pulmonary Malignancy Concern
- Acute Aortic Syndrome Concern
- ILD/Fibrotic ILD/IPF/PPF
- Pleural Disease/Pleural Malignancy
- TB/Chronic Mycobacterial Infection

### Used for
- Growth/stability rules for pulmonary lesions.
- PPF longitudinal requirements.
- Residual fibrosis versus active TB.
- Recurrent/persistent pleural effusion.
- Acute versus chronic aortic findings.
- Competing acute pneumonia/HF explanations.
- Disease-specific safety boundaries.

This temporal layer does not override those modules.

---

# MedVision internal temporal states

```text
NEW
RESOLVED
IMPROVED
WORSENED
STABLE
PERSISTENT
RECURRENT

INTERVAL_CHANGE_INDETERMINATE
COMPARISON_NOT_POSSIBLE
PRIOR_DATA_MISSING
TEMPORAL_CONFLICT

CORRESPONDENCE_CONFIRMED
CORRESPONDENCE_PROBABLE
CORRESPONDENCE_UNCERTAIN
CORRESPONDENCE_NOT_SAME
CORRESPONDENCE_UNKNOWN

COMPARABLE
LIMITED_COMPARABILITY
NOT_COMPARABLE
COMPARABILITY_UNKNOWN
```

These are MedVision system-policy labels, not formal clinical guideline terminology.
