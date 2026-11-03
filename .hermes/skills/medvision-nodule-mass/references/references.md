# references.md — Nodule/Mass

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
**Primary use:** Nodule/mass definition and morphology terminology.

### Facts used
- Pulmonary nodule: circumscribed, typically round opacity with average diameter <=30 mm.
- Mass: circumscribed lesion >30 mm in diameter.
- Mass terminology does not itself imply neoplastic etiology.
- CT nodule attenuation can be solid, ground-glass, or part-solid.
- Nodules can have varied shape, margin, location, and internal components including calcium and fat.
- Thin-section CT is important for accurate small-nodule characterization.

---

## Source S2

**Title:** ACR Appropriateness Criteria — Incidentally Detected Indeterminate Pulmonary Nodule  
**Organization:** American College of Radiology  
**Revision:** 2023  
**URL:** https://acsearch.acr.org/docs/69455/Narrative  
**Evidence type:** Imaging appropriateness guideline  
**Primary use:** Initial CXR-to-CT characterization pathway.

### Variant used

**Variant 1:** Adult >=35 years, incidentally detected indeterminate pulmonary nodule on chest radiograph; next imaging study.

### Facts used
- CT chest without IV contrast: `Usually Appropriate`.
- Image-guided transthoracic needle biopsy: `Usually Not Appropriate` as the initial next step in this variant.
- FDG-PET/CT: `Usually Not Appropriate` as the initial next step in this variant.

### Scope constraint
Do not generalize this exact variant to adults <35 years or to a CT-characterized lesion without re-evaluating the applicable scenario.

---

## Source S3

**Title:** Guidelines for Management of Incidental Pulmonary Nodules Detected on CT Images: From the Fleischner Society 2017  
**Authors:** MacMahon H, Naidich DP, Goo JM, et al.  
**Journal:** Radiology  
**Year:** 2017  
**PMID:** 28240562  
**DOI:** 10.1148/radiol.2017161659  
**URL:** https://pubmed.ncbi.nlm.nih.gov/28240562/  
**Evidence type:** Practice guideline  
**Primary use:** CT-detected incidental nodule framework, morphology/risk factors, prior imaging/growth context.

### Facts used
- Applies to incidentally encountered nodules detected at CT in adults >=35 years.
- Does not apply to lung-cancer screening, immunocompromised patients, or patients with known primary cancer at risk for metastases.
- Management differs for solid, ground-glass, part-solid, single and multiple nodules.
- Nodule size and morphology contribute to malignancy risk.
- Marginal spiculation is a malignancy risk factor.
- Patient preferences and individual risk factors matter.

### Scope constraint
Do not apply Fleischner CT tables directly to a CXR AI class without CT lesion characterization.

---

## Source S4

**Title:** British Thoracic Society guidelines for the investigation and management of pulmonary nodules  
**Authors:** Callister MEJ, Baldwin DR, Akram AR, et al.  
**Journal:** Thorax  
**Year:** 2015  
**PMID:** 26082159  
**DOI:** 10.1136/thoraxjnl-2015-207168  
**URL:** https://pubmed.ncbi.nlm.nih.gov/26082159/  
**BTS resource:** https://www.brit-thoracic.org.uk/clinical-resources/guidelines/pulmonary-nodules/  
**Evidence type:** Clinical practice guideline  
**Primary use:** Malignancy-risk framework and downstream investigation/management context.

### Facts used
- Pulmonary-nodule management is risk based.
- BTS provides risk-prediction calculators to be used with the guideline.
- PET-CT, surveillance, biopsy, and other management choices belong within a risk-based framework.

### Scope constraint
This v1 does not implement a numeric BTS risk calculator.

---

## Source S5

**Title:** Evaluation of individuals with pulmonary nodules: when is it lung cancer? Diagnosis and management of lung cancer, 3rd ed: ACCP evidence-based clinical practice guidelines  
**Authors:** Gould MK, Donington J, Lynch WR, et al.  
**Journal:** Chest  
**Year:** 2013  
**PMID:** 23649456  
**PMCID:** PMC3749714  
**DOI:** 10.1378/chest.12-2351  
**URL:** https://pubmed.ncbi.nlm.nih.gov/23649456/  
**Evidence type:** Evidence-based clinical practice guideline  
**Primary use:** Probability-of-malignancy reasoning and management-decision principles.

### Facts used
- Evaluate pulmonary nodules by estimating probability of malignancy.
- Use imaging to better characterize lesions.
- Weigh benefits and harms of surveillance, nonsurgical biopsy, and surgical approaches.
- Elicit patient preferences.

### Scope constraint
A probability-of-malignancy framework is not equivalent to a cancer diagnosis, and this MedVision v1 does not autonomously select management.

---

# Citation policy

Every medical rule added to `SKILL.md` must be traceable to:
- `[S1]`
- `[S2]`
- `[S3]`
- `[S4]`
- `[S5]`

If no source supports a proposed medical rule:
- do not add it as medical fact;
- mark `EVIDENCE_GAP`;
- or label it `MEDVISION_SYSTEM_POLICY` if it is a workflow/safety rule.

# Source precedence

1. S1 for terminology.
2. S2 for initial next imaging after an indeterminate CXR nodule in the stated population.
3. S3 for incidental CT-detected nodule management.
4. S4/S5 for broader risk-based clinical decision principles.

# Update policy

When newer evidence is added:
1. record population and modality;
2. distinguish CXR detection from CT characterization;
3. distinguish incidental CT nodules from screening nodules;
4. preserve known-cancer/immunocompromised scope differences;
5. do not silently convert imaging risk into pathology diagnosis.
