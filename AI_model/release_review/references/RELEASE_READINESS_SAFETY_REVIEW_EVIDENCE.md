# RELEASE_READINESS_SAFETY_REVIEW_EVIDENCE.md

## 0. Mục tiêu

Giai đoạn cuối của roadmap hiện tại là:

**Release-Readiness & Safety Review v1**

Mục tiêu không phải "phát hành hệ thống", mà là xây một cơ chế đánh giá có cấu trúc để trả lời:

```text
Hệ thống đã có đủ bằng chứng, kiểm soát và governance
để chuyển sang bước thử nghiệm/triển khai tiếp theo hay chưa?
```

Đây là một **governance/review harness**, không phải skill lâm sàng.

---

## 1. Release-readiness không phải một điểm số

Không tạo:

```text
Release score = 92/100
```

hoặc một chỉ số tổng hợp duy nhất.

Một hệ thống có thể đạt nhiều mục nhưng vẫn bị chặn bởi một lỗi an toàn nghiêm trọng.

Kết quả phải theo dạng:

```text
READY_FOR_NEXT_GOVERNED_STAGE
NOT_READY
BLOCKED
CONDITIONAL_REVIEW_REQUIRED
```

với lý do cụ thể.

---

## 2. Bốn nhóm review chính

Theo hướng Govern / Map / Measure / Manage:

### GOVERN
- ownership;
- policy;
- authorization;
- versioning;
- change control;
- ethics/privacy/security status;
- incident responsibility.

### MAP
- intended use;
- intended users;
- clinical workflow;
- data sources;
- foreseeable misuse;
- known limitations;
- system boundaries.

### MEASURE
- regression evidence;
- provider-backed evidence;
- dataset evaluation;
- human-AI evaluation;
- silent/prospective evidence;
- safety incident rates;
- reliability and latency.

### MANAGE
- mitigation;
- rollback;
- monitoring;
- incident response;
- change management;
- release blocking;
- post-release review.

---

## 3. Evidence maturity levels

Không phải mọi evidence đều có cùng độ mạnh.

Đề xuất:

```text
LEVEL_0_NOT_AVAILABLE
LEVEL_1_SYNTHETIC_OR_UNIT
LEVEL_2_INTERNAL_RETROSPECTIVE
LEVEL_3_EXTERNAL_OR_INDEPENDENT_RETROSPECTIVE
LEVEL_4_HUMAN_AI_READER_STUDY
LEVEL_5_SILENT_PROSPECTIVE
LEVEL_6_INTERVENTIONAL_PROSPECTIVE
```

Maturity level mô tả loại bằng chứng, không phải chất lượng tự động.

Ví dụ:
- một reader study kém thiết kế không mạnh hơn một retrospective study tốt chỉ vì level cao hơn;
- maturity không thay thế quality assessment.

---

## 4. Current MedVision evidence map

Hiện tại phần đã có chủ yếu thuộc:

```text
LEVEL_1_SYNTHETIC_OR_UNIT
LEVEL_2_INTERNAL_RETROSPECTIVE / internal deterministic harness
```

Các phần sau chưa chạy thực tế:

```text
independent dataset evaluation
provider-backed real validation
human-AI reader study
silent prospective
interventional prospective
```

Do đó current release readiness phải fail closed cho clinical deployment.

---

## 5. Intended-use lock

Review phải có một intended-use statement được khóa trước khi đánh giá release.

Phải mô tả tối thiểu:
- hệ thống hỗ trợ ai;
- sử dụng ở đâu;
- dùng dữ liệu gì;
- output là gì;
- output không phải là gì;
- bác sĩ giữ quyền quyết định nào;
- action nào bị cấm.

Nếu intended use mơ hồ:

```text
INTENDED_USE_NOT_LOCKED
```

và không được coi là ready.

---

## 6. User and workflow lock

Phải định nghĩa:
- intended user role;
- training requirement;
- workflow position;
- who reviews Hermes output;
- who finalizes report;
- escalation owner.

Không cho release review nếu chưa biết ai là người dùng thật.

---

## 7. System-version lock

Review gắn với một snapshot:

```yaml
release_candidate:
  repository_commit:
  hermes_version:
  hermes_commit:
  python_version:
  provider:
  model:
  provider_model_version:
  skill_tree_hash:
  config_hash:
  ui_version:
  evaluation_artifact_versions:
```

Thay đổi một thành phần quan trọng có thể làm mất hiệu lực một phần evidence.

