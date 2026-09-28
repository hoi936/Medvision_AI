# references.md — ILD

## Source S1

**Title:** Fleischner Society: Glossary of Terms for Thoracic Imaging  
**Authors:** Bankier AA, MacMahon H, Colby T, et al.  
**Journal:** Radiology  
**Year:** 2024  
**PMID:** 38411514  
**PMCID:** PMC10902601  
**DOI:** 10.1148/radiol.232558  
**URL:** https://pubmed.ncbi.nlm.nih.gov/38411514/  
**Evidence type:** Thoracic-imaging terminology review / glossary  
**Primary use:** Standardized imaging terminology.

### Facts used
- The glossary standardizes thoracic-imaging terminology.
- Fibrosis-related CT descriptors include reticular abnormalities, honeycombing and traction-related airway abnormalities.
- Ground-glass opacity and other CT morphology should remain modality-specific.
- These terms must not be invented from a generic CXR classifier result.

---

## Source S2

**Title:** Update of the international multidisciplinary classification of the interstitial pneumonias: an ERS/ATS statement  
**Authors:** Ryerson CJ, Adegunsoye A, Piciucchi S, et al.  
**Journal:** European Respiratory Journal  
**Year:** 2025  
**PMID:** 40774805  
**DOI:** 10.1183/13993003.00158-2025  
**URL:** https://pubmed.ncbi.nlm.nih.gov/40774805/  
**Evidence type:** ERS/ATS official statement / consensus classification  
**Primary use:** Current multidisciplinary classification.

### Facts used
- Classification expands beyond idiopathic interstitial pneumonias to include secondary causes.
- Interstitial disorders are subclassified as fibrotic or non-fibrotic.
- Updated/new terminology and patterns are included.
- Diagnostic confidence is explicitly considered in patient evaluation and management.
- Classification is multidisciplinary.

### Scope constraint
The statement provides a classification framework; it does not make a generic CXR `ILD` label equivalent to any specific subtype.

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
**Primary use:** IPF/UIP context and PPF definition.

### Facts used
- IPF diagnosis uses radiologic/histopathologic criteria in clinical context.
- UIP/probable-UIP and related HRCT categories are imaging-pattern concepts used in IPF evaluation.
- PPF in an ILD other than IPF is defined as at least 2 of 3 domains within the past year, with no alternative explanation:
  1. worsening respiratory symptoms;
  2. physiological progression;
  3. radiological progression.

### Scope constraint
- A CXR `ILD` class does not establish UIP or IPF.
- PPF cannot be inferred from a single image or isolated AI output.
- Treatment recommendations from this guideline are not encoded into this finding skill.

---

## Source S4

**Title:** ACR Appropriateness Criteria — Diffuse Lung Disease  
**Organization:** American College of Radiology  
**Version:** New 2021  
**URL:** https://acsearch.acr.org/docs/3157911/Narrative/  
**Evidence type:** Imaging appropriateness guideline  
**Primary use:** Suspected/confirmed diffuse-lung-disease imaging context.

### Facts used
- For suspected diffuse lung disease, chest radiography is `Usually Appropriate`.
- CT chest without IV contrast is also `Usually Appropriate`.
- In confirmed diffuse lung disease with acute deterioration, radiography and noncontrast CT have roles.
- In clinically indicated routine follow-up of confirmed diffuse lung disease, CT without IV contrast is `Usually Appropriate`.

### Scope constraint
Do not interpret this as an autonomous `ILD AI -> CT order` rule.

---

## Source S5

**Title:** Approach to the Evaluation and Management of Interstitial Lung Abnormalities: An Official American Thoracic Society Clinical Statement  
**Authors:** Podolanczuk AJ, Hunninghake GM, Wilson KC, et al.  
**Journal:** American Journal of Respiratory and Critical Care Medicine  
**Year:** 2025  
**PMID:** 40387336  
**PMCID:** PMC12264694  
**DOI:** 10.1164/rccm.202505-1054ST  
**URL:** https://pubmed.ncbi.nlm.nih.gov/40387336/  
**Evidence type:** ATS official clinical statement  
**Primary use:** ILA definition and working distinction between ILA and clinical ILD.

### Facts used
- ILA is a CT-defined concept involving nondependent bilateral parenchymal abnormalities meeting a defined extent.
- CT findings may include ground-glass opacity, reticulation, lung distortion, traction bronchiectasis and/or honeycombing.
- Clinical ILD is distinguished from ILA using additional evidence such as attributable symptoms, abnormal/declining lung function, fibrotic/progressive imaging abnormalities, or a specific fibrotic ILD pattern on imaging/pathology.

### Scope constraint
- Do not call a CXR classifier output an ATS-defined ILA.
- Do not turn one incidental CT feature into a specific ILD diagnosis.

---

# MedVision system-policy note

The following are **MEDVISION_SYSTEM_POLICY**, not medical-guideline terms:

- `OVERLAPPING_FINDING_EVIDENCE`
- `EVIDENCE_CONFLICT`
- `HIGH_PRIORITY_CLINICAL_REVIEW`
- preserving all upstream classifier outputs while avoiding double/triple counting
- clinician review always required

---

# Citation policy

Every medical/terminology rule added to `SKILL.md` must be traceable to:
- `[S1]`
- `[S2]`
- `[S3]`
- `[S4]`
- `[S5]`

If no source supports a proposed medical rule:
- do not add it as medical fact;
- mark `EVIDENCE_GAP`;
- or label it `MEDVISION_SYSTEM_POLICY`.

# Source precedence

1. S2 for current interstitial-pneumonia classification.
2. S3 for UIP/IPF/PPF-specific rules.
3. S5 for ILA vs ILD.
4. S1 for terminology.
5. S4 for imaging appropriateness.

# Update policy

When newer evidence is added:
1. distinguish CXR finding from HRCT pattern;
2. distinguish imaging pattern from etiologic ILD diagnosis;
3. distinguish ILA from clinical ILD;
4. preserve longitudinal requirements for PPF;
5. preserve multidisciplinary uncertainty/diagnostic confidence.
