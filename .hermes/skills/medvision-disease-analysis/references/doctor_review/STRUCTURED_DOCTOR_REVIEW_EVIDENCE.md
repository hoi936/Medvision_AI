# STRUCTURED_DOCTOR_REVIEW_EVIDENCE.md

## 0. Scope

Cross-cutting MedVision workflow module for:

**Structured Doctor Review v1**

This module defines the human-control boundary after Hermes reasoning and before any final report is created.

Frozen workflow:

```text
AI_RESULT
→ Hermes assessment
→ DRAFT_REPORT
→ DOCTOR_REVIEW
→ FINAL_REPORT
```

This module is not:
- a new top-level Hermes skill;
- a disease module;
- a treatment/action engine;
- a regulatory-compliance claim.

Its purpose is to make clinician review explicit, structured, auditable and non-destructive.

---

## 1. Core invariants

```text
AI_RESULT != DOCTOR_REVIEW
DRAFT_REPORT != FINAL_REPORT

Hermes cannot self-approve.
Hermes cannot promote draft → final.
Doctor review is required.

Doctor disagreement != rewrite AI history.
Doctor modification != AI originally predicted the modified value.

Original provenance must remain auditable.
```

The reviewing clinician remains responsible for the patient-specific clinical decision.

---

## 2. Review lifecycle

Allowed workflow states:

```text
DOCTOR_REVIEW_PENDING
DOCTOR_REVIEW_IN_PROGRESS
DOCTOR_REVIEW_COMPLETED
DOCTOR_REVIEW_REOPENED

REPORT_NOT_FINAL
REPORT_READY_FOR_FINALIZATION
REPORT_FINALIZED_BY_DOCTOR
```

Nominal transition:

```text
PENDING
→ IN_PROGRESS
→ COMPLETED
→ READY_FOR_FINALIZATION
→ FINALIZED_BY_DOCTOR
```

If clinically relevant new evidence arrives before finalization:

```text
PENDING/IN_PROGRESS/COMPLETED
→ DOCTOR_REVIEW_REOPENED
```

If new evidence arrives after a report has already been finalized:
- do not silently mutate the finalized report;
- create a new review cycle, amendment/addendum workflow, or new report version according to the host system;
- preserve the original final report as historical provenance.

Use:

`REVIEW_NEW_EVIDENCE_AFTER_FINALIZATION`

when applicable.

---

## 3. Review levels

Doctor review operates at three distinct levels:

1. finding-level review;
2. disease-hypothesis-level review;
3. report-level review.

These levels must not be collapsed.

A clinician may:
- accept an image finding;
- reject or modify a disease hypothesis based on that finding;
- edit the final narrative separately.

Example:

```text
AI finding: Pleural effusion POSITIVE
Doctor finding review: ACCEPT
Hermes HF hypothesis: SUPPORTED
Doctor hypothesis review: MODIFY → HF remains possible, not established
```

This is valid and must remain representable.

---

## 4. Finding-level decisions

Allowed finding review states:

```text
FINDING_ACCEPTED
FINDING_MODIFIED
FINDING_REJECTED
FINDING_DEFERRED
FINDING_UNREVIEWED
```

### ACCEPT

Doctor agrees with the reviewed finding as represented.

`ACCEPT` does not imply:
- agreement with every disease hypothesis using the finding;
- agreement with AI confidence/score;
- agreement with downstream treatment.

### MODIFY

Doctor accepts that an abnormality exists but changes clinically relevant representation.

Examples:
- laterality;
- location;
- morphology;
- extent;
- severity wording;
- identity correspondence;
- finding label if clinician interpretation differs.

The original AI finding remains unchanged in `AI_RESULT`.

Doctor-authored refinement belongs in `DOCTOR_REVIEW`.

### REJECT

Doctor does not accept the AI finding.

Do not rewrite:

```text
AI_RESULT:
  Nodule/Mass: POSITIVE
```

into:

```text
AI_RESULT:
  Nodule/Mass: NEGATIVE
```

Instead:

```yaml
AI_RESULT:
  Nodule/Mass:
    decision: POSITIVE

DOCTOR_REVIEW:
  finding:
    decision: FINDING_REJECTED
    comment: "..."
```

### DEFER

Doctor explicitly leaves the finding unresolved pending more information.

`DEFER` is an active human decision, not the same as unreviewed.

### UNREVIEWED

No clinician decision has been recorded.

This state can block finalization when review is required.

---

## 5. Finding added by doctor

A doctor may identify a clinically relevant finding that the AI did not report.

Represent it as a doctor-authored finding:

```yaml
doctor_added_finding:
  source: DOCTOR_REVIEW
  finding: "..."
  provenance: clinician
```

Do not backfill it into `AI_RESULT`.

Do not claim the AI detected it.

