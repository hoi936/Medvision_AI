# NO_FINDING_EVIDENCE.md

## 0. Scope

Tài liệu này định nghĩa **No finding semantics + contradiction policy** cho MedVision Hermes sau khi đã tích hợp đủ 14 positive VinBigData finding skills.

Đây **không phải finding skill thứ 15**.

`No finding` phải được xử lý ở tầng:
- canonical AI evidence;
- evidence fusion;
- contradiction detection;
- safety/clinical context;

không phải bằng một `medvision-no-finding` skill riêng.

Canonical competition label:

`No finding`

## 1. Primary source semantics

### S1 — VinDr-CXR 2022

VinDr-CXR có:
- 22 local labels;
- 6 global labels.

`No finding` là một global label.

VinDr Lab còn có rule kiểm tra annotation để ngăn radiologist:
- đánh dấu lesion/local finding;
- đồng thời chọn `No finding`.

Điều này cho thấy trong source taxonomy, `No finding` và presence của radiographic findings là semantically exclusive.

### S2 — Official VinBigData competition specification

VinBigData competition dùng:
- class IDs `0..13` cho 14 findings;
- class `14` cho `No finding`.

Official specification nêu rằng `No finding` được dùng để biểu diễn **absence of all 14 findings above**.

### S3 — VinDr-CXR clinical deployment 2022

VinDr-CXR AI output được đánh giá so với radiology reports trong real-world workflow.

Performance giảm đáng kể khi chuyển từ retrospective/in-lab sang clinical deployment.

Vì vậy AI normal/abnormal or no-finding output phải được giữ là model evidence, không phải final clinical truth.

---

## 2. Core semantic rule

`No finding` means:

`NO_TARGET_FINDING_IDENTIFIED_WITHIN_THE_14_CLASS_VINBIGDATA_TAXONOMY`

It does NOT automatically mean:
- healthy patient;
- no disease;
- no symptoms;
- no physiologic abnormality;
- no abnormality outside the 14-class taxonomy;
- no abnormality on another imaging modality;
- normal laboratory data;
- no need for doctor review.

Suggested MedVision status:

`NO_FINDING_WITHIN_14_CLASS_TAXONOMY`

This is **MEDVISION_SYSTEM_POLICY**.

---

## 3. No finding is not a finding skill

Do NOT create:

`medvision-no-finding`

Do NOT map:

```python
"No finding": "..."
```

to any finding-specific skill.

If `No finding` is POSITIVE and all 14 positive finding classes are not POSITIVE:

```text
medvision-evidence-fusion
→ medvision-safety-check
→ medvision-disease-analysis
```

No finding-specific skill is inserted.

Discovery count must therefore remain unchanged.

---

## 4. Positive No finding + zero positive target findings

If:

```text
No finding == POSITIVE
AND
none of the 14 target findings == POSITIVE
```

Hermes should preserve:

```yaml
no_finding_status: positive
interpretation: no_target_finding_identified_within_14_class_taxonomy
```

Do NOT write:
- "normal patient";
- "no disease";
- "healthy";
- "all chest pathology excluded".

Missing or unmodeled abnormalities remain possible.

---

## 5. Positive No finding + one or more positive findings

This is an internal semantic contradiction.

Example:

```text
No finding == POSITIVE
Pneumothorax == POSITIVE
```

or:

```text
No finding == POSITIVE
Pleural effusion == POSITIVE
Cardiomegaly == POSITIVE
```

### Required behavior

Preserve:
- raw `No finding` result;
- every positive finding result;
- scores/provenance.

Emit:

`NO_FINDING_CONTRADICTION`

as **MEDVISION_SYSTEM_POLICY**.

It may be represented as a subtype of:

`EVIDENCE_CONFLICT`

Do NOT:
- suppress positive findings;
- convert positive findings to negative;
- discard `No finding`;
- choose which AI class is "correct" automatically.

All positive finding skills continue to be selected exactly as before.

---

## 6. Why positive findings must still route

The frozen selector contract is:

```text
finding-specific skill selected
iff
canonical finding decision == POSITIVE
```

`No finding` must not become a gate that overrides this contract.

Therefore:

```text
No finding POSITIVE
+
Nodule/Mass POSITIVE
```

still selects:

`medvision-nodule-mass`

while evidence fusion records the contradiction.

This preserves:
- potentially important positive radiographic evidence;
- raw model provenance;
- human reviewability.

---

## 7. Multiple positive findings + No finding

If `No finding` is POSITIVE with multiple positive target findings:

- preserve all findings;
- select every positive finding skill once;
- create one structured contradiction object listing the conflicting positive findings;
- do not create one duplicate contradiction object per skill unless the existing schema requires it.

Suggested:

```yaml
no_finding_conflict:
  present: true
  type: NO_FINDING_CONTRADICTION
  conflicting_positive_findings:
    - Pleural effusion
    - Cardiomegaly
```

No ordering implies clinical priority.

---

## 8. No finding NEGATIVE

If:

`No finding == NEGATIVE`

this means only that the model did not make a positive No-finding decision.

It is NOT automatically evidence that:
- a radiographic abnormality is present;
- one of the 14 findings must be present;
- the image is abnormal.

### Case A

```text
No finding NEGATIVE
Nodule/Mass POSITIVE
```

This is semantically compatible.

