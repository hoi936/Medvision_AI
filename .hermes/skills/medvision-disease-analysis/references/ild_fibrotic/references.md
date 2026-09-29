# references.md — ILD / Fibrotic ILD Disease Analysis v1

## S1 — ATS/ERS/JRS/ALAT IPF Update + Progressive Pulmonary Fibrosis Guideline (2022)

Raghu G, Remy-Jardin M, Richeldi L, et al.  
**Idiopathic Pulmonary Fibrosis (an Update) and Progressive Pulmonary Fibrosis in Adults: An Official ATS/ERS/JRS/ALAT Clinical Practice Guideline.**  
Am J Respir Crit Care Med. 2022;205(9):e18-e47.  
PMID: 35486072  
PMCID: PMC9851481  
DOI: 10.1164/rccm.202202-0399ST  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC9851481/

### Used for
- Current four-category HRCT framework for IPF evaluation:
  - UIP pattern
  - probable UIP pattern
  - indeterminate for UIP
  - CT findings suggestive of an alternative diagnosis
- UIP morphology is not itself equivalent to IPF.
- IPF is a chronic fibrosing interstitial pneumonia of unknown cause associated with UIP features.
- PPF definition for ILD other than IPF with radiological fibrosis:
  at least two of three domains within the past year with no alternative explanation:
  worsening respiratory symptoms, physiological progression, radiological progression.
- Physiological progression:
  - absolute FVC decline >=5% predicted within 1 year; or
  - absolute Hb-corrected DLCO decline >=10% predicted within 1 year.
- Radiological progression examples:
  increased traction bronchiectasis/bronchiolectasis, new GGO with traction bronchiectasis,
  new fine reticulation, increased/coarser reticulation, new/increased honeycombing,
  increased lobar volume loss.

### Scope constraint
PPF is not defined for IPF by this criterion set. This module encodes diagnostic/progression semantics only, not antifibrotic treatment.

---

## S2 — ATS/ERS/JRS/ALAT IPF Diagnosis Guideline (2018)

Raghu G, Remy-Jardin M, Myers JL, et al.  
**Diagnosis of Idiopathic Pulmonary Fibrosis. An Official ATS/ERS/JRS/ALAT Clinical Practice Guideline.**  
Am J Respir Crit Care Med. 2018;198(5):e44-e68.  
DOI: 10.1164/rccm.201807-1255ST  
URL: https://www.thoracic.org/statements/resources/interstitial-lung-disease/diagnosis-IPF-full-length.pdf

### Used for
- IPF requires exclusion of other known causes of ILD, including:
  environmental/occupational exposure, connective-tissue disease, and drug toxicity.
- Detailed medication/exposure history and CTD evaluation are part of diagnostic workup.
- Multidisciplinary discussion is recommended/suggested for diagnostic decision-making.
- HRCT-based diagnostic reasoning must not be replaced by chest-radiograph findings.

---

## S3 — ATS/JRS/ALAT Hypersensitivity Pneumonitis Guideline (2020)

Raghu G, Remy-Jardin M, Ryerson CJ, et al.  
**Diagnosis of Hypersensitivity Pneumonitis in Adults. An Official ATS/JRS/ALAT Clinical Practice Guideline.**  
Am J Respir Crit Care Med. 2020;202(3):e36-e69.  
PMCID: PMC7397797  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC7397797/

### Used for
- HP is divided into nonfibrotic and fibrotic phenotypes.
- HP diagnosis integrates multiple domains:
  exposure identification, HRCT pattern, BAL lymphocytosis and/or histopathology.
- No individual feature is sufficient in isolation.
- Exposure may be absent/unidentified in fibrotic HP.
- Positive serum IgG supports prior exposure/sensitization but does not prove causality or HP.
- Multidisciplinary discussion is central when confidence is incomplete.

### Scope constraint
MedVision does not autonomously recommend BAL, biopsy, or exposure challenge.

---

## S4 — ERS/EULAR CTD-ILD Clinical Practice Guideline (2026)

Antoniou KM, Distler O, Gheorghiu AM, et al.  
**ERS/EULAR clinical practice guidelines for connective tissue disease-associated interstitial lung disease.**  
Eur Respir J. 2026;67(1):2402533.  
PMID: 40907995  
DOI: 10.1183/13993003.02533-2024  
URL: https://pubmed.ncbi.nlm.nih.gov/40907995/

Parallel publication:  
Ann Rheum Dis. 2026;85(1):22-60. PMID: 40912974.

### Used for
- Current disease-specific CTD-ILD screening, diagnostic and monitoring framework.
- CTD context and ILD evidence must be integrated rather than inferred from one serology or one image sign.
- Evidence certainty is limited for multiple CTD-specific questions.

### Scope constraint
This module does not encode immunosuppressive or antifibrotic treatment recommendations.

---

## S5 — Fleischner Society Thoracic Imaging Glossary (2024)

Bankier AA, MacMahon H, Colby T, et al.  
**Fleischner Society: Glossary of Terms for Thoracic Imaging.**  
Radiology. 2024;310(2):e232558.  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC10902601/

### Used for
- Standard thoracic imaging terminology.
- HRCT morphologic terms such as honeycombing, traction bronchiectasis, reticulation and ground-glass opacity remain imaging descriptors.
- Imaging morphology should not silently become disease etiology.

---

# MedVision system-policy labels

Internal labels:

```text
ILD_HYPOTHESIS_SUPPORTED
FIBROTIC_ILD_HYPOTHESIS_SUPPORTED
ILD_HYPOTHESIS_INDETERMINATE
ILD_HYPOTHESIS_CONFLICTED
ILD_HYPOTHESIS_NOT_ESTABLISHED

HRCT_PATTERN_UIP
HRCT_PATTERN_PROBABLE_UIP
HRCT_PATTERN_INDETERMINATE_FOR_UIP
HRCT_PATTERN_ALTERNATIVE_DIAGNOSIS
HRCT_PATTERN_NOT_ASSESSABLE

IPF_CONCERN_SUPPORTED
IPF_NOT_ESTABLISHED
ILD_ETIOLOGY_UNRESOLVED

FIBROTIC_HP_CONCERN_SUPPORTED
CTD_ILD_CONCERN_SUPPORTED

PPF_CRITERIA_MET
PPF_CRITERIA_NOT_MET
PPF_NOT_ASSESSABLE
```

These labels are MedVision system policy, not formal source wording.