If it maps to a canonical VinBigData class, that does not retroactively select the finding skill for the original AI result.

---

## 6. Hypothesis-level decisions

Allowed disease-hypothesis review states:

```text
HYPOTHESIS_ACCEPTED
HYPOTHESIS_MODIFIED
HYPOTHESIS_REJECTED
HYPOTHESIS_DEFERRED
HYPOTHESIS_UNREVIEWED
```

### ACCEPT

Doctor accepts the Hermes bounded disease assessment.

This does not create a stronger confirmation state than the underlying evidence allows.

Example:

```text
Hermes: PNEUMONIA_HYPOTHESIS_SUPPORTED
Doctor: ACCEPT
```

does not become microbiologically confirmed pneumonia.

### MODIFY

Doctor changes:
- support state;
- wording;
- disease scope;
- uncertainty;
- relationship to competing hypotheses;
- current/active vs historical interpretation.

The doctor-authored assessment must remain separate from the Hermes draft state.

### REJECT

Doctor does not accept that hypothesis for the reviewed report.

Original Hermes reasoning remains auditable.

### DEFER

Doctor explicitly leaves the hypothesis unresolved pending more evidence.

This is especially relevant for:
- pathology;
- CT/HRCT;
- microbiology;
- follow-up imaging;
- specialist/MDD assessment.

### UNREVIEWED

No human decision recorded.

---

## 7. Doctor review cannot manufacture evidence

Doctor review can express professional judgment, but the data model must distinguish:

```text
doctor judgment
```

from:

```text
source evidence
```

Example:

```yaml
doctor_assessment:
  statement: "Likely pneumonia"
  source: clinician_judgment
```

must not be converted into:

```yaml
microbiology:
  positive: true
```

or:

```yaml
imaging:
  consolidation: confirmed
```

unless those sources actually exist.

Doctor-authored judgment is valid clinical evidence of a clinician's assessment, but it must retain its provenance.

---

## 8. Review of uncertainty and missing information

The review UI/data contract should expose:
- known evidence;
- missing evidence;
- unresolved conflicts;
- competing hypotheses;
- safety priority;
- temporal limitations.

Doctor decisions should not silently convert missing information into negative findings.

Example:

```text
CT not performed
```

must remain missing even if the doctor rejects a CT-dependent hypothesis.

---

## 9. High-priority review items

Any existing safety/review state marked high priority must be explicitly surfaced.

Use:

`REVIEW_ACKNOWLEDGED_HIGH_PRIORITY_ITEM`

when the doctor has actively acknowledged the item.

A high-priority item can be:
- accepted;
- modified;
- rejected;
- deferred;

but it must not remain silently unreviewed if the workflow is being finalized.

Acknowledge does not mean agree.

---

## 10. Conflict review

If Hermes/arbitration preserves a conflict, the doctor may:
- resolve it;
- preserve it;
- defer it.

If unresolved at completion:

`REVIEW_CONFLICT_PRESERVED`

The final reviewed narrative may explicitly state uncertainty.

Do not force conflict resolution solely to enable finalization.

---

## 11. Finalization readiness

`REPORT_READY_FOR_FINALIZATION` may be set only when all required workflow conditions are met.

Minimum conditions:

```text
doctor_review.status == completed
reviewer identity present
review completion timestamp present
required findings reviewed or explicitly deferred
required hypotheses reviewed or explicitly deferred
high-priority items acknowledged
report-level reviewed text present
unresolved items explicitly represented
```

The system may implement stricter host-workflow requirements.

`DEFER` can be compatible with completion when the unresolved state is explicit.

`UNREVIEWED` required items cannot be silently treated as accepted.

---

## 12. Finalization authority

Only an authenticated clinician-authorized action may create:

`REPORT_FINALIZED_BY_DOCTOR`

Hermes must never:
- infer that review is complete;
- set the finalization actor;
- fabricate reviewer identity;
- fabricate review timestamp;
- auto-finalize after a timeout;
- finalize because all AI findings were accepted.

Finalization is an external human action.

---

## 13. Reviewer identity

Recommended fields:

```yaml
reviewer:
  id: null
  role: physician
  display_name: null
  organization: null
```

Authentication/authorization is owned by the host application.

Hermes must not fabricate identity.

This document does not claim compliance with 21 CFR Part 11, HIPAA, GDPR, e-signature law, or local medical-record law. Those require separate product/legal implementation.

---

## 14. Review timestamps

Preserve:
- review started time;
- individual review-event times if available;
- review completed time;
- finalization time.

Do not use:
- ingestion time;
- file modification time;
- AI inference time;

as substitutes for clinician-action time.

Missing timestamps remain missing.

---

## 15. Audit trail

Recommended event-sourced review log:

