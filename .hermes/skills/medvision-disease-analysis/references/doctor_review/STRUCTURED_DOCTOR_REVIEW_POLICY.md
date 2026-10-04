# STRUCTURED_DOCTOR_REVIEW_POLICY.md

## Integration target

Integrate under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/doctor_review/
├── STRUCTURED_DOCTOR_REVIEW_EVIDENCE.md
├── STRUCTURED_DOCTOR_REVIEW_POLICY.md
└── references.md
```

Do not create a new top-level doctor-review skill.

## Progressive-loading trigger

Load this module when:
- a Hermes assessment/draft report is ready for clinician review;
- any finding/hypothesis requires human accept/modify/reject/defer;
- arbitration contains conflicts or high-priority items;
- a review is reopened after new evidence;
- finalization readiness is being evaluated.

Do not activate during pure upstream AI inference if no review workflow is being performed.

## Workflow procedure

### Step 1 — Freeze source snapshots

Capture references to:
- `AI_RESULT`;
- Hermes assessment;
- arbitration output;
- draft report.

Do not mutate these snapshots during review.

### Step 2 — Start human review

Transition:

```text
DOCTOR_REVIEW_PENDING
→ DOCTOR_REVIEW_IN_PROGRESS
```

Only host-app authenticated clinician actions may populate reviewer identity.

### Step 3 — Review findings

For each required finding use exactly one:

```text
FINDING_ACCEPTED
FINDING_MODIFIED
FINDING_REJECTED
FINDING_DEFERRED
FINDING_UNREVIEWED
```

Doctor-added findings remain clinician-authored and separate from `AI_RESULT`.

### Step 4 — Review disease hypotheses

For each required disease hypothesis use exactly one:

```text
HYPOTHESIS_ACCEPTED
HYPOTHESIS_MODIFIED
HYPOTHESIS_REJECTED
HYPOTHESIS_DEFERRED
HYPOTHESIS_UNREVIEWED
```

Preserve original Hermes state.

### Step 5 — Review conflicts

Each conflict may be:
- resolved;
- preserved;
- deferred.

Do not force resolution.

### Step 6 — Acknowledge high-priority items

Every current high-priority item required by workflow must have explicit clinician acknowledgement before readiness.

Acknowledgement does not imply acceptance.

### Step 7 — Review narrative

Doctor-owned report-level text must be stored separately from the draft.

Do not overwrite the draft snapshot.

### Step 8 — Complete review

Set:

`DOCTOR_REVIEW_COMPLETED`

only when:
- reviewer identity is present;
- completion time is present;
- required items are reviewed or explicitly deferred;
- required high-priority items are acknowledged;
- unresolved items are explicitly represented.

### Step 9 — Evaluate finalization readiness

If all required conditions pass:

`REPORT_READY_FOR_FINALIZATION`

Otherwise:

`REPORT_NOT_FINAL`

with explicit blocking reasons.

### Step 10 — Finalization

Only external authenticated clinician action may set:

`REPORT_FINALIZED_BY_DOCTOR`

Hermes cannot perform this transition.

### Step 11 — New evidence

Before finalization:
- reopen review when clinically relevant new evidence changes reviewed state.

After finalization:
- preserve finalized record;
- create amendment/addendum/new review cycle according to host workflow.

No silent in-place mutation.

## Review ownership

AI/Hermes may:
- present evidence;
- present uncertainty;
- present conflicts;
- draft text;
- identify which items remain unreviewed.

AI/Hermes may NOT:
- act as reviewer;
- accept/reject on behalf of clinician;
- manufacture reviewer identity;
- acknowledge high-priority items;
- finalize.

## Finalization blockers

At minimum, block readiness when any applies:

```text
review status != completed
reviewer id missing
completion timestamp missing
required finding == unreviewed
required hypothesis == unreviewed
required high-priority item not acknowledged
doctor-owned report text missing
blocking conflict not represented
```

A deferred item is not automatically a blocker if:
- defer is an explicit clinician decision;
- unresolved state is retained;
- host workflow permits finalization with deferred uncertainty.

## Audit behavior

Review event history must be append-only in semantics.

Each modification should retain:
- actor;
- timestamp;
- target;
- action;
- prior value;
- new value;
- comment if supplied.

Do not destroy prior review versions.

## Output

Return structured doctor-review state only.

Final-report rendering belongs to the next module:

`Final Report Generation v1`.
