# ACUTE_AORTIC_SYNDROME_POLICY.md

## Integration target

Integrate under existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/acute_aortic_syndrome/
├── ACUTE_AORTIC_SYNDROME_EVIDENCE.md
├── ACUTE_AORTIC_SYNDROME_POLICY.md
└── references.md
```

Do not create `medvision-acute-aortic-syndrome`.

## Progressive-loading trigger

Load this module when one or more is present:

1. Canonical AI/imaging:
   - `Aortic enlargement`
   - explicit widened mediastinum / abnormal aortic contour
2. Clinical concern:
   - abrupt severe chest/back/abdominal pain
   - syncope
   - focal neurologic deficit
   - pulse deficit
   - significant inter-arm BP differential
   - shock/hypotension
   - new AR murmur
   - limb/mesenteric/renal ischemia concern
3. Known aortic risk:
   - thoracic aneurysm
   - genetic aortopathy
   - BAV-associated aortopathy
   - prior aortic intervention
4. Definitive imaging/report explicitly raises or confirms AAS.

Do not activate on unrelated findings alone.

## Reasoning procedure

### Step 1 — Preserve image evidence
Aortic enlargement remains a radiographic finding, not a diagnosis.

### Step 2 — Gather acute syndrome features
Use only supplied symptoms/signs/exam data.

### Step 3 — Gather known aortic risk context
Missing stays unknown.

### Step 4 — Handle biomarkers conservatively
No hidden D-dimer rule-out algorithm.
No hidden AAD-RS/AORTAs calculation.

### Step 5 — Check definitive imaging
CTA/TEE/MRI explicit AAS evidence outranks CXR for anatomy/diagnosis while preserving all provenance.

### Step 6 — Assign bounded state

```text
aortic CXR finding only
→ AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT

acute high-risk syndrome +/- aortic CXR clue
→ ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED

partial/incomplete acute evidence
→ ACUTE_AORTIC_SYNDROME_CONCERN_INDETERMINATE

trusted contradictory evidence
→ ACUTE_AORTIC_SYNDROME_CONCERN_CONFLICTED

definitive aortic imaging explicitly confirms AAS
→ DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS
```

### Step 7 — Subtype
Only preserve explicit subtype.
Otherwise `AAS_SUBTYPE_UNRESOLVED`.

### Step 8 — Malperfusion
Emit `MALPERFUSION_CONCERN` only when supplied evidence supports it.

### Step 9 — Safety
High-risk AAS concern propagates to existing `HIGH_PRIORITY_CLINICAL_REVIEW`.

No autonomous imaging/order/treatment/procedure/disposition.

### Step 10 — Output
Return:
- disease concern state;
- subtype;
- CXR/advanced imaging evidence;
- acute clinical features;
- risk context;
- biomarkers;
- malperfusion;
- competing diagnoses;
- conflict/missing evidence;
- safety;
- doctor review.
