# references.md — Pulmonary Fibrosis

## Source S1

**Title:** Fleischner Society: Glossary of Terms for Thoracic Imaging  
**Authors:** Bankier AA, MacMahon H, Colby T, et al.  
**Journal:** Radiology  
**Year:** 2024  
**PMID:** 38411514  
**PMCID:** PMC10902601  
**DOI:** 10.1148/radiol.232558  
**URL:** https://pubmed.ncbi.nlm.nih.gov/38411514/  
**Evidence type:** Thoracic-imaging terminology glossary  
**Primary use:** Fibrosis-related CT terminology.

### Facts used
- Standardized thoracic CT terminology includes fibrosis-related descriptors such as honeycombing and traction-related airway abnormalities.
- CT morphology must not be inferred from a generic CXR classifier output.
- Honeycombing is a fibrosis-related structural descriptor requiring appropriate imaging context.

---

## Source S2

**Title:** VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations  
**Authors:** Nguyen HQ, Lam K, Le LT, et al.  
**Journal:** Scientific Data  
**Year:** 2022  
**PMID:** 35858929  
**PMCID:** PMC9300612  
**DOI:** 10.1038/s41597-022-01498-w  
**URL:** https://pubmed.ncbi.nlm.nih.gov/35858929/  
**Evidence type:** Dataset publication  
**Primary use:** Canonical-label provenance and finding-vs-diagnosis separation.

### Facts used
- VinDr-CXR contains 22 local labels and 6 global disease-level labels.
- `Interstitial lung disease (ILD)` is a local label.
- `Pulmonary fibrosis` is a distinct local label.
- Local labels are localized findings; global labels reflect diagnostic impressions.

### Scope constraint
Dataset taxonomy does not establish etiologic independence or imply that separate local labels are independent disease evidence.

---

## Source S3

**Title:** Idiopathic Pulmonary Fibrosis (an Update) and Progressive Pulmonary Fibrosis in Adults: An Official ATS/ERS/JRS/ALAT Clinical Practice Guideline  
**Authors:** Raghu G, Remy-Jardin M, Richeldi L, et al.  
**Journal:** American Journal of Respiratory and Critical Care Medicine  
**Year:** 2022  
**PMID:** 35486072  
**PMCID:** PMC9851481  
**DOI:** 10.1164/rccm.202202-0399ST  
**URL:** https://pubmed.ncbi.nlm.nih.gov/35486072/  
**Evidence type:** Official clinical practice guideline  
**Primary use:** UIP/IPF separation and PPF criteria.

### Facts used
- IPF evaluation uses radiological/histopathological criteria in clinical context.
- UIP/probable-UIP are imaging-pattern categories used in IPF evaluation.
- In ILD other than IPF with radiological pulmonary fibrosis, PPF requires at least 2 of 3 domains within the past year with no alternative explanation:
  1. worsening respiratory symptoms;
  2. physiological progression;
  3. radiological progression.
- Accepted physiological progression includes an absolute FVC decline >=5% predicted within 1 year or absolute DLCO decline >=10% predicted within 1 year.
- Radiological progression can include increased traction bronchiectasis/bronchiolectasis, new GGO with traction bronchiectasis, new fine reticulation, increased/coarser reticulation, new/increased honeycombing, or increased lobar volume loss.

### Scope constraint
This finding skill does not autonomously implement treatment recommendations.

---

## Source S4

**Title:** High-Resolution Computed Tomography of Fibrotic Interstitial Lung Disease  
**Authors:** Rodriguez K, Ashby CL, Varela VR, Sharma A  
**Journal:** Seminars in Respiratory and Critical Care Medicine  
**Year:** 2022  
**PMID:** 36307108  
**DOI:** 10.1055/s-0042-1755563  
**URL:** https://pubmed.ncbi.nlm.nih.gov/36307108/  
**Evidence type:** Thoracic-imaging review  
**Primary use:** HRCT morphology and multidisciplinary characterization.

### Facts used
- HRCT provides detailed assessment of lung parenchyma/interstitium beyond radiography.
- Fibrotic ILD HRCT features include:
  - reticulation;
  - traction bronchiectasis/bronchiolectasis;
  - honeycombing;
  - architectural distortion;
  - volume loss.
- Characterization and distribution form distinctive CT patterns.
- CT pattern and progression are integrated with clinical, serologic and pathologic data in multidisciplinary diagnosis.

---

## Source S5

**Title:** Imaging in the diagnosis and management of fibrosing interstitial lung diseases  
**Authors:** Lederer C, Storman M, Tarnoki AD, Tarnoki DL, Margaritopoulos GA, Prosch H  
**Journal:** Breathe (Sheffield)  
**Year:** 2024  
**PMID:** 38746908  
**PMCID:** PMC11091715  
**DOI:** 10.1183/20734735.0006-2024  
**URL:** https://pubmed.ncbi.nlm.nih.gov/38746908/  
**Evidence type:** Imaging review  
**Primary use:** HRCT fibrosis signs and clinical-context dependence.

### Facts used
- HRCT plays a pivotal role in fibrosing ILD diagnosis/management.
- Fibrosis signs include honeycombing, traction bronchiectasis and lung volume loss; reticulation and GGO contribute to pattern analysis.
- Pattern interpretation depends strongly on clinical context.
- Different fibrosing ILDs can share fibrosis-related imaging features.

### Scope constraint
Do not convert a fibrosis sign into a specific etiology without the corresponding clinical context.

---

## Source S6

**Title:** Update of the international multidisciplinary classification of the interstitial pneumonias: an ERS/ATS statement  
**Authors:** Ryerson CJ, Adegunsoye A, Piciucchi S, et al.  
**Journal:** European Respiratory Journal  
**Year:** 2025  
**PMID:** 40774805  
**DOI:** 10.1183/13993003.00158-2025  
**URL:** https://pubmed.ncbi.nlm.nih.gov/40774805/  
**Evidence type:** ERS/ATS official statement / consensus classification  
**Primary use:** Fibrotic/non-fibrotic classification and diagnostic confidence.

### Facts used
- Classification now includes idiopathic and secondary causes.
- Interstitial disorders are subclassified as fibrotic versus non-fibrotic.
- Diagnostic confidence is explicitly considered.
- Classification remains multidisciplinary.

### Scope constraint
A generic CXR fibrosis label is not sufficient to identify an ILD subtype or cause.

---

# MedVision system-policy note

The following are **MEDVISION_SYSTEM_POLICY**, not medical-guideline terms:

- `OVERLAPPING_FINDING_EVIDENCE`
- `EVIDENCE_CONFLICT`
- `HIGH_PRIORITY_CLINICAL_REVIEW`
- preserving every positive upstream classifier result while avoiding semantic double/triple counting
- clinician review always required

---

# Citation policy

Every medical/terminology rule added to `SKILL.md` must be traceable to:
- `[S1]`
- `[S2]`
- `[S3]`
- `[S4]`
- `[S5]`
- `[S6]`

If no source supports a proposed medical rule:
- do not add it as medical fact;
- mark `EVIDENCE_GAP`;
- or label it `MEDVISION_SYSTEM_POLICY`.

# Source precedence

1. S3 for UIP/IPF and PPF.
2. S6 for current classification.
3. S4/S5 for HRCT fibrosis characterization.
4. S1 for terminology.
5. S2 for dataset provenance.

# Update policy

When newer evidence is added:
1. preserve CXR-vs-HRCT separation;
2. preserve finding-vs-disease separation;
3. preserve fibrosis-vs-IPF/UIP distinction;
4. preserve longitudinal criteria for PPF;
5. preserve overlap/de-duplication with ILD and broad opacity labels.
