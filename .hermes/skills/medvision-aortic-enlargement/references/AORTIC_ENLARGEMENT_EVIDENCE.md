# AORTIC_ENLARGEMENT_EVIDENCE.md

## 0. Scope

Tài liệu này là evidence sheet v1 cho **Aortic enlargement** trong MedVision Hermes.

`Aortic enlargement` trong VinBigData phải được xử lý trước hết như một **radiographic finding / abnormality of aortic size or contour on chest radiography**, không phải là chẩn đoán thoracic aortic aneurysm, aortic dissection hay acute aortic syndrome.

Phạm vi v1:
- adult chest-radiograph reasoning;
- abnormal aortic size/contour as a screening clue;
- confirmation by echocardiography / CT / MRI when available;
- aortic-diameter interpretation with age/sex/body-size context;
- acute aortic syndrome safety branch;
- hypertension association as contextual evidence only;
- missing evidence, conflicts, uncertainty and doctor review.

Không tự mở rộng v1 sang pediatric, pregnancy-specific, genetic-aortopathy-specific, or postoperative surveillance algorithms nếu chưa có source pack riêng.

---

## 1. Evidence hierarchy

### S1 — ESC 2024
**Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases. Eur Heart J. 2024.**  
PMID: 39210722  
DOI: 10.1093/eurheartj/ehae179  
Role: **primary current guideline for aortic imaging, chest-X-ray limitations, body-size/age/sex context, and acute aortic syndrome**

### S2 — ACC/AHA 2022
**Isselbacher EM, Preventza O, Hamilton Black J III, et al. 2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease. Circulation. 2022.**  
PMID: 36322642  
PMCID: PMC9876736  
DOI: 10.1161/CIR.0000000000001106  
Role: **definitions, aortic measurement/indexing, terminology, cross-sectional imaging, and AAS guardrails**

### S3 — Kallianos & Burris 2020
**Kallianos KG, Burris NS. Imaging Thoracic Aortic Aneurysm. Radiol Clin North Am. 2020.**  
PMID: 32471540  
PMCID: PMC7269689  
DOI: 10.1016/j.rcl.2020.02.009  
Role: **CTA/MRA measurement quality, artifact, reproducibility, and TAA imaging confirmation**

### S4 — Wolak et al. 2008
**Wolak A, Gransar H, Thomson LEJ, et al. Aortic size assessment by noncontrast cardiac computed tomography: normal limits by age, gender, and body surface area. JACC Cardiovasc Imaging. 2008.**  
PMID: 19356429  
DOI: 10.1016/j.jcmg.2007.11.005  
Role: **normal adult thoracic aortic dimensions vary with age, sex, BSA, and hypertension**

### S5 — Qazi et al. 2023
**Qazi S, Gona PN, Musgrave RM, et al. Distribution, Determinants and Normal Reference Values of Aortic Arch Width: Thoracic Aortic Geometry in the Framingham Heart Study. Am Heart J Plus. 2023.**  
PMID: 36742989  
PMCID: PMC9894311  
DOI: 10.1016/j.ahjo.2022.100247  
Role: **aortic-arch width varies with age, sex/body size, blood pressure, smoking and CVD context**

### S6 — Sahin & Stark 2017
**Sahin H, Stark P. Diagnostic Utility of Chest Radiography in Predicting Long-Standing Systemic Arterial Hypertension. Aorta (Stamford). 2017.**  
PMID: 29766008  
PMCID: PMC5942550  
DOI: 10.12945/j.aorta.2017.17.092  
Role: **association between aortic-arch width and long-standing hypertension; association only, not diagnosis**

### Source precedence

1. S1 for current ESC guidance on CXR, aortic imaging, size context, and AAS.
2. S2 for ACC/AHA definitions, measurement/indexing, terminology and AAS.
3. S3 for imaging quality and reproducible TAA measurement.
4. S4/S5 for normal-reference/contextual variation.
5. S6 only for the hypertension-association branch.

---

## 2. Core semantic rule

A VinBigData `Aortic enlargement` output is:

