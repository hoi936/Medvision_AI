# SILENT_PROSPECTIVE_CLINICAL_EVALUATION_POLICY.md

## 1. Integration type

Đây là **clinical-evaluation infrastructure**, không phải Hermes skill.

Không sửa `.hermes/skills`.

Khuyến nghị:

```text
AI_model/clinical_evaluation/
├── __init__.py
├── protocol_schema.py
├── deployment_snapshot.py
├── data_source_contract.py
├── silent_ingestion.py
├── silent_isolation.py
├── silent_case_store.py
├── reference_linkage.py
├── reliability_metrics.py
├── semantic_monitoring.py
├── distribution_shift.py
├── incident_log.py
├── protocol_deviation.py
├── prospective_protocol.py
├── readiness.py
└── reporting.py
```

---

## 2. V1 scope

Triển khai scaffold cho:
- SILENT_SHADOW;
- prospective protocol/readiness.

Không triển khai actual clinical connection hoặc live study.

---

## 3. Silent protocol schema

```yaml
silent_protocol:
  protocol_id:
  version:
  objective:
  mode: SILENT_SHADOW

  data_sources: []
  eligibility:
  evaluation_window:
  reference_linkage_rules:

  system_snapshot:
  provider_requirements:

  isolation:
    clinical_visibility: false
    alerts_enabled: false
    ehr_write_enabled: false

  ethics:
    status:
    reference:

  privacy:
    status:
    reference:

  security:
    status:
    reference:
```

---

## 4. Fail-closed readiness

SILENT_READY chỉ khi:
- protocol complete;
- data-source contract present;
- system snapshot frozen;
- provider/frozen-output strategy defined;
- reference linkage defined;
- silent isolation verified;
- ethics/privacy/security statuses resolved as required by host.

Không auto-assume approval.

---

## 5. Silent isolation validator

Bắt buộc verify:

```text
clinical_visibility == false
alerts_enabled == false
ehr_write_enabled == false
doctor_message_enabled == false
clinical_finalization_enabled == false
```

Fail nếu bất kỳ flag nào bật trong SILENT_SHADOW.

---

## 6. Data-source allowlist

Tạo allowlist explicit.

Unknown field:
```text
reject or quarantine
```

Không silently ingest.

---

## 7. Event-time validator

Validate:
- clinical event time;
- ingestion time;
- model run time;
- reference time;

không bị tráo.

Temporal module phải nhận clinical time, không phải ingestion time.

---

## 8. Deployment snapshot

Mỗi run:
- repo commit;
- Hermes version/commit;
- Python;
- skills hash;
- config hash;
- provider/model;
- protocol version.

Không merge result across versions without stratification.

---

## 9. Reference-linkage state machine

```text
REFERENCE_PENDING
REFERENCE_PARTIAL
REFERENCE_COMPLETE
REFERENCE_UNAVAILABLE
```

Only COMPLETE references enter final performance metrics unless metric protocol explicitly allows partial.

---

## 10. Semantic monitoring

Reuse existing invariant engine and provider-backed E2E runner where possible.

Không viết clinical policy lại.

---

## 11. Reliability metrics

Implement:
- ingestion success rate;
- normalization success rate;
- Hermes invocation success;
- parse success;
- complete-trace rate;
- latency percentiles;
- provider transient-failure rate;
- end-to-end availability.

---

## 12. Distribution shift

Scaffold descriptive monitoring for:
- input missingness;
- positive finding frequencies;
- site;
- modality/projection metadata;
- time period;
- relevant protocol metadata.

No automatic adaptation.

---

## 13. Incident log

Schema:

```yaml
incident:
  incident_id:
  case_id:
  deployment_version:
  category:
  severity:
  detected_at:
  description:
  affected_stage:
  contained:
  resolution:
```

Do not include unnecessary direct identifiers.

---

## 14. Protocol deviation log

Separate from incidents.

Examples:
- wrong eligibility;
- wrong version;
- reference missing;
- output exposure;
- wrong data source.

---

## 15. Prospective protocol scaffold

Implement SPIRIT-AI-inspired fields for:
- intended use/users;
- clinical pathway;
- intervention/control;
- AI version;
- input/output handling;
- human-AI interaction;
- error handling;
- endpoint;
- safety/stopping rules;
- ethics/consent.

No actual trial start.

---

## 16. Readiness review

Harness may emit:

```text
INTERVENTIONAL_READINESS_REVIEW_REQUIRED
```

It must not auto-approve:

```text
INTERVENTIONAL_READY
```

unless explicit governance approval object is supplied.

---

## 17. Actual-study explicit authorization

No silent or interventional session may start automatically.

Require:
- explicit authorized start token/event;
- protocol version match;
- deployment snapshot match.

Unit tests only use synthetic authorization fixtures.

---

## 18. Reporting

Generate:
- JSON;
- CSV;
- Markdown.

Separate:
- scaffold readiness;
- blockers;
- silent technical metrics;
- semantic metrics;
- reference-linked metrics;
- incidents;
- deviations;
- no clinical-benefit claim unless appropriate study actually runs.

---

## 19. Unit-test fixtures

Synthetic fixtures for:
- silent isolation pass/fail;
- missing protocol;
- unresolved ethics;
- unresolved security;
- data-source unknown field;
- event-time mismatch;
- reference pending;
- version mismatch;
- incident logging;
- protocol deviation;
- readiness review;
- no auto-transition to interventional.

Synthetic data never reported as clinical results.

---

## 20. Exit criteria scaffold

Can report:

```text
SILENT / PROSPECTIVE CLINICAL EVALUATION HARNESS: IMPLEMENTED
```

if infrastructure/tests pass.

Without actual configured study:

```text
SILENT CLINICAL EVALUATION: NOT RUN
PROSPECTIVE INTERVENTIONAL EVALUATION: NOT RUN
```

No clinical benefit claim.
