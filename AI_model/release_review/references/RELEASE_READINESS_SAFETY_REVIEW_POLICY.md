# RELEASE_READINESS_SAFETY_REVIEW_POLICY.md

## 1. Integration type

Đây là **governance/evaluation infrastructure**.

Không sửa `.hermes/skills`.

Khuyến nghị:

```text
AI_model/release_review/
├── __init__.py
├── review_schema.py
├── evidence_inventory.py
├── system_snapshot.py
├── intended_use.py
├── risk_register.py
├── safety_case.py
├── change_impact.py
├── evidence_invalidation.py
├── security_readiness.py
├── privacy_readiness.py
├── provider_readiness.py
├── monitoring_plan.py
├── rollback_plan.py
├── incident_response.py
├── readiness.py
└── reporting.py
```

---

## 2. V1 là scaffold

Không tự đưa ra production approval.

V1 triển khai:
- schema;
- evidence inventory;
- blocker rules;
- risk register;
- safety-case linkage;
- change-impact mapping;
- readiness state machine;
- reporting.

---

## 3. Target stages

Support:

```text
INTERNAL_RESEARCH
OFFLINE_DATASET_EVALUATION
READER_STUDY
SILENT_EVALUATION
INTERVENTIONAL_STUDY
PRODUCTION_CLINICAL_USE
```

Mỗi target có blocker/evidence requirements khác nhau.

---

## 4. Evidence inventory

Mỗi artifact:

```yaml
evidence_artifact:
  evidence_id:
  category:
  artifact_type:
  path_or_reference:
  version:
  system_snapshot:
  status:
  summary:
  limitations:
```

Không infer PASS từ file tồn tại.

---

## 5. Intended-use validator

Fail readiness nếu thiếu:
- intended user;
- setting;
- input;
- output;
- clinical role;
- prohibited uses;
- doctor-control statement.

---

## 6. Risk register

Implement lifecycle:
```text
OPEN
MITIGATED
ACCEPTANCE_REQUIRED
ACCEPTED
CLOSED
```

Software không được tự chuyển sang ACCEPTED.

---

## 7. Safety case

Mỗi critical safety claim phải có evidence link.

Nếu evidence chưa chạy:
```text
claim.status = INCOMPLETE
```

Không dùng synthetic result thay real-world evidence nếu claim yêu cầu real-world stage.

---

## 8. Change impact

Implement deterministic mapping giữa:
- change type;
- evidence potentially invalidated;
- required re-test groups.

No automatic clinical judgment beyond configured mapping.

---

## 9. Evidence invalidation

Ví dụ rules:
- provider/model change -> invalidate provider-dependent evidence;
- skill clinical semantics change -> invalidate downstream semantic evidence;
- UI warning change -> invalidate affected human-factors evidence;
- ingestion/time mapping change -> invalidate temporal/silent evidence.

Return explicit affected evidence IDs.

---

## 10. Security/privacy status

Store explicit externally supplied status:

```text
NOT_ASSESSED
IN_PROGRESS
RESOLVED
BLOCKING_ISSUE
```

Harness does not perform legal certification.

---

## 11. Monitoring and rollback

For live-stage readiness require:
- monitoring plan;
- owner;
- thresholds/stopping conditions;
- rollback artifact;
- incident response.

Missing -> blocker.

---

## 12. Governance approval

Final stage transition requires:

```yaml
governance_approval:
  status: PENDING|APPROVED|REJECTED
  approved_by:
  role:
  approved_at:
  scope:
```

Harness cannot create APPROVED automatically.

---

## 13. Current baseline import

Create an import/fixture representing current evidence:

```text
997 passed, 365 skipped
17 skills
17/17 hard
17/17 schema
Hermes v0.21.4
silent/prospective harness implemented
actual clinical evaluations not run
provider unset
```

This is baseline metadata only.

---

## 14. Current expected decision test

Synthetic/project-state test should show:

```text
target = OFFLINE_DATASET_EVALUATION
→ may be conditionally ready if dataset/governance configured

target = SILENT_EVALUATION
→ BLOCKED due actual protocol/data/provider/ethics/privacy/security gaps

target = PRODUCTION_CLINICAL_USE
→ BLOCKED due missing real-world evidence and governance
```

Do not hard-code "ready" for actual project; base decision on supplied artifacts/status.

---

## 15. Reporting

Generate:
- JSON;
- CSV evidence matrix;
- Markdown readiness report.

Report:
- target stage;
- blockers;
- evidence;
- residual risks;
- missing evidence;
- governance state;
- explicit no-certification disclaimer.

---

## 16. Unit-test fixtures

Test:
- missing intended use;
- unresolved critical risk;
- provider change invalidation;
- skill change invalidation;
- UI change human-factors invalidation;
- no rollback plan for live stage;
- governance pending;
- critical security blocker;
- real-world evidence missing;
- evidence artifact exists but status incomplete;
- no composite score;
- no auto-approval.

---

## 17. Exit criteria scaffold

Can report:

```text
RELEASE-READINESS & SAFETY REVIEW HARNESS: IMPLEMENTED
```

Actual decision should state target stage separately.

Without governance/evidence:

```text
PRODUCTION CLINICAL RELEASE: NOT APPROVED / NOT ASSESSED FOR DEPLOYMENT
```

Use wording appropriate to project governance, not regulatory certification.
