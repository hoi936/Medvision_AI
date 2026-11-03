# references.md — Pleural Thickening

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
**Primary use:** Standard terminology and modality-specific pleural descriptors.

### Facts used
- The glossary standardizes thoracic-radiology terminology.
- Pleural abnormalities should be described using specific imaging morphology when available.
- CT-specific pleural morphology should not be invented from a generic CXR classifier result.

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
- VinDr-CXR separates local radiographic findings from global suspected-disease labels.
- Pleural abnormalities are handled as imaging findings rather than automatically as etiologic disease diagnoses.

### Scope constraint
Dataset taxonomy does not establish cause or independence of overlapping findings.

---

## Source S3

**Title:** Pictorial Review of Pleural Disease: Multimodality Imaging and Differential Diagnosis  
**Authors:** Yamada A, Taiji R, Nishimoto Y, et al.  
**Journal:** RadioGraphics  
**Year:** 2024  
**PMID:** 38547031  
**DOI:** 10.1148/rg.230079  
**URL:** https://pubmed.ncbi.nlm.nih.gov/38547031/  
**Evidence type:** Multimodality pleural-imaging review  
**Primary use:** Pleural-thickening morphology and broad differential.

### Facts used
- Pleural thickening may be unilateral or bilateral and focal, multifocal, or diffuse.
- Multiple disease groups can produce pleural thickening, including asbestos-related disease, neoplasms, and systemic disease.
- CT, MRI, and FDG PET/CT can help characterize/differentiate pleural lesions.
- Pleural plaques can manifest as discontinuous pleural thickening and may calcify.
- Malignant pleural mesothelioma can manifest with circumferential nodular pleural thickening.
- Pleural effusion and pleural thickening may coexist in multiple disease processes.

### Scope constraint
Imaging morphology can increase concern but does not replace pathology/clinical diagnosis.

---

## Source S4

**Title:** British Thoracic Society Guideline for pleural disease  
**Authors:** Roberts ME, Rahman NM, Maskell NA, et al.  
**Journal:** Thorax  
**Year:** 2023  
**PMID:** 37433578  
**DOI:** 10.1136/thorax-2022-219784  
**URL:** https://pubmed.ncbi.nlm.nih.gov/37433578/  
**Evidence type:** Current clinical practice guideline  
**Primary use:** Pleural-disease investigation/management context.

### Facts used
- Pleural disease requires scenario-specific clinical investigation.
- Malignant pleural disease belongs in a broader pleural diagnostic framework rather than being inferred from one CXR feature.
- Pleural procedures and downstream management depend on clinical context and should not be triggered autonomously by this finding skill.

---

## Source S5

**Title:** Focal pleural thickening mimicking pleural plaques on chest computed tomography: tips and tricks  
**Authors:** Alfudhili KM, Lynch DA, Laurent F, Ferretti GR, Dunet V, Beigelman-Aubry C  
**Journal:** British Journal of Radiology  
**Year:** 2016  
**PMID:** 26539633  
**PMCID:** PMC4985966  
**DOI:** 10.1259/bjr.20150792  
**URL:** https://pubmed.ncbi.nlm.nih.gov/26539633/  
**Evidence type:** CT imaging review  
**Primary use:** Pleural-plaque mimic guardrail.

### Facts used
- Focal pleural thickening has multiple potential causes/mimics.
- Mimics can include normal structures and disease processes such as prior tuberculosis, pleural metastasis, silicosis, and rarer conditions.
- Accurate pleural-plaque recognition requires appropriate technical/anatomic context.

### Scope constraint
Do not infer pleural plaque or asbestos exposure from generic thickening.

---

## Source S6

**Title:** Clinical consequences of asbestos-related diffuse pleural thickening: A review  
**Authors:** Miles SE, Sandrini A, Johnson AR, Yates DH  
**Journal:** Journal of Occupational Medicine and Toxicology  
**Year:** 2008  
**PMID:** 18775081  
**PMCID:** PMC2553409  
**DOI:** 10.1186/1745-6673-3-20  
**URL:** https://pubmed.ncbi.nlm.nih.gov/18775081/  
**Evidence type:** Review  
**Primary use:** Asbestos-related diffuse pleural thickening and plaque distinction.

### Facts used
- Asbestos-related diffuse pleural thickening is extensive visceral-pleural fibrosis occurring in an asbestos-exposure context.
- It may coexist with asbestos-related pleural plaques.
- Diffuse pleural thickening and pleural plaques have distinct pathology.
- Asbestos exposure may be occupational or environmental.

### Scope constraint
- Do not infer asbestos exposure from pleural thickening alone.
- Do not infer asbestosis from pleural thickening alone.

---

# MedVision system-policy note

The following are **MEDVISION_SYSTEM_POLICY**, not medical-guideline terms:

- `EVIDENCE_CONFLICT`
- `HIGH_PRIORITY_CLINICAL_REVIEW`
- preserving upstream findings while avoiding etiologic over-attribution
- clinician review always required

A future Calcification skill may introduce overlap/de-duplication rules, but this skill must not assume calcification localization without explicit evidence.

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

1. S3 for pleural morphology/differential.
2. S4 for clinical pleural-disease framework.
3. S6 for asbestos-related diffuse pleural thickening.
4. S5 for plaque mimics.
5. S1 for terminology.
6. S2 for dataset provenance.

# Update policy

When newer evidence is added:
1. distinguish CXR finding from cross-sectional morphology;
2. distinguish pleural thickening from pleural plaques;
3. distinguish asbestos association from proven exposure/etiology;
4. distinguish suspicious morphology from pathology diagnosis;
5. preserve finding-vs-disease separation.
