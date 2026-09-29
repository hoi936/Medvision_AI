# FINAL_REPORT_GENERATION_POLICY.md

## Integration target

Integrate under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/final_report/
├── FINAL_REPORT_GENERATION_EVIDENCE.md
├── FINAL_REPORT_GENERATION_POLICY.md
└── references.md
```

Do not create a new top-level final-report skill.

## Progressive-loading trigger

Load this module only when one of the following is true:

1. Structured Doctor Review is completed and finalization readiness is being evaluated.
2. A final-report candidate is requested from a completed reviewed state.
3. A finalized report needs an amendment/new-version workflow because new evidence arrived.
4. A candidate/report version mismatch or snapshot-binding issue must be evaluated.

Do not activate:
- during raw AI inference;
- during disease reasoning;
- during an incomplete/unreviewed doctor-review workflow.

## Rendering procedure

### Step 1 — Validate review state

Require:
- completed doctor review;
- readiness == ready;
- reviewer identity;
- review completion timestamp;
- required high-priority acknowledgement;
- reviewed report content.

If not:

`FINAL_REPORT_BLOCKED_BY_REVIEW`

with explicit blocking reasons.

### Step 2 — Validate review/source versions

Bind to:
- review ID/version;
- AI snapshot ID;
- Hermes snapshot ID;
- draft snapshot ID.

If review version changed:

`FINAL_REPORT_VERSION_MISMATCH`

If source references do not match the reviewed snapshots:

`FINAL_REPORT_SOURCE_MISMATCH`

Never silently bind to newer upstream data.

### Step 3 — Collect only reviewed clinical content

Include:
- accepted findings;
- doctor modifications;
- doctor-added findings;
- accepted/modified hypothesis content;
- explicitly preserved uncertainty/conflicts;
- doctor-authored report narrative.

Exclude as affirmative content:
- rejected findings;
- rejected hypotheses;
- unreviewed required items;
- raw AI/Hermes statements not reviewed.

### Step 4 — Render report sections

Preferred structured sections:

```text
PATIENT / STUDY
CLINICAL INFORMATION
TECHNIQUE
COMPARISON
FINDINGS
IMPRESSION
RECOMMENDATIONS (only when doctor-authored)
LIMITATIONS / UNRESOLVED ITEMS where appropriate
```

Host system may alter display order while preserving semantics.

### Step 5 — Preserve certainty

Rendering is not a reasoning step.

Do not:
- upgrade "possible" to "likely";
- upgrade concern to confirmed;
- remove doctor-preserved uncertainty;
- create a top-ranked diagnosis.

### Step 6 — Preserve doctor authorship

Doctor-added/modified information may appear naturally in final narrative.

Audit must retain that these details were doctor-authored rather than AI-originated.

### Step 7 — Recommendations

Render recommendation/follow-up text only if:
- explicitly doctor-authored; or
- explicitly clinician-approved external content under host policy.

Hermes must not create action/recommendation text.

### Step 8 — Produce candidate

Successful rendering creates:

`FINAL_REPORT_CANDIDATE_READY`

and/or:

`FINAL_REPORT_RENDERED_FROM_REVIEW`

with:

```text
finalized = false
```

### Step 9 — Finalization

Only authenticated external clinician action can set:

`FINAL_REPORT_FINALIZED_BY_DOCTOR`

and provide:
- finalized_by;
- finalized_at.

Renderer cannot perform that action.

### Step 10 — Post-finalization evidence

If new clinically relevant evidence arrives:
- finalized report remains immutable;
- flag `FINAL_REPORT_AMENDMENT_REQUIRED`;
- create new review/report version according to host policy.

Do not silently update the old final report.

## Final-report content ownership

### AI/Hermes owns
- source provenance;
- structured evidence references;
- draft reasoning;
- rendering mechanics.

### Doctor owns
- accepted/modified/rejected review decisions;
- final findings interpretation;
- impression;
- clinical uncertainty decisions;
- recommendation/action wording;
- finalization.

## Structured template behavior

Templates may improve consistency but must not:
- auto-fill absent normal findings;
- force a diagnosis;
- force a recommendation;
- erase uncertainty;
- infer comparisons.

Empty optional fields should remain null/omitted according to host template rules.

## Report status contract

```text
FINAL_REPORT_NOT_GENERATABLE
FINAL_REPORT_BLOCKED_BY_REVIEW
FINAL_REPORT_SOURCE_MISMATCH
FINAL_REPORT_VERSION_MISMATCH
FINAL_REPORT_CANDIDATE_READY
FINAL_REPORT_RENDERED_FROM_REVIEW
FINAL_REPORT_FINALIZED_BY_DOCTOR
FINAL_REPORT_AMENDMENT_REQUIRED
FINAL_REPORT_SUPERSEDED
```

## Output

Return a structured report candidate plus provenance/finalization metadata.

Do not claim a candidate is a final medical report until doctor finalization is explicitly supplied.
