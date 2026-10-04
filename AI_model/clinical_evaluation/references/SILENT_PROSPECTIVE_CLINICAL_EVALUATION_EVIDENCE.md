# SILENT_PROSPECTIVE_CLINICAL_EVALUATION_EVIDENCE.md

## 0. Mục tiêu

Giai đoạn tiếp theo là:

**Silent / Prospective Clinical Evaluation v1**

Mục tiêu là xây hạ tầng cho hai mức đánh giá gần môi trường thật:

```text
SILENT_SHADOW_EVALUATION
```

và sau này:

```text
PROSPECTIVE_INTERVENTIONAL_EVALUATION
```

Trong v1, ưu tiên xây **silent/shadow mode** trước.

---

## 1. Silent/shadow mode là gì

Trong silent mode:

- dữ liệu thật từ workflow lâm sàng có thể được đưa vào hệ thống theo protocol được phê duyệt;
- Hermes chạy song song;
- output Hermes **không hiển thị cho bác sĩ chăm sóc**;
- output Hermes **không ảnh hưởng quyết định điều trị hoặc báo cáo chính thức**;
- kết quả được lưu để so sánh hồi cứu với reference/final clinical outcome phù hợp.

Do đó:

```text
silent output
!= clinical action
```

---

## 2. Không dùng "silent" như cách lách kiểm soát nghiên cứu

Silent mode vẫn có thể liên quan:
- dữ liệu sức khỏe;
- hệ thống bệnh viện;
- quyền truy cập hồ sơ;
- yêu cầu đạo đức/nghiên cứu;
- bảo mật và quản trị dữ liệu.

Harness không tự kết luận silent mode là exempt.

Trước actual deployment phải có quyết định của đơn vị thực hiện.

---

## 3. Prospective interventional mode là giai đoạn sau

Trong prospective interventional mode:
- bác sĩ thực sự thấy output Hermes;
- output có thể ảnh hưởng workflow;
- cần protocol can thiệp rõ hơn;
- cần đánh giá human-AI interaction, use error, safety và outcome.

V1 không tự khởi chạy mode này.

---

## 4. Hai mode phải tách biệt

```text
SILENT_SHADOW
PROSPECTIVE_INTERVENTIONAL
```

Không dùng chung một trạng thái mơ hồ.

Mọi event phải ghi rõ mode.

---

## 5. Silent mode ưu tiên trước

Lý do:
- đo integration reliability;
- đo latency;
- đo missing-input frequency;
- đo parse/runtime failures;
- đo semantic safety;
- phát hiện dataset/workflow shift;
- kiểm tra mapping từ dữ liệu thật vào CASE_DATA;
- không làm thay đổi chăm sóc.

Silent mode là bước giảm rủi ro trước khi cân nhắc interventional mode.

---

## 6. Intake pipeline

Silent pipeline đề xuất:

```text
clinical source systems
→ de-identification / approved secure mapping
→ case ingestion
→ CASE_DATA normalization
→ Hermes
→ invariant checks
→ silent result store
→ reference/outcome linkage
→ offline evaluation
```

Không cho Hermes ghi trực tiếp vào hồ sơ bệnh án trong v1.

---

## 7. Data-source contract

Mỗi nguồn cần định nghĩa:

```yaml
data_source:
  source_id:
  source_type:
  system_name:
  owner:
  ingestion_mode:
  fields_allowed:
  fields_excluded:
  timestamp_semantics:
  update_frequency:
  data_quality_checks:
```

Không tự ingest field ngoài allowlist.

---

## 8. Event-time correctness

Trong môi trường thật, phải phân biệt:
- acquisition time;
- result time;
- report-finalization time;
- ingestion time;
- Hermes-run time.

Không dùng ingestion time thay clinical event time.

Điều này đặc biệt quan trọng cho:
- temporal reasoning;
- microbiology/pathology arriving later;
- amendment;
- current vs historical state.

---

## 9. Version binding

Mỗi silent run phải bind tới:

```yaml
system_snapshot:
  repository_commit:
  hermes_version:
  hermes_commit:
  python_version:
  skill_tree_hash:
  config_hash:
  provider:
  model:
  provider_model_version:
  ui_version: null
```

