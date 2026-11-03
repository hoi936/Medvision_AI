# references.md — Calcification

## Source S1

**Title:** VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations  
**Authors:** Nguyen HQ, Lam K, Le LT, et al.  
**Journal:** Scientific Data  
**Year:** 2022  
**PMID:** 35858929  
**PMCID:** PMC9300612  
**DOI:** 10.1038/s41597-022-01498-w  
**URL:** https://pubmed.ncbi.nlm.nih.gov/35858929/  
**Evidence type:** Dataset publication  
**Primary use:** Canonical label semantics and provenance.

### Facts used
- VinDr-CXR contains 22 local labels and 6 global disease-level labels.
- `Calcification` is local label #4.
- Local labels are annotated with bounding boxes.
- Global labels reflect diagnostic impressions.

### Scope constraint
A local bounding box provides image-plane localization but does not automatically establish the anatomical compartment or etiology.

---

## Source S2

**Title:** Pulmonary Calcification and Ossification: Pathogenesis, CT Appearance, and Specific Disorders  
**Authors:** Toussie D, Azour L, Garrana S, et al.  
**Journal:** RadioGraphics  
**Year:** 2025  
**PMID:** 40338797  
**DOI:** 10.1148/rg.240110  
**URL:** https://pubmed.ncbi.nlm.nih.gov/40338797/  
**Evidence type:** Thoracic-imaging review  
**Primary use:** Pulmonary calcification vs ossification and pulmonary mechanisms.

### Facts used
- Pulmonary calcification and ossification have distinct pathogenesis, histology, and radiologic appearance.
- Pulmonary calcification may be metastatic or dystrophic.
- Metastatic pulmonary calcification is associated with systemic hypercalcemia.
- Dystrophic pulmonary calcification is associated with local lung injury and can occur with prior infection, fibrosis, or scarring.
- Pulmonary high attenuation can also occur in neoplastic and other disease contexts.

### Scope constraint
Do not assign metastatic/dystrophic mechanism unless pulmonary localization and relevant context are independently supplied.

---

## Source S3

**Title:** Chest calcifications beyond the lung parenchyma—A review  
**Authors:** Carvalho JG, Sousa J, Fernandes C, França M  
**Journal:** Radiologia (English Edition)  
**Year:** 2022  
**PMID:** 36243445  
**DOI:** 10.1016/j.rxeng.2022.06.001  
**URL:** https://pubmed.ncbi.nlm.nih.gov/36243445/  
**Evidence type:** Imaging review  
**Primary use:** Location-based extrapulmonary thoracic calcification reasoning.

### Facts used
- Thoracic calcifications occur in a wide variety of disorders.
- A location-based approach is central to differential diagnosis.
- Extrapulmonary thoracic calcifications include nodal, pleural, and other thoracic locations.
- Calcified mediastinal nodes can occur after healed granulomatous infection but have a broader differential.
- Pleural calcification can occur after chronic inflammatory processes and in asbestos-related plaque disease.

### Scope constraint
Do not convert a location-associated possibility into a definitive etiology.

---

## Source S4

**Title:** Calcified Lung Nodules: A Diagnostic Challenge in Clinical Daily Practice  
**Authors:** Baratella E, Carbi M, Minelli P, et al.  
**Journal:** Tomography  
**Year:** 2025  
**PMID:** 40137568  
**PMCID:** PMC11946818  
**DOI:** 10.3390/tomography11030028  
**URL:** https://pubmed.ncbi.nlm.nih.gov/40137568/  
**Evidence type:** Imaging review  
**Primary use:** Calcified pulmonary nodules and malignancy guardrail.

### Facts used
- Calcified lung nodules are common incidental findings.
- Calcification is often associated with benign conditions but does not inherently exclude malignancy.
- Patterns include diffuse, central, popcorn, lamellated, punctate, and eccentric.
- Pattern, distribution, clinical context, and multimodality imaging contribute to characterization.
- Malignant nodules can contain calcification.

### Scope constraint
This source applies when calcification is actually within a pulmonary nodule. Do not apply nodule rules to a generic unlocalized Calcification class.

---

## Source S5

**Title:** Fleischner Society: Glossary of Terms for Thoracic Imaging  
**Authors:** Bankier AA, MacMahon H, Colby T, et al.  
**Journal:** Radiology  
**Year:** 2024  
**PMID:** 38411514  
**PMCID:** PMC10902601  
**DOI:** 10.1148/radiol.232558  
**URL:** https://pubmed.ncbi.nlm.nih.gov/38411514/  
**Evidence type:** Thoracic-imaging terminology glossary  
**Primary use:** Standard terminology and pleural plaque context.

### Facts used
- Pleural plaque is a focal fibrohyaline lesion arising in parietal pleura.
- Pleural plaques are usually associated with previous exposure to fibrous silicates, usually asbestos.
- At imaging, pleural plaques are well-defined areas of pleural thickening and often contain calcification.

### Scope constraint
Generic `Calcification + Pleural thickening` is not enough to establish a calcified pleural plaque or asbestos exposure.

---

## Source S6

**Title:** Intrathoracic calcifications: radiographic features and differential diagnoses  
**Authors:** Brown K, Mund DF, Aberle DR, Batra P, Young DA  
**Journal:** RadioGraphics  
**Year:** 1994  
**PMID:** 7855339  
**DOI:** 10.1148/radiographics.14.6.7855339  
**URL:** https://pubmed.ncbi.nlm.nih.gov/7855339/  
**Evidence type:** Foundational thoracic-imaging review  
**Primary use:** Broad location/pattern framework.

### Facts used
- Intrathoracic calcifications can occur in pulmonary parenchyma, mediastinum, hilar/mediastinal lymph nodes, pleura, chest wall, or multiple structures.
- Location, calcification pattern, and clinical features help determine the differential.
- Calcification can be related to prior infection, neoplasm, metabolic disease, occupational exposure, or previous medical therapy.

### Scope constraint
This older source supports the broad location principle; newer S2–S5 sources take precedence for specific contemporary characterization.

---

# MedVision system-policy note

The following are **MEDVISION_SYSTEM_POLICY**, not named medical-guideline terms:

- `OVERLAPPING_FINDING_EVIDENCE`
- `EVIDENCE_CONFLICT`
- `HIGH_PRIORITY_CLINICAL_REVIEW`
- `CROSS_SECTIONAL_CALCIFICATION_CHARACTERIZATION_RELEVANT`
- preserving upstream findings while avoiding unsupported localization and double counting
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

1. S1 for dataset semantics.
2. S2 for pulmonary calcification/ossification.
3. S3 for location-based extrapulmonary reasoning.
4. S4 for calcified nodules.
5. S5 for standard terminology/pleural plaques.
6. S6 for broad historical location framework.

# Update policy

When newer evidence is added:
1. preserve location-first reasoning;
2. distinguish image-plane localization from anatomical structure;
3. distinguish calcification from ossification;
4. distinguish morphology from etiology;
5. preserve finding-vs-diagnosis separation.
