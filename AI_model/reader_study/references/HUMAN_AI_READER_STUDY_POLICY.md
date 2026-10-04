# HUMAN_AI_READER_STUDY_POLICY.md

## 1. Integration type

Đây là **evaluation/study infrastructure**, không phải Hermes skill.

Không sửa `.hermes/skills`.

Khuyến nghị:

```text
AI_model/reader_study/
├── study_schema.py
├── protocol.py
├── randomization.py
├── session_manager.py
├── event_log.py
├── frozen_assistance.py
├── endpoints.py
├── mrmc_export.py
├── safety_analysis.py
├── human_ai_analysis.py
└── reporting.py
```

Tests:

```text
AI_model/tests/test_reader_study_schema.py
AI_model/tests/test_reader_study_protocol.py
AI_model/tests/test_reader_study_randomization.py
AI_model/tests/test_reader_study_frozen_assistance.py
AI_model/tests/test_reader_study_endpoints.py
AI_model/tests/test_reader_study_safety_analysis.py
AI_model/tests/test_reader_study_reporting.py
```

---

## 2. Scaffold first

V1 được coi là hoàn thành hạ tầng nếu có:
- study schema;
- protocol validator;
- reader/case manifest;
- condition assignment;
- randomization/counterbalancing;
- washout metadata;
- frozen Hermes assistance binding;
- reader event schema;
- endpoint computation;
- safety analysis;
- MRMC-compatible export;
- reporting;
- unit tests.

Không cần actual clinicians để hoàn thành scaffold.

---

## 3. No fake study

Nếu chưa có:
- dataset;
- reader list;
- complete protocol;
- ethics/privacy determination khi cần;
- provider/frozen Hermes outputs;

thì report:

```text
HUMAN-AI READER STUDY HARNESS: IMPLEMENTED
HUMAN-AI READER STUDY: NOT RUN
```

---

## 4. Study protocol schema

```yaml
study_protocol:
  study_id:
  version:
  objective:
  design: paired_mrmc|other

  conditions:
    - UNAIDED
    - HERMES_ASSISTED

  assistance_mode:
  primary_endpoint:
  secondary_endpoints: []

  dataset_id:
  reference_standard_version:

  readers:
    target_roles: []
    target_experience_range:
    planned_count:

  sessions:
    count:
    washout:
    counterbalanced: true

  randomization:
    method:
    seed:

  training:
    required: true
    training_case_set_id:

  system_snapshot:
  ui_version:

  ethics:
    status:
    determination_reference:
```

---

## 5. Fail-closed protocol validation

Study cannot become READY when:
- primary endpoint missing;
- dataset missing;
- reference standard missing;
- reader plan missing;
- condition definition incomplete;
- randomization absent;
- training cases overlap evaluation cases;
- Hermes snapshot missing for assisted mode;
- ethics status unresolved when host marks determination required.

---

## 6. Reader manifest

```yaml
reader_manifest:
  reader_id:
  role:
  specialty:
  experience_band:
  site:
  prior_ai_experience:
  assigned_sequence:
```

Store categorical bands if exact values are unnecessary.

---

## 7. Case manifest

Reuse independent Clinical Dataset Evaluation cases when configured.

Do not use:
- golden regression cases;
- PB cases;
- E2E fixtures;

as the main reader dataset.

Each case binds:
- case data;
- reference standard;
- frozen Hermes assistance;
- case stratum;
- randomization ID.

---

## 8. Frozen assistance

For Reader Study v1, preferred mode:

```text
precompute Hermes output once per case
validate it
freeze it
hash it
show same snapshot to all assisted readers
```

This makes the human comparison reproducible.

Metadata:

```yaml
frozen_assistance:
  case_id:
  hermes_output_hash:
  repo_commit:
  hermes_version:
  provider:
  model:
  generated_at:
  validation_state:
```

---

## 9. Session sequencing

Support:
- AB sequence;
- BA sequence.

Example:
```text
A = UNAIDED
B = HERMES_ASSISTED
```