---

## 8. Change-impact classification

Mỗi thay đổi cần được phân loại:

```text
NON_CLINICAL_LOW_IMPACT
CLINICAL_SEMANTIC_IMPACT
MODEL_PROVIDER_IMPACT
DATA_PIPELINE_IMPACT
UI_HUMAN_FACTORS_IMPACT
SECURITY_IMPACT
WORKFLOW_IMPACT
```

Không coi mọi thay đổi code là tương đương.

---

## 9. Evidence invalidation matrix

Ví dụ:

### Skill clinical rule changed
Phải xem lại:
- module unit tests;
- E2E;
- provider-backed E2E;
- dataset evaluation;
- possibly reader/silent evidence.

### Provider/model changed
Phải xem lại:
- provider-backed E2E;
- frozen assistance;
- dataset evaluation using real model;
- reader study assistance snapshot;
- silent evaluation.

### UI changed
Có thể không invalidate disease semantics,
nhưng có thể invalidate:
- human factors;
- reader study;
- warning visibility;
- provenance comprehension.

### Data ingestion changed
Có thể invalidate:
- temporal correctness;
- missingness;
- silent prospective results.

---

## 10. Release blockers

Hard blockers nên gồm:

```text
unresolved critical semantic failure
doctor-review bypass
autonomous clinical action
silent isolation breach
wrong-patient data binding
critical provenance corruption
provider/runtime pin mismatch
security critical issue unresolved
ethics/privacy/security approval required but unresolved
system version not frozen
no rollback path
```

Các blocker cụ thể phải cấu hình theo target stage.

---

## 11. Stage-specific readiness

Không có một "release" duy nhất.

Phải phân biệt:

```text
READY_FOR_INTERNAL_RESEARCH
READY_FOR_OFFLINE_DATASET_EVALUATION
READY_FOR_READER_STUDY
READY_FOR_SILENT_EVALUATION
READY_FOR_INTERVENTIONAL_STUDY
READY_FOR_PRODUCTION_CLINICAL_USE
```

MedVision hiện không nên tự động đạt các stage sau chỉ từ regression.

---

## 12. Current likely stage

Dựa trên baseline hiện tại:

- internal research harness: mạnh;
- offline evaluation infrastructure: có;
- actual independent evaluation: chưa có;
- actual reader study: chưa có;
- silent evaluation: chưa có;
- interventional: chưa có.

Do đó software có thể ở trạng thái:

```text
READY_FOR_GOVERNED_OFFLINE_EVALUATION_SETUP
```

nhưng chưa đủ bằng chứng để:

```text
READY_FOR_PRODUCTION_CLINICAL_USE
```

Đây là mô tả governance, không phải certification.

---

## 13. Safety case structure

Tạo một "safety case" có cấu trúc:

```yaml
claim:
  id:
  statement:

evidence:
  - artifact:
    version:
    result:

assumptions: []
limitations: []
residual_risks: []
owner:
status:
```

Ví dụ:

```text
Claim:
Hermes không tự final báo cáo.

Evidence:
- doctor review tests
- final report tests
- E2E invariants

Limitation:
real-provider validation chưa chạy.
```

---

## 14. Không dùng test count thay cho evidence quality

Ví dụ:

```text
997 passed
```

là bằng chứng về regression breadth.

Nó không tự chứng minh:
- clinical accuracy;
- real-world safety;
- clinical benefit;
- external generalization.

Release review phải ghi rõ điều này.

---

## 15. Risk register

Mỗi risk:

```yaml
risk:
  risk_id:
  category:
  hazard:
  cause:
  affected_user:
  potential_harm:
  existing_controls:
  evidence:
  residual_risk:
  owner:
  status:
```

Không cần numeric risk score nếu organization chưa có validated rubric.

Có thể dùng categorical:
```text
LOW
MODERATE
HIGH
CRITICAL
```
nếu criteria được định nghĩa trước.

---

## 16. Core MedVision risks cần theo dõi

Ít nhất:
- unsupported diagnosis;
- unsupported etiology;
- missing-as-negative;
- score-as-probability;
- temporal false progression;
- conflict suppression;
- duplicate evidence amplification;
- disease ranking;
- autonomous action;
- doctor-review bypass;
- report auto-finalization;
- wrong snapshot/version;
- stale final report;
- provenance loss;
- provider behavior change;
- UI anchoring;
- silent isolation breach;
- data leakage/wrong patient;
- cybersecurity/provider outage.