`RADIOGRAPHIC_EVIDENCE_OF_ABNORMAL_AORTIC_SIZE_OR_CONTOUR`

It is NOT automatically:
- thoracic aortic aneurysm;
- aortic dissection;
- acute aortic syndrome;
- aortic rupture;
- penetrating atherosclerotic ulcer;
- intramural hematoma;
- hypertension;
- an indication for surgery or another intervention.

---

## 3. Chest-radiograph role and limitations

### S1

ESC 2024 states that chest radiography performed for other indications or when AAS is suspected may detect abnormalities of aortic size/contour that should be confirmed with another imaging technique.

S1 reports limited sensitivity and specificity of CXR for aortic disease and explicitly states that a normal CXR does not rule out acute aortic syndrome.

### S2

ACC/AHA 2022 similarly states that plain CXR is neither sufficiently sensitive nor specific to diagnose AAS. Certain findings can raise suspicion, particularly when new compared with prior imaging.

### Hermes rule

If AI reports `Aortic enlargement`:
- preserve it as radiographic evidence;
- do not convert it to a definitive aortic disease diagnosis;
- look for confirmatory cross-sectional or echocardiographic measurements if available.

If the CXR is described as normal:
- do not use normal CXR to exclude AAS when clinical suspicion is high.

---

## 4. Cross-sectional confirmation and aortic measurement

### S1 / S2 / S3

Accurate aortic assessment depends on standardized measurements.

CT and MRI provide high-quality cross-sectional assessment of the thoracic aorta; CT is a key modality when acute aortic disease is suspected, and CTA/MRA are central to thoracic aortic aneurysm diagnosis and surveillance.

S3 emphasizes:
- measurement artifacts can occur;
- technique and reproducibility matter;
- high-quality, reproducible measurements are required.

### Hermes behavior

If CT/MRI/TTE aortic measurements are available:
- preserve the CXR finding separately;
- use direct aortic measurements as stronger evidence for true aortic dilatation;
- record modality, aortic segment, and measurement if supplied.

Do NOT invent:
- aortic diameter;
- aortic segment;
- aneurysm size;
- growth rate.

---

## 5. Dilation vs aneurysm terminology

### S2 scope

ACC/AHA 2022 discusses ascending-aortic/root terminology and supports:
- `dilated` for milder enlargement;
- `aneurysm` at larger diameters in the relevant ascending-aortic context;
- preference for `dilation` over ambiguous use of `ectasia`.

The guideline also emphasizes that thresholds may require adjustment/indexing for patients substantially smaller or taller than average.

### Hermes guardrail

Do NOT apply a generic CXR class `Aortic enlargement` as equivalent to:
- `dilated ascending aorta`;
- `thoracic aortic aneurysm`.

The ACC/AHA numeric categories relate to measured aortic diameters in defined anatomic contexts, not to an AI CXR class.

If no segment-specific cross-sectional measurement exists:
`aneurysm_status: unknown`

is appropriate.

Do not encode a CXR-derived aneurysm threshold.

---

## 6. Age / sex / body-size context

### S1
ESC states that expected aortic diameter should be interpreted with age, sex and body surface area, and notes that the aorta tends to enlarge with ageing.

### S4
Wolak et al. found thoracic aortic dimensions vary with age, sex and BSA; hypertension was also associated with dimensions.

### S5
Framingham data showed aortic-arch width increases with age and was associated with body size, blood pressure, smoking burden and prevalent cardiovascular disease.

### Hermes behavior

A larger aortic contour:
- may have demographic/body-size context;
- is not automatically a pathologic aneurysm.

Never infer:
`older age -> normal enlargement`
or
`wide arch -> aneurysm`

without appropriate measurements/reference context.

If age/sex/body size are missing and true aortic dilation is being considered:
add them to `missing_evidence` when clinically relevant.

---

## 7. Hypertension branch

### S6

S6 reports an association between aortic-arch width on frontal radiography and long-standing systemic hypertension in its study population.

### Hermes behavior

Aortic enlargement/arch widening can be considered compatible with chronic hypertensive vascular remodeling when other evidence supports that context.

