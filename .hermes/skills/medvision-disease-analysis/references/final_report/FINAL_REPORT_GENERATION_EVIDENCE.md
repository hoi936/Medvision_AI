# FINAL_REPORT_GENERATION_EVIDENCE.md

## 0. Scope

Cross-cutting MedVision workflow module for:

**Final Report Generation v1**

This module renders a structured final-report candidate only from doctor-reviewed state.

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
- a doctor-review substitute;
- an autonomous finalization/signature authority;
- a treatment/action engine.

---

## 1. Core invariant

```text
Raw AI/Hermes state
!= final report source of truth

Doctor-reviewed state
= only allowed clinical content source for final report rendering
```

Hermes may render text from reviewed state.

Hermes may NOT:
- override doctor modifications;
- restore doctor-rejected items;
- promote deferred/unreviewed items into definitive statements;
- fabricate reviewer identity;
- finalize/sign the report.

---

## 2. Preconditions

Before rendering a final-report candidate, require:

```text
doctor_review.status == completed
doctor_review.finalization.readiness == ready
doctor_review.reviewer.id present
doctor_review.timestamps.completed_at present
doctor-owned reviewed report text/state available
required high-priority items acknowledged
source snapshot references present or explicitly flagged incomplete
```

If conditions fail:

`FINAL_REPORT_BLOCKED_BY_REVIEW`

or:

`FINAL_REPORT_NOT_GENERATABLE`

with blocking reasons.

---

## 3. Source-of-truth precedence for rendering

For each reportable item:

```text
doctor-reviewed value
> doctor-authored modification
> doctor-accepted Hermes/AI value
```

But this precedence applies only to the rendered report, not to historical provenance.

Historical objects remain unchanged.

Example:

```text
AI: Pleural effusion
Doctor: small right pleural effusion
```

Final report may say:

```text
Small right pleural effusion.
```

But audit must still show:
- AI produced generic pleural effusion;
- doctor supplied size/laterality.

---

## 4. Rejected items

Doctor-rejected findings/hypotheses must not appear as current affirmative final-report statements.

They may appear only if:
- the doctor explicitly documents the disagreement/history in the reviewed narrative; or
- an audit/provenance section is being rendered for internal use.

Do not silently delete the source history.

---

## 5. Deferred items

Doctor-deferred items must not be converted into:
- positive findings;
- negative findings;
- confirmed diagnoses.

If the doctor includes them in the final reviewed narrative, preserve bounded language such as:
- indeterminate;
- unresolved;
- pending external evidence;
- cannot be established from available data.

Do not invent the missing study/test.

---

## 6. Unreviewed items

Required unreviewed items block readiness and therefore block final-report generation.

If a non-required item remains unreviewed and host policy permits completion:
- do not promote it into the final report unless doctor-authored reviewed text includes it;
- preserve audit status separately.

---

## 7. Findings section

The final Findings section should contain doctor-reviewed imaging findings only.

Recommended principles:
- use appropriate anatomic/radiologic terminology;
- preserve laterality/location/extent only when reviewed/supplied;
- preserve relevant negative findings only when explicitly reviewed;
- preserve limitations when relevant;
- preserve comparison statements only when supported by reviewed temporal evidence.

Do not copy all AI classes mechanically.

Do not include AI scores unless the doctor explicitly chooses to include them and host policy allows it.

Default MedVision final report should omit AI confidence scores from the clinical narrative.

---

## 8. Impression section

The Impression is the concise reviewed clinical synthesis.

It may include:
- accepted/modified disease hypotheses;
- important finding-level conclusions;
- uncertainty;
- clinically important differential when doctor-reviewed;
- current temporal change when validated;
- clinically significant unresolved issue when explicitly retained.

It must not:
- resurrect rejected hypotheses;
- convert possible/indeterminate into confirmed;
- create numeric disease probabilities;
- create ranked differential unless the doctor explicitly authored an ordered differential and host policy preserves it as doctor-authored content.

MedVision itself must not generate disease rankings.

---

## 9. Recommendations / follow-up

ACR reporting guidance allows follow-up/additional studies when appropriate, but MedVision's frozen action boundary is stricter.

Therefore:

```text
Hermes-generated recommendation
→ prohibited

Doctor-authored recommendation
→ may be rendered verbatim/faithfully
```