Nếu system version đổi:
- tạo deployment version mới;
- không gộp metric mà không phân tầng version.

---

## 10. Input completeness monitoring

Ghi các tỷ lệ:
- missing symptoms;
- missing labs;
- missing prior imaging;
- missing timestamps;
- missing modality metadata;
- missing reference standard;
- delayed external results.

Không impute lâm sàng chỉ để tăng completion rate.

---

## 11. Runtime reliability metrics

Silent mode phải đo:

```text
ingestion success
normalization success
Hermes invocation success
parse success
trace completeness
final-report candidate generation success
latency
provider transient failure
provider configuration failure
```

Các metric này tách khỏi clinical correctness.

---

## 12. Semantic safety metrics

Reuse các bất biến hiện có:

```text
PROVENANCE_PRESERVED
MISSING_STAYS_UNKNOWN
NO_SCORE_TO_DISEASE_PROBABILITY
NO_UNSUPPORTED_ETIOLOGY
NO_UNSUPPORTED_DIAGNOSIS
OVERLAP_NOT_DOUBLE_COUNTED
CONFLICT_PRESERVED
SAFETY_ESCALATION_WHEN_SUPPORTED
NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE
DOCTOR_REVIEW_REQUIRED
TEMPORAL_STATE_VALID
ARBITRATION_NO_RANKING
FINAL_REPORT_FROM_REVIEW_ONLY
NO_AUTO_FINALIZATION
```

Silent deployment không được nới lỏng rule vì là dữ liệu thật.

---

## 13. Reference linkage

Silent result có thể được so với:
- final radiology report;
- later CT/HRCT;
- pathology;
- microbiology;
- echo;
- discharge diagnosis;
- adjudicated reference standard;

tùy task.

Không chọn outcome thuận lợi nhất sau khi xem Hermes output.

Reference linkage rule phải pre-specify.

---

## 14. Delayed ground truth

Một số ground truth chỉ có sau:
- vài giờ;
- vài ngày;
- vài tuần.

Do đó mỗi case cần reference status:

```text
REFERENCE_PENDING
REFERENCE_PARTIAL
REFERENCE_COMPLETE
REFERENCE_UNAVAILABLE
```

Không tính pending như negative.

---

## 15. Silent-case state

```yaml
silent_case:
  silent_case_id:
  source_case_id:
  deployment_version:
  ingested_at:
  clinical_event_times:
  hermes_run_id:
  hermes_output_hash:
  invariant_result:
  reference_status:
  outcome_linkage:
```

---

## 16. Silent output isolation

Silent output phải:
- không hiển thị trong clinical viewer;
- không đi vào doctor workflow;
- không tạo alert;
- không tạo recommendation;
- không tạo final report trong EHR;
- không tạo message cho clinician.

Nếu silent output bị lộ vào workflow thật:

```text
SILENT_ISOLATION_BREACH
```

đây là lỗi nghiêm trọng của evaluation infrastructure.

---

## 17. No clinical finalization in silent mode

Dù Hermes tạo draft/candidate trong sandbox:

```text
finalized=false
```

Không tạo:
- doctor identity;
- sign-off;
- report amendment trong hồ sơ thật.

---

## 18. Monitoring for distribution shift

Nếu metadata cho phép, theo dõi:
- site;
- scanner/protocol;
- AP/PA;
- inpatient/outpatient;
- disease prevalence proxy;
- missingness pattern;
- documentation style;
- image-model positive-rate distribution.

Đây là monitoring, không tự điều chỉnh model.

---

## 19. No online learning

Silent/prospective v1 không cho:
- Hermes tự sửa skill;
- model tự fine-tune;
- threshold tự đổi;
- prompt tự thích nghi;
- model fallback âm thầm.

Mọi thay đổi system phải qua version mới.

---

## 20. Prospective protocol fields

Scaffold prospective mode cần hỗ trợ:

```yaml
prospective_protocol:
  objective:
  intended_users:
  intended_use:
  clinical_pathway_position:
  intervention:
  control:
  eligibility:
  primary_endpoint:
  safety_endpoints:
  stopping_rules:
  system_version:
  human_ai_interaction:
  input_failure_handling:
  output_failure_handling:
  ethics_status:
  consent_strategy:
  data_monitoring:
```

---

## 21. Stopping rules

