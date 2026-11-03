# references.md — Aortic Enlargement

## Source S1

**Title:** 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases  
**Authors:** Mazzolai L, Teixido-Tura G, Lanzi S, et al.; ESC Scientific Document Group  
**Journal:** European Heart Journal  
**Year:** 2024  
**PMID:** 39210722  
**DOI:** 10.1093/eurheartj/ehae179  
**URL:** https://pubmed.ncbi.nlm.nih.gov/39210722/  
**Evidence type:** Current clinical practice guideline  
**Primary use:** Chest-X-ray limitations, aortic imaging, size context and acute aortic syndrome.

### Facts used
- CXR can detect abnormalities of aortic size/contour that require confirmation by another imaging technique.
- CXR has limited diagnostic sensitivity/specificity for aortic disease.
- Normal CXR does not rule out AAS.
- Aortic measurements require standardized imaging.
- Expected aortic size depends on age, sex and body-size context.
- CCT/CMR/TTE/TOE have defined roles in aortic assessment.
- Suspected AAS requires prompt definitive imaging; ECG-gated CT is a major/preferred diagnostic modality in appropriate patients.

---

## Source S2

**Title:** 2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease  
**Authors:** Isselbacher EM, Preventza O, Hamilton Black J III, et al.  
**Journal:** Circulation  
**Year:** 2022  
**PMID:** 36322642  
**PMCID:** PMC9876736  
**DOI:** 10.1161/CIR.0000000000001106  
**URL:** https://pubmed.ncbi.nlm.nih.gov/36322642/  
**Evidence type:** Clinical practice guideline  
**Primary use:** Definitions, terminology, measurement/indexing and acute aortic syndrome.

### Facts used
- Plain CXR is neither sufficiently sensitive nor specific to diagnose AAS.
- CXR abnormalities may raise suspicion, particularly if new compared with prior films.
- CT is recommended as initial diagnostic imaging for suspected AAS; TEE/MRI are reasonable alternatives in appropriate settings.
- Accurate aortic measurement requires defined segmental measurements and reproducible technique.
- Aortic size interpretation may require normalization to body size/height.
- ACC/AHA terminology distinguishes measured ascending-aortic dilation/aneurysm categories and prefers `dilation` over ambiguous `ectasia`.

### Scope constraint
Numeric measured-aortic categories in this guideline must NOT be applied directly to the VinBigData `Aortic enlargement` CXR class.

---

## Source S3

**Title:** Imaging Thoracic Aortic Aneurysm  
**Authors:** Kallianos KG, Burris NS  
**Journal:** Radiologic Clinics of North America  
**Year:** 2020  
**PMID:** 32471540  
**PMCID:** PMC7269689  
**DOI:** 10.1016/j.rcl.2020.02.009  
**URL:** https://pubmed.ncbi.nlm.nih.gov/32471540/  
**Evidence type:** Imaging review  
**Primary use:** Cross-sectional confirmation, measurement artifact and reproducibility.

### Facts used
- CTA and MRA are major techniques for TAA diagnosis/surveillance.
- Imaging technique, artifact and measurement error matter.
- Reproducible, high-quality aortic measurements are important.

---

## Source S4

**Title:** Aortic size assessment by noncontrast cardiac computed tomography: normal limits by age, gender, and body surface area  
**Authors:** Wolak A, Gransar H, Thomson LEJ, et al.  
**Journal:** JACC Cardiovascular Imaging  
**Year:** 2008  
**PMID:** 19356429  
**DOI:** 10.1016/j.jcmg.2007.11.005  
**URL:** https://pubmed.ncbi.nlm.nih.gov/19356429/  
**Evidence type:** Adult CT reference study  
**Primary use:** Normal-size context.

### Facts used
- Thoracic aortic dimensions vary with age, sex and BSA.
- Hypertension was associated with thoracic aortic dimensions in the study population.
- Normal ranges are segment- and population-dependent.

### Scope constraint
Do not transplant the study's CT reference values directly to CXR measurements.

---

## Source S5

**Title:** Distribution, Determinants and Normal Reference Values of Aortic Arch Width: Thoracic Aortic Geometry in the Framingham Heart Study  
**Authors:** Qazi S, Gona PN, Musgrave RM, et al.  
**Journal:** American Heart Journal Plus  
**Year:** 2023  
**PMID:** 36742989  
**PMCID:** PMC9894311  
**DOI:** 10.1016/j.ahjo.2022.100247  
**URL:** https://pubmed.ncbi.nlm.nih.gov/36742989/  
**Evidence type:** Population CT study  
**Primary use:** Aortic-arch geometry and contextual determinants.

### Facts used
- Aortic-arch width increases with age.
- Greater width was associated with body size, diastolic blood pressure, smoking burden and prevalent CVD.
- Sex-specific and age-specific reference context matters.

### Scope constraint
This is CT-based geometry and must not be treated as a universal CXR cutoff.

---

## Source S6

**Title:** Diagnostic Utility of Chest Radiography in Predicting Long-Standing Systemic Arterial Hypertension  
**Authors:** Sahin H, Stark P  
**Journal:** Aorta (Stamford)  
**Year:** 2017  
**PMID:** 29766008  
**PMCID:** PMC5942550  
**DOI:** 10.12945/j.aorta.2017.17.092  
**URL:** https://pubmed.ncbi.nlm.nih.gov/29766008/  
**Evidence type:** Observational diagnostic-association study  
**Primary use:** Hypertension-association branch only.

### Facts used
- Frontal CXR aortic-arch width was associated with long-standing systemic arterial hypertension in the study cohort.

### Scope constraint
- Do not diagnose hypertension from aortic enlargement.
- Do not encode the study-specific arch-width cutoffs as universal diagnostic thresholds.

---

# Citation policy

Every medical rule added to `SKILL.md` must be traceable to:
- `[S1]`
- `[S2]`
- `[S3]`
- `[S4]`
- `[S5]`
- `[S6]`

If no source supports a proposed medical rule:
- do not add it as medical fact;
- mark `EVIDENCE_GAP`;
- or label it `MEDVISION_SYSTEM_POLICY` if it is a workflow/safety rule.

# Source precedence

1. S1 ESC 2024.
2. S2 ACC/AHA 2022.
3. S3 cross-sectional imaging review.
4. S4/S5 adult reference/context studies.
5. S6 hypertension association only.

# Update policy

When newer evidence is added:
1. record modality, aortic segment, age group and population;
2. distinguish CXR contour evidence from direct cross-sectional measurement;
3. preserve differing guideline terminology;
4. do not silently convert an AI class into aneurysm/dissection;
5. update `SKILL.md` only after evidence review.