Allowed final-report recommendation content must be:
- explicitly clinician-authored during Doctor Review; or
- explicitly imported from an external clinician-approved source under host policy.

Do not transform disease uncertainty into an autonomous recommendation.

---

## 10. Comparison section

Only include comparison statements based on reviewed temporal reasoning.

Examples:

Allowed:
```text
Compared with CT 2026-06-01, the same RUL nodule is unchanged.
```

when same-lesion/comparability are reviewed.

Not allowed:
```text
Stable nodule.
```

when prior data are missing or noncomparable.

If comparison is limited:
- state the limitation if doctor-reviewed;
- do not overstate stability/progression.

---

## 11. Clinical indication

Clinical indication may be included from verified source data.

Do not synthesize symptoms/history that were not supplied.

Do not turn a hypothesis into the indication.

---

## 12. Technique / limitations

Include technique and limitations only from:
- verified study metadata;
- radiologist/doctor-reviewed data;
- source systems.

Do not infer:
- AP vs PA;
- portable technique;
- inspiratory quality;
- rotation;
- image quality;

unless supplied or explicitly reviewed.

---

## 13. Patient/study identifiers

The report renderer may map verified host-system metadata such as:
- patient identifier;
- study identifier;
- exam type;
- exam date/time;
- facility;
- ordering/referring clinician.

Hermes must not fabricate missing identifiers.

This module does not define privacy/security compliance.

---

## 14. Structured report sections

Recommended MedVision rendering contract:

```yaml
final_report_candidate:
  report_status: candidate
  source_review_id: null
  source_review_version: null

  patient_study:
    patient_id: null
    study_id: null
    exam: null
    exam_datetime: null

  clinical_information:
    indication: null

  technique:
    text: null

  comparison:
    text: null

  findings:
    text: null
    structured_items: []

  impression:
    text: null
    structured_items: []

  recommendations:
    text: null
    source: doctor_authored|external_clinician_approved|null

  limitations: []

  unresolved_items: []

  provenance:
    ai_snapshot_id: null
    hermes_snapshot_id: null
    draft_report_snapshot_id: null
    doctor_review_id: null
    doctor_review_version: null

  finalization:
    finalized: false
    finalized_by: null
    finalized_at: null
```

Candidate rendering is not yet a finalized medical record.

---

## 15. Version binding

A report candidate must bind to a specific completed doctor-review version.

If current review version changes after rendering:

`FINAL_REPORT_VERSION_MISMATCH`

The old candidate must not be silently reused.

Generate a new candidate from the new reviewed state.

---

## 16. Source snapshot binding

The candidate must reference the source snapshots reviewed by the doctor.

If snapshot IDs are missing/inconsistent:

`FINAL_REPORT_SOURCE_MISMATCH`

or explicit audit incompleteness.

Do not silently bind to newer AI/Hermes outputs that the doctor did not review.

---

## 17. Finalization boundary

`FINAL_REPORT_CANDIDATE_READY` means the content is renderable.

`FINAL_REPORT_RENDERED_FROM_REVIEW` means rendering succeeded from a valid reviewed state.

Neither means the report is finalized.

Only authenticated clinician action may create:

`FINAL_REPORT_FINALIZED_BY_DOCTOR`

and set:
- finalized_by;
- finalized_at.

Hermes must not perform this transition.

---

## 18. Final report after doctor finalization

Once finalized:
- the rendered clinical content is immutable in place;
- corrections/addenda/amendments require a new version/workflow;
- old report remains historical provenance.

If new clinically relevant evidence appears afterward:

`FINAL_REPORT_AMENDMENT_REQUIRED`

according to host-system workflow.

Do not silently rewrite the finalized report.

---

## 19. Superseded reports

If a corrected/amended report becomes current:
- prior final report remains stored;
- mark it as superseded if host policy uses that concept;
- link versions.

Use:

`FINAL_REPORT_SUPERSEDED`

only when an actual replacement/amendment exists.

Do not erase prior final text.

---

## 20. Conflict and uncertainty rendering

Final reports may contain uncertainty.

Correct examples:
- "Indeterminate..."
- "Cannot be established from the available data..."
- "Findings may reflect more than one process..."

Do not force a definitive diagnosis merely because a final report is being generated.

Final != certain.

---

## 21. Cross-disease arbitration handoff

Cross-Disease Arbitration supplies:
- competing hypotheses;
- coexistence;
- shared/distinct evidence;
- unresolved attribution;
- review priority.

