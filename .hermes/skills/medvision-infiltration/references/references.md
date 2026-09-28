# references.md — Infiltration

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
**Primary use:** Modern terminology.

### Facts used
- `Opacity` is a nonspecific focal or diffuse area of increased attenuation.
- `Infiltrate` is obsolete/nonrecommended terminology.
- Historical usage of `infiltrate` overlaps with `opacity`.
- More specific descriptors should be preferred where available.

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
**Primary use:** Canonical-label semantics.

### Facts used
- The dataset separates local radiographic findings from global suspected-disease labels.
- `Infiltration` is a local label.
- `Lung opacity` is also a distinct local label.
- `Consolidation`, `Atelectasis`, `Nodule/Mass`, and other findings are separately represented.
- Disease-level labels include Pneumonia, Tuberculosis, Lung tumor and others.

### Scope constraint
The dataset taxonomy does not establish medical causality or independence among overlapping local findings.

---

## Source S3

**Title:** Is infiltrate a useful term in the interpretation of chest radiographs? Physician survey results  
**Authors:** Patterson HS, Sponaugle DN  
**Journal:** Radiology  
**Year:** 2005  
**PMID:** 15798161  
**DOI:** 10.1148/radiol.2351020759  
**URL:** https://pubmed.ncbi.nlm.nih.gov/15798161/  
**Evidence type:** Physician survey / terminology study  
**Primary use:** Direct evidence of ambiguity and imprecision.

### Facts used
- Physicians interpreted `infiltrate` as compatible with many different pathophysiologic processes.
- Most respondents thought the term implied more than one process.
- Only a small minority thought the term implied a specific etiology.
- The authors concluded that `infiltrate` is a nonspecific and imprecise radiographic descriptor.

### Scope constraint
This is an older terminology study; S1 is the current preferred terminology source.

---

## Source S4

**Title:** ACR Appropriateness Criteria — Acute Respiratory Illness in Immunocompetent Patients  
**Organization:** American College of Radiology  
**Revision:** 2024  
**URL:** https://acsearch.acr.org/docs/69446/Narrative/  
**Evidence type:** Imaging appropriateness guideline  
**Primary use:** Acute respiratory illness context in immunocompetent adults.

### Facts used
- Imaging appropriateness depends on clinical scenario, examination, vital signs, risk factors and prior imaging.
- CT is not a universal next step for every acute respiratory illness or nonspecific CXR label.

### Scope constraint
Do not use this source to infer pneumonia from `Infiltration`.

---

## Source S5

**Title:** ACR Appropriateness Criteria — Acute Respiratory Illness in Immunocompromised Patients  
**Organization:** American College of Radiology  
**URL:** https://acsearch.acr.org/docs/69447/Narrative/  
**Evidence type:** Imaging appropriateness guideline  
**Primary use:** Immunocompromised acute-respiratory-illness context.

### Facts used
- For immunocompromised acute respiratory illness with normal/equivocal/nonspecific CXR, CT chest without IV contrast is rated Usually Appropriate as next imaging.
- For immunocompromised acute respiratory illness with multiple/diffuse/confluent CXR opacities, CT chest without IV contrast is rated Usually Appropriate as next imaging.
- Imaging strategy is scenario-specific.

### Scope constraint
- Do not generalize these rules to immunocompetent or unknown-status patients.
- Do not autonomously order CT.

---

# MedVision system-policy note

The following are **MEDVISION_SYSTEM_POLICY**, not medical-guideline terms:

- `OVERLAPPING_FINDING_EVIDENCE`
- preserve all upstream canonical labels while preventing semantic double/triple counting;
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

1. S1 for current terminology.
2. S2 for dataset taxonomy/provenance.
3. S3 for term ambiguity evidence.
4. S4/S5 only within matching acute-respiratory scenarios.

# Update policy

When newer evidence is added:
1. preserve canonical dataset provenance;
2. distinguish modern terminology from legacy labels;
3. distinguish local finding from disease diagnosis;
4. preserve overlapping outputs but avoid double counting;
5. do not silently introduce disease-specific inference.
