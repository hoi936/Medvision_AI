# CLINICAL_DATASET_EVALUATION_POLICY.md

## 1. Đây là evaluation harness, không phải skill

Không thêm `.hermes/skills`.

Khuyến nghị layout:

```text
AI_model/evaluation/
├── dataset_schema.py
├── dataset_loader.py
├── reference_standard.py
├── evaluation_runner.py
├── metrics.py
├── confidence_intervals.py
├── subgroup_analysis.py
├── error_analysis.py
└── reporting.py
```

Tests:

```text
AI_model/tests/test_evaluation_dataset_schema.py
AI_model/tests/test_evaluation_metrics.py
AI_model/tests/test_evaluation_reference_standard.py
AI_model/tests/test_evaluation_split_integrity.py
AI_model/tests/test_evaluation_reporting.py
```

---

## 2. Phase A — Scaffold trước khi có dataset thật

Có thể hoàn thành mà chưa có dữ liệu thật:
- schema;
- split validator;
- reference-standard contract;
- metric implementation;
- CI implementation;
- system snapshot;
- synthetic unit fixtures;
- report generator.

Không được báo "dataset evaluation passed" khi chưa có dataset thật.

---

## 3. Dataset manifest

Tạo schema, ví dụ:

```yaml
dataset_manifest:
  dataset_id:
  dataset_version:
  source:
  institution:
  date_range:
  deidentified: true

  counts:
    patients:
    studies:
    cxr:
    ct:
    longitudinal_cases:

  splits:
    development: []
    validation: []
    evaluation: []

  overlap_checks:
    patient_overlap: false
    study_overlap: false
    golden_case_overlap: false
```

---

## 4. Case format

Tạo JSON schema/Pydantic/dataclass phù hợp project.

Bắt buộc phân biệt:
- missing;
- explicit negative;
- positive;
- unknown.

Không dùng empty string để trộn nhiều trạng thái nếu có thể tránh.

---

## 5. Reference-standard object

```yaml
reference_standard:
  task:
  source_type:
  source_ids: []
  reviewer_count:
  adjudicated:
  confidence:
  limitations: []
  label:
```

Không tự map mọi task về một label binary.

---

## 6. Metrics module

Implement deterministic metrics cho:
- binary finding tasks;
- multiclass/bounded-state tasks;
- safety violation rates;
- temporal states;
- arbitration invariants;
- report fidelity fields.

Mỗi result:
- numerator;
- denominator;
- estimate;
- CI nếu áp dụng.

---

## 7. No single aggregate score

Không tạo:

```text
MedVision score = 92/100
```

hoặc một weighted composite duy nhất.

Báo dashboard theo từng dimension.

---

## 8. System snapshot

Trước mỗi evaluation run, lưu:

```yaml
system_snapshot:
  repo_commit:
  hermes_version:
  hermes_commit:
  python_version:
  provider:
  model:
  config_hash:
  skill_tree_hash:
```

Nếu provider chưa cấu hình, evaluation requiring real reasoning phải BLOCK.

---

## 9. Split integrity validator

Fail nếu:
- patient overlap;
- study duplicate;
- longitudinal patient split across partitions;
- golden case reused as independent evaluation case;
- exact duplicate report/image across protected splits.

---

## 10. Synthetic unit fixtures

Dùng fixtures nhỏ chỉ để test code metric.

Không báo những fixture này như evaluation results.

Ví dụ:
- perfect predictions;
- all wrong;
- all indeterminate;
- one critical violation;
- duplicated patient;
- longitudinal leakage.

---

## 11. Evaluation runner states

```text
EVALUATION_SCAFFOLD_READY
EVALUATION_DATASET_MISSING
EVALUATION_PROVIDER_BLOCKED
EVALUATION_REFERENCE_INCOMPLETE
EVALUATION_READY
EVALUATION_RUNNING
EVALUATION_COMPLETE
EVALUATION_FAILED
```

---

## 12. Pre-run fail-closed

Trước evaluation thật kiểm tra:
- dataset available;
- manifest valid;
- reference standards complete for requested tasks;
- no split leakage;
- system frozen;
- provider/model available nếu task cần real Hermes;
- metrics pre-specified.

---

## 13. Provider-independent evaluation

Một số task có thể đánh giá mà không cần LLM provider:
- split integrity;
- schema;
- reference completeness;
- upstream AI finding metrics nếu predictions đã có sẵn;
- doctor-review/final-report deterministic validators.

Không gọi đó là Hermes real performance.

---

## 14. Provider-backed dataset evaluation

Nếu đánh giá Hermes thật:
- reuse Provider-Backed E2E runner/preflight;
- no retry semantic failures;
- fixed trial policy;
- reuse invariant engine;
- store trace/result.

---

## 15. Primary report

Sinh:
- JSON machine-readable;
- CSV metric tables;
- Markdown summary.

PDF/Word có thể làm sau, không phải core v1.

---

## 16. Error review set

Tạo danh sách lỗi de-identified:

```yaml
error_case:
  case_id:
  category:
  expected:
  observed:
  evidence_refs:
  system_version:
```

Không thay golden expectation dựa trên model output.

---

## 17. Exit criteria cho scaffold v1

Có thể báo:

```text
CLINICAL DATASET EVALUATION HARNESS: IMPLEMENTED
```

khi:
- schemas;
- split integrity;
- reference-standard contract;
- metrics;
- CI;
- reporting;
- unit tests
đều đạt.

Nếu chưa có dataset/provider:

```text
CLINICAL DATASET EVALUATION: NOT RUN
```

---

## 18. Exit criteria cho actual evaluation

Chỉ báo:

```text
CLINICAL DATASET EVALUATION: COMPLETE
```

khi:
- dataset độc lập thực sự đã được chạy;
- reference standards hợp lệ;
- system snapshot frozen;
- all pre-specified metrics reported;
- failures retained;
- limitations documented.

Không tự đổi thành "clinically validated".