Only doctor-reviewed arbitration content may enter the final report.

Do not render:
- hidden scores;
- winner;
- top diagnosis;
- pseudo-probabilities.

---

## 22. Temporal reasoning handoff

Only reviewed temporal states may be rendered:
- new;
- stable;
- improved;
- worsened;
- persistent;
- recurrent;
- resolved;
- indeterminate.

Do not independently recalculate temporal state during final report rendering.

---

## 23. Disease-module handoff

Do not change disease semantics during rendering.

Examples:
- `PNEUMONIA_HYPOTHESIS_SUPPORTED` remains bounded if accepted;
- `MICROBIOLOGICALLY_CONFIRMED_TB` only exists if the TB module/source evidence established it;
- `PATHOLOGY_CONFIRMED_MESOTHELIOMA` remains pathology-derived;
- `DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS` remains source-specific.

Report generation is formatting/synthesis, not a new diagnostic inference step.

---

## 24. No Finding handoff

`No Finding` must retain its 14-class taxonomy meaning.

Do not render:
- "Normal chest"
- "No disease"
- "Healthy"

unless a doctor explicitly authors such a conclusion and it is otherwise supported.

If doctor-reviewed final findings include abnormalities from CT/human review despite prior CXR No Finding:
- report current reviewed abnormalities;
- preserve CXR No Finding only in audit/history as appropriate.

---

## 25. Critical / nonroutine communication

A final report does not automatically prove that a critical result was communicated.

If the host system provides a documented nonroutine communication event, it may be referenced.

Do not fabricate:
- recipient;
- date/time;
- communication method;
- acknowledgement.

Final-report rendering is not a substitute for closed-loop communication.

---

## 26. Language fidelity

Renderer should:
- preserve doctor-authored meaning;
- use concise radiology terminology;
- avoid introducing stronger certainty;
- avoid changing laterality/site;
- avoid silently expanding abbreviations into a different meaning.

If standard terminology normalization is used:
- retain semantic equivalence;
- preserve original reviewed value in audit.

---

## 27. Empty/missing sections

Do not fill missing sections with invented normal statements.

Examples:
- no comparison available → do not invent "No prior";
- no technique metadata → leave null/omit according to template;
- no recommendation → omit/none, not "no follow-up needed" unless doctor authored that conclusion.

---

## 28. Candidate-generation failure states

Use:

```text
FINAL_REPORT_NOT_GENERATABLE
FINAL_REPORT_BLOCKED_BY_REVIEW
FINAL_REPORT_SOURCE_MISMATCH
FINAL_REPORT_VERSION_MISMATCH
```

Every failure should include explicit blocking reasons.

Do not silently fall back to raw AI/Hermes draft.

---

## 29. Recommended rendering pipeline

```text
completed doctor review
→ validate readiness
→ validate review version
→ validate snapshot bindings
→ collect doctor-reviewed findings
→ collect doctor-reviewed hypotheses
→ collect doctor-authored report text
→ render structured sections
→ preserve uncertainty/conflicts
→ create FINAL_REPORT_CANDIDATE_READY
→ external doctor finalization
→ FINAL_REPORT_FINALIZED_BY_DOCTOR
```

---

## 30. Hard constraints

Hermes MUST NOT:

1. Generate final-report clinical content directly from raw `AI_RESULT`.
2. Generate final-report clinical content directly from unreviewed Hermes assessment.
3. Bypass Structured Doctor Review.
4. Reintroduce doctor-rejected findings.
5. Reintroduce doctor-rejected hypotheses.
6. Treat deferred/unreviewed items as accepted.
7. Upgrade uncertainty/confirmation during rendering.
8. Invent recommendations or follow-up actions.
9. Invent patient/study identifiers.
10. Invent technique/comparison/limitations.
11. Invent reviewer identity or finalization timestamp.
12. Recalculate disease diagnosis in the rendering step.
13. Recalculate temporal change in the rendering step.
14. Generate disease ranking/probability.
15. Treat `No Finding` as no disease.
16. Fabricate critical-result communication.
17. Reuse a stale candidate after review version changes.
18. Bind to AI/Hermes snapshots the doctor did not review.
19. Mutate a finalized report in place.
20. Delete/suppress historical report versions.
21. Auto-finalize a candidate.
22. Omit doctor finalization authority.