```yaml
review_events:
  - event_id: R1
    timestamp: null
    actor_id: null
    actor_role: physician
    target_type: finding|hypothesis|report|conflict|priority_item
    target_id: null
    action: accept|modify|reject|defer|acknowledge|reopen|complete|finalize
    before: null
    after: null
    comment: null
```

Audit principles:
- append-only event history;
- no silent deletion;
- before/after representation when modified;
- actor and timestamp preserved when provided;
- provenance of AI/Hermes snapshots preserved.

Implementation details belong to the host system.

---

## 16. Snapshot separation

Recommended immutable references:

```yaml
audit:
  ai_snapshot_id: null
  hermes_snapshot_id: null
  draft_report_snapshot_id: null
  review_version: 1
```

Doctor edits create review-layer data, not mutation of source snapshots.

---

## 17. Doctor edits and AI provenance

Example:

```text
AI:
Pleural effusion POSITIVE

Doctor:
small RIGHT pleural effusion
```

Correct interpretation:

```text
AI detected Pleural effusion.
Doctor refined laterality/size.
```

Incorrect interpretation:

```text
AI detected a small right pleural effusion.
```

The added details are doctor-authored.

---

## 18. Doctor rejection and disease reasoning

If a doctor rejects an upstream finding used by Hermes:
- preserve original Hermes assessment;
- mark the related current reviewed hypothesis as modified/rejected as appropriate;
- do not retroactively mutate the earlier reasoning trace.

A new post-review draft may be generated from reviewed states later, but provenance remains explicit.

---

## 19. Re-review after new evidence

If new pathology, microbiology, CT, HRCT, echo, or other clinically relevant evidence arrives before finalization:
- review may be reopened;
- affected findings/hypotheses should be flagged;
- unaffected reviewed items need not be erased.

Use:

`DOCTOR_REVIEW_REOPENED`

If new evidence arrives after finalization:
- do not alter the finalized record in place;
- create an amendment/addendum/new review cycle according to host policy.

---

## 20. Final report is downstream

Structured Doctor Review does not itself generate the final report.

It produces reviewed, human-owned structured state suitable for:

```text
Final Report Generation v1
```

Final-report generation must consume doctor-reviewed state, not raw AI/Hermes state directly.

---

## 21. Recommended data contract

```yaml
doctor_review:
  review_id: null
  status: pending|in_progress|completed|reopened
  version: 1

  reviewer:
    id: null
    role: physician
    display_name: null

  timestamps:
    started_at: null
    completed_at: null

  finding_reviews:
    - finding_id: null
      ai_snapshot_ref: null
      ai_state: null
      decision: accept|modify|reject|defer|unreviewed
      doctor_value: null
      comment: null
      reviewed_at: null

  doctor_added_findings: []

  hypothesis_reviews:
    - hypothesis_id: null
      hermes_snapshot_ref: null
      hermes_state: null
      decision: accept|modify|reject|defer|unreviewed
      doctor_assessment: null
      comment: null
      reviewed_at: null

  conflict_reviews:
    - conflict_id: null
      decision: resolve|preserve|defer
      resolution: null

  priority_item_reviews:
    - item_id: null
      priority: high|elevated|routine
      acknowledged: false
      decision: null

  report_review:
    draft_snapshot_ref: null
    doctor_impression: null
    doctor_findings_text: null
    doctor_comment: null

  unresolved_items: []

  audit:
    ai_snapshot_id: null
    hermes_snapshot_id: null
    draft_report_snapshot_id: null
    review_events: []

  finalization:
    readiness: not_ready|ready
    blocking_reasons: []
    finalized: false
    finalized_by: null
    finalized_at: null
```

---

## 22. Hard constraints

Hermes MUST NOT:

1. Mutate `AI_RESULT` to reflect doctor disagreement.
2. Mutate historical Hermes reasoning to look doctor-authored.
3. Treat doctor modification as an original AI prediction.
4. Delete rejected AI findings from provenance.
5. Delete rejected Hermes hypotheses from provenance.
6. Treat `DEFER` as `ACCEPT`.
7. Treat `UNREVIEWED` as `ACCEPT`.
8. Fabricate reviewer identity.
9. Fabricate review/finalization timestamps.
10. Auto-complete doctor review.
11. Auto-acknowledge high-priority items.
12. Auto-finalize a report.
13. Promote `DRAFT_REPORT` directly to `FINAL_REPORT`.
14. Let AI acceptance count as physician approval.
15. Hide unresolved conflicts to enable finalization.
16. Turn missing evidence into negative evidence.
17. Create pathology/microbiology/imaging evidence from doctor opinion alone.
18. Silently mutate a finalized report after new evidence.
19. Merge audit events destructively.
20. Claim regulatory/legal compliance from this workflow design alone.
21. Issue autonomous treatment/testing/procedure/disposition actions.
22. Omit the doctor-review requirement.
