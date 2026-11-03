# CROSS_DISEASE_ARBITRATION_POLICY.md

## Integration target

Integrate under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/cross_disease_arbitration/
├── CROSS_DISEASE_ARBITRATION_EVIDENCE.md
├── CROSS_DISEASE_ARBITRATION_POLICY.md
└── references.md
```

Do not create a new top-level arbitration skill.

## Progressive-loading trigger

Load this module when at least one of the following is present:

1. Two or more disease modules emit nontrivial hypotheses for the same case.
2. One evidence item plausibly supports multiple disease hypotheses.
3. Disease modules disagree about attribution of the same finding/process.
4. Multiple diseases may coexist.
5. A high-priority safety hypothesis competes with a more strongly supported non-urgent hypothesis.
6. Temporal reasoning changes the support state of one or more disease hypotheses.
7. Doctor review requires a structured differential rather than a single disease summary.

Do not activate merely because one disease module is loaded and no competing hypothesis exists.

## Reasoning procedure

### Step 1 — Build one canonical evidence ledger

Create unique evidence IDs.

Normalize duplicate references to the same underlying evidence object.

Preserve:
- source;
- timestamp;
- modality/test;
- provenance;
- uncertainty.

Do not clone evidence simply because multiple modules cite it.

### Step 2 — Import bounded disease states

Consume disease-module outputs as-is.

Do not weaken or strengthen disease-specific confirmation rules.

Normalize only into:

```text
HYPOTHESIS_SUPPORTED
HYPOTHESIS_POSSIBLE
HYPOTHESIS_INDETERMINATE
HYPOTHESIS_CONFLICTED
HYPOTHESIS_NOT_ESTABLISHED
```

while preserving each module's original state.

### Step 3 — Mark shared evidence

If one evidence ID supports >1 hypothesis:

`SHARED_EVIDENCE_PRESENT`

Record all supported hypotheses.

Do not convert shared evidence into multiple independent confirmations.

### Step 4 — Mark distinct evidence

For each hypothesis, identify supporting evidence not shared with competitors.

Use:

`DISTINCT_EVIDENCE_PRESENT`

when present.

Distinct evidence may explain why one hypothesis is better supported without creating a rank or probability.

### Step 5 — De-duplicate overlapping evidence

When multiple labels plausibly represent the same process:

`DUPLICATE_EVIDENCE_DEDUPLICATED`

Preserve all original labels/provenance.

### Step 6 — Identify competition

Use:

`COMPETING_HYPOTHESES_PRESENT`

when multiple hypotheses explain the same problem/evidence domain.

Default:

`MUTUAL_EXCLUSIVITY_NOT_ESTABLISHED`

unless explicit evidence supports exclusivity.

### Step 7 — Assess coexistence

Use:

`COEXISTING_PROCESSES_POSSIBLE`

when more than one disease may be present.

Use:

`COEXISTING_PROCESSES_SUPPORTED`

only when independent evidence streams support multiple diseases.

Do not force one hypothesis to absorb all abnormalities.

### Step 8 — Handle unresolved attribution

If an evidence item cannot be assigned to one disease with adequate support:

`EVIDENCE_ATTRIBUTION_UNRESOLVED`

Keep the evidence shared/unassigned rather than forcing attribution.

### Step 9 — Handle contradiction

For each hypothesis maintain:
- supporting evidence;
- contradicting evidence;
- missing evidence;
- conflicts.

Missing is never contradicting.

Explicit negative evidence follows the owning disease module's semantics.

### Step 10 — Separate support, completeness, and urgency

For every hypothesis output three independent dimensions:

```text
support_state
evidence_completeness
review_priority
```

Never collapse them into one score.

### Step 11 — Apply temporal updates

Use temporal reasoning to update current support states when valid.

Preserve historical states and evidence.

No "newer always wins" shortcut.

### Step 12 — Aggregate review priority

Global review priority is the highest justified review/safety priority.

List exact priority drivers.

Do not interpret review priority as disease likelihood.

### Step 13 — Synthesize without ranking

Produce:
- current supported hypotheses;
- possible/indeterminate hypotheses;
- conflicted hypotheses;
- coexistence relationships;
- shared vs distinct evidence;
- unresolved attribution;
- missing information;
- safety/review priority.

Do NOT output:
- winner;
- top diagnosis;
- ranked differential;
- percentages;
- evidence scores.

### Step 14 — Doctor review

Mark doctor review required.

Arbitration output is not FINAL_REPORT.

No autonomous treatment/testing/procedure/disposition action.