---

## 17. Residual-risk acceptance

Software không tự chấp nhận residual risk.

Phải có explicit governance object:

```yaml
risk_acceptance:
  risk_id:
  decision:
  accepted_by:
  role:
  date:
  rationale:
  scope:
```

Hermes không được điền `accepted_by`.

---

## 18. Security readiness

Review tối thiểu:
- secrets not committed;
- provider credentials separated;
- dependency/runtime pinning;
- vulnerability process;
- threat model status;
- logging/access controls;
- data-at-rest/in-transit assumptions;
- external provider dependency;
- fail-safe behavior on outage.

Không tự claim HIPAA/GDPR/FDA cybersecurity compliance.

---

## 19. Privacy readiness

Kiểm tra:
- minimum necessary data;
- de-identification where relevant;
- retention;
- access roles;
- raw model output storage;
- provider data handling;
- logs;
- research vs clinical data boundaries.

Unresolved policy -> blocker for relevant stage.

---

## 20. Provider dependency readiness

Phải ghi:
- provider;
- model;
- SLA assumptions;
- outage behavior;
- model-version drift;
- deprecation plan;
- fallback policy.

MedVision hiện cấm silent fallback model.

Nếu provider thay model không kiểm soát được:
- flag risk;
- require revalidation strategy.

---

## 21. Monitoring plan

Trước silent/interventional/production:
- define metrics;
- define cadence;
- define owners;
- define escalation;
- define pause threshold;
- define version stratification.

Monitoring không được tự sửa model.

---

## 22. Rollback plan

Mỗi governed deployment stage cần:
- rollback trigger;
- rollback owner;
- last-known-good version;
- data compatibility notes;
- communication path.

Không có rollback plan -> blocker cho stage có live deployment.

---

## 23. Incident response

Phải map các incident categories đã có sang:
- severity;
- owner;
- acknowledgement;
- containment;
- root-cause review;
- corrective action;
- evidence preservation.

Không để incident log chỉ là logging thụ động.

---

## 24. Change control

Mọi thay đổi release candidate:
- có ID;
- lý do;
- impact class;
- affected evidence;
- required re-tests;
- reviewer;
- approval.

Không tự thay skill/runtime/provider sau freeze.

---

## 25. Release checklist không thay risk review

Checklist chỉ là index.

Một item "PASS" phải trỏ tới:
- evidence artifact;
- version;
- test result;
- owner.

Không dùng checkbox không có bằng chứng.

---

## 26. Readiness decision object

```yaml
readiness_decision:
  review_id:
  target_stage:
  system_snapshot:
  blockers: []
  conditions: []
  evidence_summary: []
  residual_risks: []
  governance_approval:
    status:
    approved_by:
    approved_at:
  decision:
```

Software không tự điền approval identity.

---

## 27. Readiness states

```text
RELEASE_REVIEW_SCAFFOLD_READY
RELEASE_REVIEW_INCOMPLETE
RELEASE_BLOCKED
CONDITIONAL_REVIEW_REQUIRED
READY_FOR_NEXT_GOVERNED_STAGE
RELEASE_REVIEW_FAILED
```

Không dùng:

```text
CLINICALLY_SAFE
FDA_READY
PRODUCTION_SAFE
```

trừ khi có định nghĩa/authority tương ứng.

---

## 28. Current blocker projection

Với baseline hiện tại, likely blockers:

```text
real provider validation not run
independent dataset evaluation not run
reader study not run
silent evaluation not run
ethics/privacy/security determinations absent
actual provider/model absent
```

Đây không phải software failure; là evidence/readiness gaps.

---

## 29. Release-readiness report

Report tách:
- system snapshot;
- target stage;
- evidence inventory;
- passed controls;
- blockers;
- residual risks;
- required next evidence;
- owner;
- decision;
- limitations.

Không dùng một overall score.

---

## 30. Hard constraints

Release-Readiness & Safety Review v1 MUST NOT:

1. tự phê duyệt release;
2. claim regulatory compliance;
3. claim clinical safety từ regression;
4. dùng test count làm clinical performance;
5. bỏ qua evidence chưa chạy;
6. tự accept residual risk;
7. tự chuyển sang interventional/production;
8. đổi provider/model/skills để pass review;
9. tạo composite release score;
10. che critical blocker bằng average metric;
11. thêm autonomous action;
12. làm yếu doctor-control boundary.
