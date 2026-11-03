# references.md — Acute Aortic Syndrome Concern v1

## S1 — 2024 ESC Guidelines for Peripheral Arterial and Aortic Diseases

Mazzolai L, Teixido-Tura G, Lanzi S, et al.  
**2024 ESC Guidelines for the management of peripheral arterial and aortic diseases.**  
European Heart Journal. 2024;45(36):3538-3700.  
PMID: 39210722  
DOI: 10.1093/eurheartj/ehae179  
URL: https://pubmed.ncbi.nlm.nih.gov/39210722/

### Used for
- Current ESC framework for acute thoracic aortic syndromes.
- Acute aortic syndrome includes aortic dissection, intramural haematoma, penetrating atherosclerotic ulcer, and related acute aortic pathology.
- Diagnosis requires integration of symptoms, examination, risk context, and definitive aortic imaging.
- This module does not implement treatment recommendations from the guideline.

---

## S2 — 2022 ACC/AHA Aortic Disease Guideline

Isselbacher EM, Preventza O, Hamilton Black J 3rd, et al.  
**2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease.**  
Circulation. 2022.  
PMID: 36322642  
PMCID: PMC9876736  
DOI: 10.1161/CIR.0000000000001106  
URL: https://www.ahajournals.org/doi/10.1161/CIR.0000000000001106

### Used for
- Plain chest X-ray is neither sufficiently sensitive nor specific to diagnose acute aortic syndrome.
- CT is recommended as initial diagnostic imaging in suspected AAS; TEE and MRI are reasonable alternatives.
- CXR findings may raise suspicion but cannot confirm or exclude AAS.
- No biomarker is diagnostic.
- In low pretest-probability contexts, low D-dimer combined with low risk scoring can make AAS unlikely, but this is context dependent.
- AAD-RS/AORTAs may aid evaluation but are not universally adopted.

### Scope constraint
MedVision does not autonomously order CT/TEE/MRI, compute an undocumented risk score, or make treatment decisions.

---

## S3 — Chest radiography diagnostic-accuracy study

von Kodolitsch Y, Nienaber CA, Dieckmann C, et al.  
**Chest radiography for the diagnosis of acute aortic syndrome.**  
Am J Med. 2004;116(2):73-77.  
PMID: 14715319  
DOI: 10.1016/j.amjmed.2003.08.030  
URL: https://pubmed.ncbi.nlm.nih.gov/14715319/

### Used for
- CXR has limited diagnostic value for AAS.
- Sensitivity was incomplete overall and particularly limited for proximal aortic disease.
- A normal chest radiograph cannot safely rule out AAS.

---

## S4 — Existing MedVision Aortic Enlargement finding evidence

The existing `medvision-aortic-enlargement` skill is authoritative for:
- Aortic enlargement as a radiographic finding;
- CXR limitations;
- `Aortic enlargement != aneurysm != dissection != acute aortic syndrome`;
- CT/MRI/TTE as stronger anatomic evidence;
- normal CXR not excluding acute aortic pathology;
- acute concerning symptoms raising AAS concern without confirming dissection.

This disease module builds on that skill and must not weaken its guardrails.

---

# MedVision system-policy labels

Internal labels:

```text
ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED
ACUTE_AORTIC_SYNDROME_CONCERN_INDETERMINATE
AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT
ACUTE_AORTIC_SYNDROME_CONCERN_CONFLICTED
ACUTE_AORTIC_SYNDROME_NOT_ESTABLISHED
DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS
AAS_SUBTYPE_UNRESOLVED
MALPERFUSION_CONCERN
```

These are MedVision system-policy states, not formal guideline wording.
