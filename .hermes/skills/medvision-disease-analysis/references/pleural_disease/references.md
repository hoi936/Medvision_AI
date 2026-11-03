# references.md — Pleural Disease / Pleural Malignancy Concern v1

## S1 — British Thoracic Society Guideline for Pleural Disease (2023)

Roberts ME, Rahman NM, Maskell NA, et al.  
**British Thoracic Society Guideline for pleural disease.**  
Thorax. 2023;78(Suppl 3):s1-s42.  
URL: https://thorax.bmj.com/content/78/Suppl_3/s1

### Used for
- Adult undiagnosed unilateral pleural effusion.
- Pleural infection and pleural malignancy diagnostic reasoning.
- Imaging must be interpreted with clinical history and pleural-fluid characteristics.
- CT can support pleural malignancy, but a negative CT does not exclude malignancy.
- Pleural-fluid cytology is an initial test for suspected secondary pleural malignancy; negative cytology does not exclude malignancy.
- Pleural-fluid biomarkers should not be used alone to diagnose secondary pleural malignancy.
- Imaging features of infection and malignancy overlap.
- Pleural infection may show lentiform fluid, visceral pleural thickening/split-pleura sign, extrapleural fat changes, and consolidation, but these findings have limited sensitivity.
- Pleural thickening plus unexplained unilateral effusion can warrant continued diagnostic concern when no clear diagnosis is established.

### Scope constraint
MedVision does not autonomously recommend thoracentesis, biopsy, PET-CT, pleurodesis, IPC, surgery, antibiotics, or other treatment.

---

## S2 — ESMO Malignant Pleural Mesothelioma Guideline (2022 publication; 2021 approval)

Popat S, Baas P, Faivre-Finn C, et al.  
**Malignant pleural mesothelioma: ESMO Clinical Practice Guidelines for diagnosis, treatment and follow-up.**  
Ann Oncol. 2022;33(2):129-142.  
DOI: 10.1016/j.annonc.2021.11.005  
URL: https://www.annalsofoncology.org/article/S0923-7534(21)04820-1/fulltext

### Used for
- Mesothelioma diagnostic reasoning requires integration of occupational/asbestos history, CT, pleural-fluid evaluation, and usually tissue pathology with immunohistochemistry.
- Plain chest radiography lacks sufficient sensitivity/specificity for diagnosis/staging.
- Cytology can yield false-negative results and definitive mesothelioma diagnosis often requires tissue.
- Unilateral pleural thickening, with or without fluid and/or pleural plaques, can raise concern but is not itself diagnostic.
- Asbestos exposure is a risk/context factor, not a mesothelioma diagnosis.
- Pleural plaques do not establish mesothelioma.

### Scope constraint
This module does not encode treatment, staging, surgery, systemic therapy, radiotherapy, or surveillance decisions.

---

## S3 — ATS/STS/STR Malignant Pleural Effusion Guideline (2018)

Feller-Kopman DJ, Reddy CB, DeCamp MM, et al.  
**Management of Malignant Pleural Effusions. An Official ATS/STS/STR Clinical Practice Guideline.**  
Am J Respir Crit Care Med. 2018;198(7):839-849.  
DOI: 10.1164/rccm.201807-1415ST  
URL: https://www.atsjournals.org/doi/10.1164/rccm.201807-1415ST

### Used for
- Malignant pleural effusion is a disease entity requiring confirmed malignancy in pleural fluid/pleura or equivalent source evidence.
- Pleural effusion itself is not synonymous with malignant pleural effusion.
- This reference is used only for disease-definition context; treatment recommendations are outside MedVision v1.

---

## S4 — Fleischner Society Thoracic Imaging Glossary (2024)

Bankier AA, MacMahon H, Colby T, et al.  
**Fleischner Society: Glossary of Terms for Thoracic Imaging.**  
Radiology. 2024;310(2):e232558.  
PMID: 38411514  
PMCID: PMC10902601  
DOI: 10.1148/radiol.232558  
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC10902601/

### Used for
- Standard terminology for pleural effusion, pleural thickening, and pleural plaque.
- Pleural plaque is a focal fibrohyaline parietal-pleural lesion and may contain calcification.
- Pleural plaques are usually associated with prior exposure to fibrous silicates, commonly asbestos.
- Pleural thickening has multiple possible causes, including fibrosis, prior/recurrent mechanical irritation, effusion, pneumothorax, asbestos exposure, infection, metastases, lymphoma, and mesothelioma.

### Scope constraint
Imaging terminology does not establish etiology or malignancy.

---

# MedVision system-policy labels

Internal labels:

```text
PLEURAL_DISEASE_HYPOTHESIS_SUPPORTED
PLEURAL_DISEASE_HYPOTHESIS_INDETERMINATE
PLEURAL_ETIOLOGY_UNRESOLVED

PLEURAL_MALIGNANCY_CONCERN_SUPPORTED
PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE
PLEURAL_MALIGNANCY_CONCERN_CONFLICTED
PLEURAL_MALIGNANCY_NOT_ESTABLISHED

MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED
CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION
PATHOLOGY_CONFIRMED_PLEURAL_MALIGNANCY

MESOTHELIOMA_CONCERN_SUPPORTED
MESOTHELIOMA_NOT_ESTABLISHED
PATHOLOGY_CONFIRMED_MESOTHELIOMA

PLEURAL_INFECTION_CONCERN_SUPPORTED
PLEURAL_INFECTION_NOT_ESTABLISHED

ASBESTOS_RELATED_PLEURAL_DISEASE_CONCERN
```

These are MedVision system-policy states, not formal guideline terminology.