Readers are allocated across AB/BA when design requires counterbalancing.

Case order randomized separately per session under fixed reproducible seeds.

---

## 10. Prevent same-session leakage

Within a session:
- no access to reader's prior interpretation of the same case unless protocol explicitly allows;
- no ground truth;
- no other reader output;
- no future outcomes outside protocol.

---

## 11. Reader event logging

Log structured decisions, not thought process.

Do not ask readers to provide chain-of-thought.

Capture:
- timestamps;
- decisions;
- report text;
- review actions;
- confidence if protocol;
- high-priority acknowledgement;
- assistance interactions if UI records them.

---

## 12. Endpoint library

Support deterministic calculation for:

### Accuracy/semantic endpoints
- agreement with reference;
- major error;
- unsafe false upgrade;
- critical miss.

### Workflow endpoints
- total time;
- time to final review;
- report completion.

### Human-AI endpoints
- AI suggestion acceptance;
- AI suggestion modification;
- AI suggestion rejection;
- incorrect-AI acceptance;
- correct-AI rejection;
- assistance-use rate.

### Safety endpoints
- missed high priority;
- unsupported action retained;
- review-boundary failure;
- provenance misunderstanding.

Do not create one composite benefit score.

---

## 13. Statistical export

Provide tidy data suitable for MRMC analysis:

```text
reader_id
case_id
condition
reference
reader_result
score_if_protocol_has_one
correct
time
error_class
```

Scaffold may export for:
- FDA iMRMC-compatible workflows where appropriate;
- R/Python MRMC packages;

but v1 does not need to implement a new MRMC statistical engine from scratch.

---

## 14. Paired difference summaries

For descriptive reporting, can calculate paired reader/case differences.

Inferential MRMC analysis must account for reader and case effects.

Do not use naive independent-observation p-values.

---

## 15. Time analysis

Time metrics need:
- explicit interruption policy;
- pre-specified outlier handling;
- paired comparison where design is paired.

Keep raw time values.

---

## 16. Safety stop logic for research session

If study UI detects software failure:
- mark case/session technical failure;
- do not silently substitute ground truth;
- do not alter reader output.

This is study integrity, not patient safety management because v1 is offline.

---

## 17. Human-factors issue log

Support:

```yaml
human_factors_issue:
  issue_id:
  reader_id:
  case_id:
  condition:
  category:
  severity:
  description:
  ui_component:
  reproducible:
```

Examples:
- provenance unclear;
- AI/doctor authorship confused;
- warning missed;
- conflict presentation misunderstood;
- workflow friction.

---

## 18. Reporting

Generate:
- JSON;
- CSV;
- Markdown study summary.

Summary separates:
- clinical accuracy/semantic results;
- safety;
- time;
- human-AI behavior;
- usability issues.

---

## 19. Study states

Implement:

```text
READER_STUDY_SCAFFOLD_READY
READER_STUDY_PROTOCOL_INCOMPLETE
READER_STUDY_DATASET_MISSING
READER_STUDY_PROVIDER_BLOCKED
READER_STUDY_ETHICS_STATUS_UNRESOLVED
READER_STUDY_READERS_MISSING
READER_STUDY_READY
READER_STUDY_RUNNING
READER_STUDY_COMPLETE
READER_STUDY_FAILED
```

---

## 20. Actual-study gate

Do not begin data collection until:
- protocol frozen;
- system/UI frozen;
- dataset frozen;
- reference standard frozen;
- training set frozen;
- randomization prepared;
- reader list ready;
- required institutional ethics/privacy status documented;
- Hermes assistance generated/frozen;
- data storage path approved.

---

## 21. Exit criteria scaffold

Report:

```text
HUMAN-AI READER STUDY HARNESS: IMPLEMENTED
```

when infrastructure and unit tests pass.

If no actual study:
```text
HUMAN-AI READER STUDY: NOT RUN
```

Do not claim benefit to clinicians/patients.
