# TEMPORAL_REASONING_POLICY.md

## Integration target

Integrate under the existing:

`medvision-disease-analysis`

Suggested path:

```text
.hermes/skills/medvision-disease-analysis/references/temporal_reasoning/
├── TEMPORAL_REASONING_EVIDENCE.md
├── TEMPORAL_REASONING_POLICY.md
└── references.md
```

Do not create a new top-level temporal skill.

## Progressive-loading trigger

Load this module when any of the following is present:

1. More than one clinically relevant timepoint for the same patient.
2. Explicit language such as:
   - prior/current;
   - interval change;
   - new;
   - stable;
   - persistent;
   - improved;
   - worsened;
   - resolved;
   - recurrent;
   - growth/progression.
3. Serial imaging, labs, physiology, microbiology, pathology, or disease assessments.
4. A disease module requires a longitudinal determination:
   - pulmonary-nodule growth/stability;
   - ILD/PPF progression;
   - recurrent/persistent pleural effusion;
   - residual-vs-active TB;
   - evolving congestion;
   - pneumonia resolution/persistence;
   - chronic-vs-acute aortic change.
5. Current and prior evidence conflict.

Do not activate merely because a single study contains the word "chronic" if no temporal comparison is being requested or implied.

## Reasoning procedure

### Step 1 — Build an event timeline

For each relevant observation preserve:
- event/acquisition/sample date;
- source/report date if distinct;
- modality/test;
- source/provenance;
- value/finding;
- explicit uncertainty.

Never use ingestion/file-modification time as clinical time.

### Step 2 — Identify the temporal entity

Choose what is actually being compared:

```text
finding
lesion
disease
lab
physiology
microbiology
pathology
```

Do not compare two observations merely because they share a generic label.

### Step 3 — Resolve correspondence

Assign:

```text
CORRESPONDENCE_CONFIRMED
CORRESPONDENCE_PROBABLE
CORRESPONDENCE_UNCERTAIN
CORRESPONDENCE_NOT_SAME
CORRESPONDENCE_UNKNOWN
```

If not same or unknown, do not emit growth/stability/resolution as if the same entity were tracked.

### Step 4 — Assess comparability

Assign:

```text
COMPARABLE
LIMITED_COMPARABILITY
NOT_COMPARABLE
COMPARABILITY_UNKNOWN
```

Capture modality, protocol, units, method, anatomy coverage, software and other relevant limitations.

### Step 5 — Determine valid interval state

Only after correspondence + comparability are adequate, consider:

```text
NEW
RESOLVED
IMPROVED
WORSENED
STABLE
PERSISTENT
RECURRENT
```

Otherwise prefer:
- `PRIOR_DATA_MISSING`
- `COMPARISON_NOT_POSSIBLE`
- `INTERVAL_CHANGE_INDETERMINATE`
- `TEMPORAL_CONFLICT`

### Step 6 — Apply disease-specific temporal rule

The temporal module provides evidence structure.

The owning disease module decides disease semantics.

Examples:
- nodule module decides whether growth raises malignancy concern;
- ILD module decides whether PPF criteria are met;
- TB module decides whether current evidence supports activity;
- pleural module decides whether effusion is persistent/recurrent;
- pneumonia module decides whether temporal change affects pneumonia concern.

Do not duplicate disease-specific diagnostic thresholds here.

### Step 7 — Handle competing explanations

Before attributing worsening to one disease, preserve alternative causes.

Examples:
- edema can mimic ILD radiologic worsening;
- pneumonia can create new opacity;
- technique can change apparent nodule size;
- treatment/intervention can occur between observations.

Temporal sequence alone does not prove causality.

### Step 8 — Preserve supersession without erasure

A later, more definitive source may change current interpretation.

Example:
- CTA confirms no AAS after suspicious CXR.

Represent:
- earlier CXR evidence;
- later CTA evidence;
- resulting disease interpretation;
- source/timing.

Do not delete historical evidence.

### Step 9 — Safety

Temporal worsening may influence existing safety priority only when actual severe current-state evidence supports it.

No autonomous treatment or disposition action.

### Step 10 — Output

Return:
- timeline;
- compared entity;
- correspondence;
- comparability;
- interval;
- change state;
- interventions/confounders;
- disease-specific handoff;
- conflicts;
- missing evidence;
- doctor review.