But:

`Aortic enlargement -> hypertension`

is prohibited.

Do not diagnose hypertension from CXR.

Use actual BP measurements/history as direct evidence when available.

Do not import the study-specific arch-width cutoffs as universal hypertension diagnostic thresholds in v1.

---

## 8. Acute aortic syndrome branch

### S1 / S2

Acute aortic syndromes are life-threatening conditions. CXR can raise suspicion but cannot reliably confirm or exclude them.

Clinical high-risk features can include, depending on the actual case:
- abrupt severe chest/back pain;
- hypotension/shock;
- pulse or blood-pressure differential;
- neurologic deficits;
- aortic regurgitation/pericardial complications;
- other clinician-documented AAS concern.

ESC 2024 identifies ECG-gated cardiovascular CT as a preferred/major confirmatory imaging technique for suspected AAS in appropriate patients; ACC/AHA 2022 recommends CT as initial diagnostic imaging for suspected AAS, with TEE/MRI as alternatives where appropriate.

### Hermes behavior

If `Aortic enlargement` coexists with high-risk AAS clinical features:

emit:

`ACUTE_AORTIC_SYNDROME_CONCERN`

and:

`HIGH_PRIORITY_CLINICAL_REVIEW`

Do NOT output:
- `aortic dissection confirmed`;
- `aneurysm rupture confirmed`.

Do not delay urgency reasoning merely because CXR is normal or nonspecific.

---

## 9. Relationship to mediastinal contour

Aortic enlargement may contribute to abnormal mediastinal/aortic contour on CXR.

### Hermes guardrail

Do not assume:
- every widened mediastinum is aortic enlargement;
- every aortic enlargement finding is AAS;
- every abnormal aortic contour is aneurysm.

If a prior CXR is available and a contour change is new, this may increase concern in an appropriate clinical context, but it does not establish the diagnosis [S2].

---

## 10. Supporting evidence model

### IMAGE_EVIDENCE
- AI `Aortic enlargement`;
- model score;
- aortic contour/arch description if supplied;
- mediastinal width/contour if supplied;
- radiologist/manual CXR interpretation;
- prior CXR comparison.

### AORTIC_IMAGING_EVIDENCE
Potentially relevant:
- TTE aortic-root/ascending-aortic dimensions;
- CT/CTA measurements;
- MRI/MRA measurements;
- segment-specific maximum diameter;
- prior measurements/growth if explicitly provided.

### CLINICAL_EVIDENCE
Potentially relevant:
- chest/back pain characteristics;
- hemodynamic stability;
- pulse/BP differential;
- neurologic symptoms;
- hypertension history;
- known bicuspid valve/genetic aortopathy only if supplied.

### DEMOGRAPHIC / BODY-SIZE CONTEXT
- age;
- sex;
- height;
- BSA if provided.

---

## 11. Contradicting and conflicting evidence

### Not contradiction by itself
- no chest pain;
- normal blood pressure;
- no known hypertension.

These may reduce support for some etiologic hypotheses but do not negate a radiographic aortic-enlargement finding.

### Direct evidence conflict
Examples:
- AI reports aortic enlargement while trusted human CXR review explicitly reports normal aortic contour/size;
- later reliable imaging directly disputes the original radiographic interpretation.

Emit:

`EVIDENCE_CONFLICT`

and preserve both sources.

### Modality discordance

CXR `Aortic enlargement` plus normal cross-sectional segment measurements is not simply ignored.

Report:
- CXR finding;
- stronger direct measurement evidence;
- possible radiographic/technical contour discrepancy;
- uncertainty.

Do not silently prefer the AI.

---

## 12. Missing evidence

Potential missing fields:
- symptoms and onset;
- hemodynamic stability;
- BP/pulse differential;
- prior imaging comparison;
- direct aortic measurement;
- aortic segment measured;
- age/sex/body size when size interpretation requires normalization;
- hypertension history;
- CT/CTA/MRI/TTE confirmation.

Missing data is not negative evidence.

---

## 13. Safety policy

