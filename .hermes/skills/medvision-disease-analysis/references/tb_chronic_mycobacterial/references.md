# references.md — Tuberculosis / Chronic Mycobacterial Thoracic Infection v1

## S1 — WHO Consolidated Guidelines on Tuberculosis, Module 3: Diagnosis (2025)

World Health Organization.  
**WHO consolidated guidelines on tuberculosis: module 3: diagnosis.**  
Geneva: WHO; 16 April 2025.  
ISBN: 978-92-4-010798-4  
URL: https://www.who.int/publications/i/item/9789240107984

### Used for
- Current WHO diagnostic framework integrating TB infection, TB disease, and drug-resistance detection.
- WHO-recommended molecular tests as initial diagnostic tests for pulmonary and selected extrapulmonary TB.
- Low-complexity automated NAATs on pleural tissue/fluid and other extrapulmonary specimens in people with signs/symptoms of extrapulmonary TB.
- Disease diagnosis requires disease-directed evaluation; tests for infection and tests for active disease are not interchangeable.

### Scope constraint
MedVision does not autonomously order diagnostic testing, isolation, treatment, or drug-resistance therapy.

---

## S2 — WHO Operational Handbook on Tuberculosis, Module 3: Diagnosis (2025)

World Health Organization.  
**WHO operational handbook on tuberculosis: module 3: diagnosis.**  
Geneva: WHO; 5 August 2025.  
ISBN: 978-92-4-011099-1  
URL: https://www.who.int/publications/i/item/9789240110991

### Used for
- Implementation context for respiratory and non-respiratory TB diagnostics.
- Interpretation of discordant diagnostic results.
- Current diagnostic technology framework.

---

## S3 — WHO TB Knowledge Sharing: testing for TB infection

World Health Organization.  
**Testing for TB infection / IGRA and TST guidance.**  
URL: https://tbksp.who.int/en/node/633

### Used for
- TST/IGRA detect immune sensitization to M. tuberculosis antigens.
- A TB-infection test alone cannot distinguish TB infection from TB disease.
- Active disease requires separate clinical/imaging/microbiological evaluation.

---

## S4 — CDC Clinical and Laboratory Diagnosis for Tuberculosis

Centers for Disease Control and Prevention.  
**Clinical and Laboratory Diagnosis for Tuberculosis.**  
URL: https://www.cdc.gov/tb/hcp/testing-diagnosis/clinical-and-laboratory-diagnosis.html

### Used for
- AFB smear is rapid but AFB are not specific for M. tuberculosis.
- Negative AFB smears do not exclude TB disease.
- Molecular/NAA testing rapidly detects M. tuberculosis nucleic acid.
- CXR abnormalities may suggest TB but cannot definitively diagnose it.
- TB blood/skin tests are infection tests and may be negative in some people with TB disease.

---

## S5 — ATS/CDC/IDSA Clinical Practice Guideline: Diagnosis of TB (2017)

Lewinsohn DM, Leonard MK, LoBue PA, et al.  
**Official ATS/IDSA/CDC Clinical Practice Guidelines: Diagnosis of Tuberculosis in Adults and Children.**  
Clin Infect Dis. 2017;64(2):e1-e33.  
DOI: 10.1093/cid/ciw694  
URL: https://www.idsociety.org/practice-guideline/diagnosis-of-tb-in-adults-and-children/

### Used for
- TST/IGRA cannot be used to exclude active TB in a patient with suspected TB.
- AFB smear negative does not exclude pulmonary TB.
- Extrapulmonary AFB smear, culture, NAAT, and histology require clinical-context interpretation.
- Negative smear/culture/NAAT from extrapulmonary sites cannot universally exclude TB because false negatives occur.
- Pleural/peritoneal ADA and free IFN-gamma are supportive, not definitive, evidence.

---

## S6 — British Thoracic Society Pleural Disease Guideline (2023)

Roberts ME, Rahman NM, Maskell NA, et al.  
**British Thoracic Society Guideline for pleural disease.**  
Thorax. 2023;78(Suppl 3):s1-s42.  
URL: https://thorax.bmj.com/content/78/Suppl_3/s1

### Used for
- Pleural ADA and/or IFN-gamma can support tuberculous pleural-effusion evaluation in appropriate prevalence contexts.
- ADA alone is not a universally definitive TB diagnosis.
- Tissue sampling for culture/sensitivity is preferred in suspected tuberculous pleural effusion.
- Pleural TB reasoning must integrate epidemiology, imaging, fluid/tissue and microbiology.

### Scope constraint
No autonomous thoracentesis, biopsy, or treatment logic is encoded.

---

## S7 — ATS/ERS/ESCMID/IDSA NTM Pulmonary Disease Guideline (2020)

Daley CL, Iaccarino JM Jr, Lange C, et al.  
**Treatment of Nontuberculous Mycobacterial Pulmonary Disease: An Official ATS/ERS/ESCMID/IDSA Clinical Practice Guideline.**  
Clin Infect Dis. 2020;71(4):e1-e36.  
DOI: 10.1093/cid/ciaa241  
URL: https://www.idsociety.org/practice-guideline/nontuberculous-mycobacterial-ntm-diseases/

### Used for
- NTM pulmonary disease requires integration of clinical, radiographic, and microbiologic criteria.
- Environmental contamination/colonization is possible.
- A single positive sputum NTM culture does not automatically establish NTM pulmonary disease.
- The same NTM species generally must be recovered from at least two sputum cultures for the standard sputum-culture criterion, or other specified microbiologic criteria must be met.

### Scope constraint
This module does not recommend NTM treatment.

---

# MedVision system-policy labels

Internal labels:

```text
PULMONARY_TB_CONCERN_SUPPORTED
PULMONARY_TB_CONCERN_INDETERMINATE
PULMONARY_TB_NOT_ESTABLISHED

PLEURAL_TB_CONCERN_SUPPORTED
PLEURAL_TB_CONCERN_INDETERMINATE
PLEURAL_TB_NOT_ESTABLISHED

MICROBIOLOGICALLY_CONFIRMED_TB
PATHOLOGY_SUPPORTED_TB
TB_ACTIVITY_UNRESOLVED
TB_SITE_UNRESOLVED

AFB_DETECTED_SPECIES_UNRESOLVED

NTM_PULMONARY_DISEASE_CONCERN_SUPPORTED
NTM_PULMONARY_DISEASE_NOT_ESTABLISHED

CHRONIC_THORACIC_INFECTION_CONCERN_SUPPORTED
CHRONIC_INFECTION_ETIOLOGY_UNRESOLVED
```

These are MedVision system-policy states, not formal WHO/ATS diagnostic categories.
