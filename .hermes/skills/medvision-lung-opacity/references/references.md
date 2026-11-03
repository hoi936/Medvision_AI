# references.md — Lung Opacity

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
**Primary use:** Opacity terminology and relationship to other descriptors.

### Facts used
- `Opacity` is any focal or diffuse nonspecific area of increased attenuation.
- Opacity is a general descriptor and does not indicate the nature of the condition causing it.
- `Infiltrate` is obsolete/nonrecommended terminology that historically has sometimes been used synonymously with opacity.
- Ground-glass terminology is specifically defined for CT and should be applied in the CT context.
- Consolidation has a more specific imaging definition than generic opacity.

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
**Primary use:** VinDr/VinBigData annotation semantics.

### Facts used
- The dataset contains 22 local labels and 6 global labels.
- `Lung opacity` is a local finding label.
- `Infiltration`, `Consolidation`, `Atelectasis`, and `Nodule/Mass` are also local labels.
- Global labels include suspected disease-level impressions such as Lung tumor, Pneumonia, Tuberculosis, COPD, Other diseases, and No finding.
- Local labels are spatially localized with bounding boxes; global labels reflect diagnostic impression.

### Scope constraint
Dataset label structure supports separation of radiographic findings from disease-level labels. It does not by itself define clinical causality among the local findings.

---

## Source S3

**Title:** ACR Appropriateness Criteria — Diffuse Lung Disease  
**Organization:** American College of Radiology  
**Version:** New 2021  
**URL:** https://acsearch.acr.org/docs/3157911/Narrative/  
**Evidence type:** Imaging appropriateness guideline  
**Primary use:** Diffuse-lung-disease context only.

### Facts used
- The guideline addresses suspected diffuse lung disease.
- Chest radiography and CT/HRCT have roles in evaluating diffuse lung disease depending on the clinical question.

### Scope constraint
Do not generalize diffuse-lung-disease imaging guidance to every isolated `Lung Opacity` AI finding.

---

## Source S4

**Title:** ACR Appropriateness Criteria — Acute Respiratory Illness in Immunocompetent Patients  
**Organization:** American College of Radiology  
**Revision:** 2024  
**URL:** https://acsearch.acr.org/docs/69446/Narrative/  
**Evidence type:** Imaging appropriateness guideline  
**Primary use:** Acute respiratory illness context only.

### Facts used
- Imaging appropriateness varies by symptoms, examination, vital signs, risk factors, and the initial imaging result.
- CT is not a universal next step for every acute respiratory illness or every opacity.

### Scope constraint
Do not infer pneumonia or automatically recommend CT from a generic Lung Opacity label.

---

## Source S5

**Title:** Improving reference standards for validation of AI-based radiography  
**Authors:** Duggan GE, Reicher JJ, Liu Y, Tse D, Shetty S  
**Journal:** British Journal of Radiology  
**Year:** 2021  
**PMID:** 34142868  
**PMCID:** PMC8248225  
**DOI:** 10.1259/bjr.20210435  
**URL:** https://pubmed.ncbi.nlm.nih.gov/34142868/  
**Evidence type:** AI/radiology reference-standard study  
**Primary use:** Human-reader variability and AI reference-standard caution.

### Facts used
- Six radiologists evaluated chest radiographs for findings including airspace opacity.
- Inter-reader agreement/reproducibility was not perfect.
- Majority voting/adjudication improved reference-standard reproducibility for several findings.
- AI validation must account for reader disagreement and reference-standard construction.

### Scope constraint
This source supports uncertainty/conflict handling, not a disease-specific diagnostic rule.

---

# MedVision system-policy note

The following are **MEDVISION_SYSTEM_POLICY**, not claims sourced to a medical guideline:

- `OVERLAPPING_FINDING_EVIDENCE`
- preserving all positive upstream findings while preventing semantic double counting;
- preferring a more-specific imaging descriptor for characterization without deleting the broad Lung Opacity output;
- `EVIDENCE_CONFLICT`;
- `HIGH_PRIORITY_CLINICAL_REVIEW`;
- doctor review always required.

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

1. S1 for terminology.
2. S2 for dataset-label semantics.
3. S3/S4 only within their clinical scope.
4. S5 for AI/reference-standard uncertainty.

# Update policy

When newer evidence is added:
1. distinguish broad descriptor from specific pattern;
2. distinguish dataset taxonomy from medical causality;
3. distinguish CXR from CT-specific terminology;
4. preserve overlap rather than double counting;
5. do not silently convert an imaging finding into a disease diagnosis.