If case data suggest AAS or another acute unstable aortic process:

emit:
- `ACUTE_AORTIC_SYNDROME_CONCERN`
- `HIGH_PRIORITY_CLINICAL_REVIEW`

This is for urgent human clinical review.

Hermes must not autonomously:
- prescribe anti-impulse therapy;
- choose medications;
- order surgery/endovascular intervention;
- choose contrast/imaging protocols;
- issue procedural instructions.

---

## 14. AI score interpretation

The model score is not automatically:
- probability of aneurysm;
- probability of dissection;
- probability of AAS;
- measured aortic diameter;
- risk of rupture;
- treatment urgency.

Keep separate:

```text
image_model_score
radiographic_aortic_enlargement
direct_aortic_measurement
aortic_disease_hypothesis
AAS_safety_concern
uncertainty
```

Never convert `0.88` into “88% probability of thoracic aortic aneurysm” or “88% probability of dissection”.

---

## 15. Recommended structured output

```yaml
finding: aortic_enlargement
finding_type: radiographic_finding

image_evidence:
  model_score: null
  aortic_contour: unknown
  mediastinal_context: unknown
  prior_change: unknown

direct_aortic_imaging:
  available: false
  modality: unknown
  segment: unknown
  diameter_mm: null
  prior_diameter_mm: null
  growth_rate: unknown

size_context:
  age: unknown
  sex: unknown
  height: unknown
  bsa: unknown

aortic_disease_hypotheses:
  true_aortic_dilatation:
    status: unknown
    evidence: []
  thoracic_aortic_aneurysm:
    status: unknown
    evidence: []
  acute_aortic_syndrome:
    status: unknown
    evidence: []
  chronic_hypertensive_remodeling:
    status: unknown
    evidence: []

supporting_evidence: []
contradicting_evidence: []
missing_evidence: []
conflicts: []

safety:
  priority: routine|elevated|high
  flags: []

assessment:
  summary: ""
  uncertainty: ""
  requires_doctor_review: true

citations: []
```

---

## 16. Prohibited inferences

Hermes MUST NOT:

1. Equate `Aortic enlargement` with thoracic aortic aneurysm.
2. Equate `Aortic enlargement` with aortic dissection.
3. Equate `Aortic enlargement` with acute aortic syndrome.
4. Use a normal chest X-ray to exclude AAS when clinical suspicion is high.
5. Infer a measured aortic diameter from the AI class or CXR score.
6. Apply CT/MRI ascending-aortic numeric definitions directly to the CXR AI class.
7. Diagnose hypertension from aortic-arch enlargement.
8. Treat older age or larger body size as proof that enlargement is benign.
9. Infer segment-specific disease without segment-specific evidence.
10. Infer growth rate without serial measurements.
11. Convert the AI score into aneurysm/dissection probability.
12. Treat missing data as negative evidence.
13. Issue autonomous treatment/procedure orders.
14. Present the draft assessment as the physician's final diagnosis.
15. Add unsourced medical rules.

---

## 17. Evidence gaps for v2

Potential additions:
- bicuspid-aortic-valve-specific pathways;
- Marfan/Loeys-Dietz/nonsyndromic HTAD;
- pregnancy-specific aortic risk;
- arch/descending-aorta segment-specific normal ranges;
- postoperative/post-TEVAR surveillance;
- detailed aortic-growth thresholds;
- dedicated CXR projection/mediastinal-width evidence;
- treatment thresholds for established aneurysm.

Do not invent these detailed rules in v1.

---

## 18. Bottom line

```text
Aortic enlargement AI finding
        ↓
preserve as radiographic evidence
        ↓
check symptoms / AAS red flags
        ↓
HIGH PRIORITY if acute-risk context
        ↓
look for CT/MRI/TTE measurements
        ↓
interpret diameter with segment + age/sex/body size
        ↓
separate dilation / aneurysm / AAS hypotheses
        ↓
hypertension only as contextual association
        ↓
identify missing/conflicting evidence
        ↓
bounded assessment
        ↓
doctor review required
```