Interventional study protocol phải pre-specify stopping/pause rules.

Ví dụ:
- unexpected harmful recommendation;
- doctor-review bypass;
- repeated critical semantic error;
- system output shown to wrong patient;
- silent isolation breach;
- major data-integrity issue.

Harness không tự chọn numeric thresholds; protocol phải cấu hình.

---

## 22. Incident classification

Hỗ trợ:

```text
TECHNICAL_INCIDENT
DATA_INTEGRITY_INCIDENT
SEMANTIC_SAFETY_INCIDENT
HUMAN_FACTORS_INCIDENT
PRIVACY_SECURITY_INCIDENT
SILENT_ISOLATION_BREACH
PROTOCOL_DEVIATION
```

Không dùng một loại chung "error".

---

## 23. Protocol deviation

Ghi:
- case processed outside eligibility;
- wrong system version;
- wrong input;
- output exposed in silent mode;
- missing required reference;
- clinician saw output before allowed;
- manual override outside protocol.

---

## 24. Prospective interventional output

Nếu sau này activated:
- doctor remains decision-maker;
- all AI content remains advisory;
- doctor review still required;
- autonomous action prohibited;
- final report only after doctor action.

Không thay doctor-control boundary.

---

## 25. Human factors

Prospective workflow phải ghi nhận:
- alert visibility;
- provenance understanding;
- conflict understanding;
- time burden;
- edit burden;
- dismissal/accept behavior;
- use errors.

Không thu hidden chain-of-thought.

---

## 26. Real-world latency

Đo:
- data availability → ingestion;
- ingestion → Hermes start;
- Hermes start → output;
- output → available-to-study-system;
- if interventional: output → clinician viewed.

Không chỉ đo API latency.

---

## 27. Uptime

Đo:
- scheduled evaluation window;
- system available;
- provider available;
- ingestion available;
- end-to-end available.

Tách availability khỏi clinical performance.

---

## 28. Silent evaluation primary outputs

Khuyến nghị dashboard tách:

```text
A. integration reliability
B. data completeness
C. semantic safety
D. reference-linked clinical performance
E. latency/availability
F. distribution shift
G. incident/protocol deviations
```

Không tạo một overall score.

---

## 29. Readiness to move from silent to interventional

Không tự động chuyển phase chỉ vì metric tốt.

Cần explicit review bởi project/study governance.

Harness chỉ có thể tạo:

```text
INTERVENTIONAL_READINESS_REVIEW_REQUIRED
```

không tự set READY dựa trên một điểm.

---

## 30. Ethics/privacy/security boundary

Không tự quyết:
- IRB/ethics exemption;
- consent waiver;
- data-use legality;
- HIPAA/GDPR/local-law compliance;
- cybersecurity approval.

Chỉ lưu trạng thái do tổ chức cung cấp.

---

## 31. Silent/prospective states

```text
CLINICAL_EVAL_SCAFFOLD_READY
SILENT_PROTOCOL_INCOMPLETE
SILENT_DATA_SOURCE_MISSING
SILENT_PROVIDER_BLOCKED
SILENT_ETHICS_STATUS_UNRESOLVED
SILENT_SECURITY_STATUS_UNRESOLVED
SILENT_READY
SILENT_RUNNING
SILENT_COMPLETE
SILENT_FAILED

INTERVENTIONAL_PROTOCOL_INCOMPLETE
INTERVENTIONAL_READINESS_REVIEW_REQUIRED
INTERVENTIONAL_READY
INTERVENTIONAL_RUNNING
INTERVENTIONAL_COMPLETE
INTERVENTIONAL_FAILED
```

---

## 32. Hard constraints

Silent / Prospective Clinical Evaluation v1 MUST NOT:

1. tự kết nối hệ thống bệnh viện;
2. tự tuyển bệnh nhân;
3. tự hiển thị Hermes output cho bác sĩ;
4. tự tác động chăm sóc;
5. tự quyết ethics/privacy/security approval;
6. gọi silent data là prospective clinical benefit;
7. online-learn hoặc tự sửa skill;
8. tự chuyển phase sang interventional;
9. auto-finalize report;
10. tạo autonomous action;
11. bỏ qua provider/version binding;
12. dùng pending outcome như negative.
