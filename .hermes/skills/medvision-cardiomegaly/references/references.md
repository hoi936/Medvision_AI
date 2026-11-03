# references.md — Cardiomegaly

## Source S1

**Title:** Radiological Cardiothoracic Ratio in Evidence-Based Medicine  
**Authors:** Truszkiewicz K, Poręba R, Gać P  
**Journal:** Journal of Clinical Medicine  
**Year:** 2021  
**PMID:** 34066783  
**PMCID:** PMC8125954  
**DOI:** 10.3390/jcm10092016  
**URL:** https://pubmed.ncbi.nlm.nih.gov/34066783/  
**Evidence type:** Review  
**Primary use:** CTR definition, PA projection, technique limitations, silhouette interpretation.

### Facts used
- CTR is conventionally measured on PA radiographs.
- A conventional cutoff above 0.50 supports radiographic heart enlargement.
- Increased CTR does not directly describe cardiac function.
- CTR assessment outside PA projection has important limitations.
- Apparent cardiac enlargement can be difficult to distinguish from pericardial disease.

---

## Source S2

**Title:** Diagnostic performance of chest radiography measurements for the assessment of cardiac chamber enlargement  
**Authors:** Soares Torres F, Eifer DA, Sanchez Tijmes F, Nguyen ET, Hanneman K  
**Journal:** CMAJ  
**Year:** 2021  
**PMID:** 34750176  
**PMCID:** PMC8584372  
**DOI:** 10.1503/cmaj.210083  
**URL:** https://pubmed.ncbi.nlm.nih.gov/34750176/  
**Evidence type:** Diagnostic accuracy study using cardiac MRI as reference  
**Primary use:** Limits of the traditional 0.50 CTR threshold.

### Facts used
- The traditional CTR 0.50 cutpoint has limited diagnostic value for cardiac chamber enlargement.
- In PA studies it showed only moderate sensitivity and specificity.
- CXR heart-size measurements are imperfect surrogates for true chamber enlargement.

---

## Source S3

**Title:** 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure  
**Authors:** Heidenreich PA, Bozkurt B, Aguilar D, et al.  
**Journal:** Circulation  
**Year:** 2022  
**PMID:** 35363499  
**DOI:** 10.1161/CIR.0000000000001063  
**URL:** https://pubmed.ncbi.nlm.nih.gov/35363499/  
**Evidence type:** Official clinical practice guideline  
**Primary use:** Heart-failure clinical integration and TTE role.

### Facts used
- Chest X-ray is useful in patients with suspected/new-onset HF to assess cardiomegaly, congestion/edema and alternative causes.
- CXR should not be the sole determinant of the presence or specific cause of HF.
- Cardiomegaly may be absent in acute HF.
- TTE provides direct information about cardiac structure and function, including myocardium, valves and pericardium.

### Scope constraint
Do not transform a Cardiomegaly finding into an HF diagnosis.

---

## Source S4

**Title:** How well can the chest radiograph diagnose left ventricular dysfunction?  
**Authors:** Badgett RG, Mulrow CD, Otto PM, Ramírez G  
**Journal:** Journal of General Internal Medicine  
**Year:** 1996  
**PMID:** 8945695  
**DOI:** 10.1007/BF02599031  
**URL:** https://pubmed.ncbi.nlm.nih.gov/8945695/  
**Evidence type:** Diagnostic review/meta-analytic synthesis of older studies  
**Primary use:** LV dysfunction guardrail.

### Facts used
- Cardiomegaly had limited sensitivity/specificity for reduced EF in pooled evidence.
- Cardiomegaly alone cannot adequately confirm or exclude LV dysfunction in usual clinical settings.

### Age note
Use for the stable limitation that CXR cardiomegaly is not equivalent to LV dysfunction. S2/S3 take precedence where more current evidence applies.

---

## Source S5

**Title:** Diagnostic value of B-Type natriuretic peptide and chest radiographic findings in patients with acute dyspnea  
**Authors:** Knudsen CW, Omland T, Clopton P, et al.  
**Journal:** American Journal of Medicine  
**Year:** 2004  
**PMID:** 15006584  
**DOI:** 10.1016/j.amjmed.2003.10.028  
**URL:** https://pubmed.ncbi.nlm.nih.gov/15006584/  
**Evidence type:** Prospective diagnostic study  
**Primary use:** Integration of BNP and CXR in acute dyspnea.

### Facts used
- BNP and CXR findings provided complementary diagnostic information for HF in acute dyspnea.
- Cardiomegaly is contextual evidence, not standalone proof of HF.

### Scope constraint
The study-specific BNP threshold is not encoded as a universal rule in this Cardiomegaly skill.

---

## Source S6

**Title:** Is there any diagnostic value of anteroposterior chest radiography in predicting cardiac chamber enlargement?  
**Authors:** Sahin H, Chowdhry DN, Olsen A, Nemer O, Wahl L  
**Journal:** International Journal of Cardiovascular Imaging  
**Year:** 2019  
**PMID:** 30143921  
**URL:** https://pubmed.ncbi.nlm.nih.gov/30143921/  
**Evidence type:** Diagnostic accuracy study  
**Primary use:** AP portable projection limitations.

### Facts used
- AP radiographs can overestimate apparent heart size/CTR relative to CT-based measures.
- A standard 0.50 CTR threshold on AP radiographs has poor specificity for chamber enlargement.
- AP projection must increase interpretation uncertainty.

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

1. S1 for CTR/projection semantics.
2. S2 for modern diagnostic-performance limitations of CTR.
3. S3 for HF and echocardiography context.
4. S4 for the stable LV-dysfunction guardrail.
5. S5 for BNP+CXR integration in acute dyspnea.
6. S6 for AP projection limitations.

# Update policy

When newer evidence is added:
1. record year, population and modality;
2. compare it against existing rules;
3. preserve disagreements;
4. do not silently replace a radiographic surrogate with a disease diagnosis;
5. update `SKILL.md` only after evidence review.
