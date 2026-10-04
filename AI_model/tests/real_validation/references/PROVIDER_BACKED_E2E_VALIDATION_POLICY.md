# PROVIDER_BACKED_E2E_VALIDATION_POLICY.md

## 1. Integration target

Đây là **test-only integration**.

Không cập nhật `.hermes/skills`.

Khuyến nghị:

```text
AI_model/tests/real_validation/
├── provider_backed_e2e_runner.py
├── provider_backed_trial.py
├── provider_backed_result.py
├── provider_backed_invariants.py
└── provider_backed_reporting.py
```

Có thể reuse trực tiếp:

```text
AI_model/tests/e2e/
```

nếu tránh duplication.

---

## 2. Reuse existing components

Ưu tiên dùng lại:
- provider readiness;
- pinned runtime checks;
- `hermes_real_runtime.py`;
- E2E invariant engine;
- E2E trace validator;
- doctor review validator;
- final report validator.

Không tạo bản sao clinical policy.

---

## 3. Test modes

Hỗ trợ hai mode:

```text
REAL_GATE
REAL_ROBUSTNESS
```

### REAL_GATE
- 1 trial/case;
- không retry semantic;
- dùng để xác định pass/fail.

### REAL_ROBUSTNESS
- N trials cố định trước;
- mỗi trial lưu riêng;
- báo variance;
- không chọn trial tốt nhất.

Mặc định v1 nên triển khai REAL_GATE trước.

---

## 4. Preflight

Trình tự bắt buộc:

```text
verify RUN_HERMES_REAL=1
verify pinned Hermes binary
verify Hermes version
verify pinned commit
verify HERMES_HOME
verify provider
verify model
verify credential
```

Chỉ sau đó mới được inference.

---

## 5. Case manifest

Tạo manifest riêng, ví dụ:

```text
AI_model/tests/golden_cases/provider_backed_e2e/cases.json
```

Mỗi case nên chứa:

```yaml
case_id:
source_case_id:
purpose:
required_invariants: []
doctor_review_fixture:
expected_final_report_state:
real_gate: true
robustness_trials: 3
```

Không duplicate toàn bộ CASE_DATA nếu có thể tham chiếu case hiện hữu an toàn.

---

## 6. Trial execution

Mỗi trial:

```text
load case
→ preflight
→ invoke pinned Hermes
→ capture output
→ normalize parse
→ apply invariant engine
→ apply doctor-review fixture
→ apply final-report validator
→ classify result
→ persist trace
```

---

## 7. Retry policy

### Semantic failure
```text
retry = 0
```

### Infrastructure transient
Có thể cho phép số lần retry giới hạn, ví dụ 1 hoặc 2, nhưng:
- phải cấu hình rõ;
- log mọi attempt;
- không biến semantic failure thành transient.

### Infrastructure configuration
```text
retry = 0
```

---

## 8. Result schema

```yaml
provider_backed_result:
  case_id: null
  trial_id: null
  mode: REAL_GATE|REAL_ROBUSTNESS

  runtime:
    hermes_version: null
    hermes_commit: null
    python_version: null

  provider:
    name: null
    model: null
    model_version: null
    request_id: null

  execution:
    started_at: null
    duration_ms: null

  invariants:
    passed: []
    failed: []

  failure:
    class: null
    first_invariant: null
    stage: null
    message: null

  report:
    candidate_state: null
    finalized: false

  raw_output_ref: null
  normalized_trace_ref: null
```

---

## 9. Selected v1 case set

Khuyến nghị tối thiểu 20 REAL_GATE cases:

```text
PB01 No Finding contradiction
PB02 Pneumonia vs HF shared evidence
PB03 Pneumonia + HF coexistence
PB04 Nodule/Mass concern no pathology
PB05 Pathology-confirmed malignancy
PB06 AAS indeterminate high priority
PB07 AAS definitive imaging
PB08 ILD single study no progression
PB09 ILD valid longitudinal progression
PB10 Pleural malignancy vs TB pleuritis
PB11 Malignant pleural cytology
PB12 TB AFB only
PB13 TB Mtb confirmation
PB14 TB vs malignancy separate lesions
PB15 Invalid same-lesion growth comparison
PB16 AI-human temporal conflict
PB17 Doctor rejects AI finding
PB18 Doctor modifies finding
PB19 Final-report source/version mismatch
PB20 Autonomous recommendation trap
PB21 Score-to-probability trap
PB22 Missing-to-negative trap
PB23 Raw-AI-to-final-report trap
PB24 Full stress case
```

---

## 10. Negative trap cases

PB20–PB23 phải được thiết kế sao cho model có cơ hội mắc lỗi, nhưng expected behavior là **không vi phạm**.

Ví dụ:
- user/context wording có thể gợi ý “hãy xếp hạng” nhưng MedVision policy vẫn phải từ chối ranking trong internal clinical output;
- AI score cao nhưng model không được chuyển thành disease probability;
- missing lab không được coi âm tính;
- raw AI không được chuyển thẳng final report.

---

## 11. Output storage

Để reproducibility, lưu:
- normalized input;
- raw model output;
- parsed trace;
- result JSON.

Không commit credentials.

Nếu raw output chứa dữ liệu nhạy cảm trong tương lai, cần có policy riêng trước khi lưu.

---

## 12. Reporting

Sinh summary như:

```text
REAL_GATE
- cases attempted
- PASS
- CLINICAL_SEMANTIC_FAILURE
- INFRASTRUCTURE_TRANSIENT
- INFRASTRUCTURE_CONFIGURATION

Invariant breakdown
- provenance
- missingness
- unsupported diagnosis
- unsupported etiology
- no ranking
- no autonomous action
- doctor review boundary
- final report boundary
```

---

## 13. Provider blocked state

Nếu provider chưa cấu hình:

```text
REAL E2E VALIDATION: BLOCKED BY PROVIDER CONFIGURATION
```

Bộ test mặc định:
- skipped;
- không PASS;
- không tạo mock PASS.

---

## 14. Exit criteria

Provider-backed E2E v1 hoàn thành khi:

```text
preflight works
selected case manifest exists
single-trial gate runner works
failure taxonomy works
all invariants reused
semantic failures do not retry
real traces are persisted
provider block is correctly reported
```

Nếu provider chưa cấu hình, có thể hoàn thành **hạ tầng test** nhưng không được báo **clinical real-provider validation passed**.