Select Nodule/Mass as usual.

### Case B

```text
No finding NEGATIVE
all 14 findings NEGATIVE
```

Do NOT infer:
- normal;
- abnormal;
- hidden disease.

Use:

`no_finding_status: not_established`

and preserve uncertainty.

---

## 9. Missing No finding result

Missing is not negative.

If the `No finding` field/result is absent:
- do not synthesize a NEGATIVE value;
- do not infer `No finding`;
- do not infer abnormality.

Use:

`no_finding_status: missing`

if the output schema supports it.

---

## 10. Symptoms and labs are not direct contradiction

`No finding` refers to the CXR target-finding taxonomy.

Therefore:

```text
No finding POSITIVE
+
fever
+
dyspnea
```

is NOT automatically an image-evidence contradiction.

Clinical disease can exist without one of these 14 modeled radiographic findings being detected.

Hermes should:
- preserve symptoms/labs;
- preserve No finding;
- keep disease hypotheses separate;
- continue safety reasoning.

---

## 11. Severe clinical state can override complacency, not evidence provenance

If `No finding` is POSITIVE but independent evidence shows:
- severe respiratory distress;
- marked hypoxemia;
- hemodynamic instability;
- another high-risk syndrome;

emit:

`HIGH_PRIORITY_CLINICAL_REVIEW`

when existing safety policy requires it.

Do NOT reinterpret No finding as proof that the patient is safe.

Do NOT autonomously diagnose/treat.

---

## 12. Human or CT disagreement

Examples:

```text
AI: No finding POSITIVE
Human CXR: focal abnormality present
```

or:

```text
AI: No finding POSITIVE
CT: corresponding thoracic abnormality present
```

Preserve both sources.

Emit:

`EVIDENCE_CONFLICT`

The more specific human/CT evidence may characterize the abnormality, but the AI output remains in the audit trail.

---

## 13. Human agreement

Example:

```text
AI: No finding POSITIVE
Radiologist: no target abnormality identified on CXR
```

This is concordant image evidence.

But still do NOT infer:
- no disease;
- no symptoms;
- no pathology outside the target taxonomy.

---

## 14. Score semantics

`No finding` model score is not automatically:
- probability that the patient is healthy;
- probability of no disease;
- probability that all thoracic pathology is absent;
- negative predictive value;
- safety probability.

Example:

```text
No finding score = 0.96
```

must NOT become:

```text
96% probability of being healthy
```

Keep:

```text
image_model_score
no_finding_decision
target_finding_decisions
clinical_evidence
uncertainty
```

separate.

---

## 15. No finding + Other lesion

`Other lesion` is one of the 14 positive competition finding classes.

Therefore:

```text
No finding POSITIVE
Other lesion POSITIVE
```

is a `NO_FINDING_CONTRADICTION`.

Do not treat `Other lesion` as an exception.

---

## 16. All 14 positive + No finding

If all 14 positive finding classes are POSITIVE and `No finding` is also POSITIVE:

- preserve all 15 raw class results;
- select all 14 positive finding skills exactly once;
- do not select a No finding skill;
- emit one No-finding contradiction structure containing all 14 positive findings;
- maintain payload order for finding skills;
- do not infer clinical priority from ordering.

---

## 17. Recommended structured output

```yaml
no_finding:
  present_in_payload: true
  decision: POSITIVE|NEGATIVE|UNKNOWN
  model_score: null
  interpretation: unknown

target_findings:
  positive: []
  negative: []
  missing: []

no_finding_conflict:
  present: false
  type: null
  conflicting_positive_findings: []

supporting_evidence: []
contradicting_evidence: []
missing_evidence: []

safety:
  priority: routine|elevated|high
  flags: []

assessment:
  no_target_finding_within_taxonomy: unknown
  disease_exclusion_supported: false
  requires_doctor_review: true
```

---

## 18. Prohibited inferences

Hermes MUST NOT:

1. Create a fifteenth finding skill for `No finding`.
2. Map `No finding` to `medvision-other-lesion`.
3. Treat `No finding` as "healthy".
4. Treat `No finding` as "no disease".
5. Treat `No finding` as absence of abnormalities outside the 14-class taxonomy.
6. Use `No finding` to suppress a POSITIVE target finding.
7. Silently discard `No finding` when a positive finding exists.
8. Automatically decide which conflicting AI class is correct.
9. Treat `No finding NEGATIVE` as proof of abnormality.
10. Convert missing No finding into NEGATIVE.
11. Treat symptoms/lab abnormalities as direct contradiction of the image label by themselves.
12. Ignore severe clinical evidence because No finding is positive.
13. Convert No finding score into probability of health/no disease.
14. Skip doctor review.

---

## 19. Bottom line

```text
No finding result
        ↓
POSITIVE?
├─ yes
│   ↓
│   any of 14 findings POSITIVE?
│   ├─ no  → NO_FINDING_WITHIN_14_CLASS_TAXONOMY
│   │         not "no disease"
│   │
│   └─ yes → preserve everything
│             NO_FINDING_CONTRADICTION
│             select all positive finding skills
│             no automatic winner
│
├─ no/NEGATIVE
│   ↓
│   positive findings?
│   ├─ yes → route them normally
│   └─ no  → No finding not established
│
└─ missing
    → stay missing
```
