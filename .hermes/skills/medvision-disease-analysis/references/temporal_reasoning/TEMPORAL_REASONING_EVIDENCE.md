# TEMPORAL_REASONING_EVIDENCE.md

## 0. Scope

Cross-cutting MedVision Disease Analysis v2 reference module for:

**Longitudinal / Temporal Reasoning**

This module answers questions such as:
- Is a finding new, resolved, improved, worsened, stable, persistent, or recurrent?
- Are two observations actually comparable?
- Are they the same lesion/process?
- Does a disease-specific progression criterion have valid longitudinal support?
- Which evidence is older versus newer, and how should conflicts be preserved?

This is not:
- a new top-level Hermes skill;
- a new finding mapping;
- a treatment/action engine;
- a generic numeric-trend calculator.

Target flow remains:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ temporal_reasoning reference module
```

The temporal layer supports disease modules but does not replace them.

---

## 1. Core principle

Temporal claims require actual temporal evidence.

```text
No prior study != new lesion
No prior study != stable lesion
Single study != progression
Single lab != trend
```

A valid temporal interpretation requires enough evidence to establish:
1. ordering in time;
2. entity/process correspondence;
3. comparison eligibility;
4. actual interval change.

If any required component is missing, use a bounded unknown/indeterminate state rather than inventing change.

---

## 2. Temporal states

Allowed MedVision temporal states:

```text
NEW
RESOLVED
IMPROVED
WORSENED
STABLE
PERSISTENT
RECURRENT

INTERVAL_CHANGE_INDETERMINATE
COMPARISON_NOT_POSSIBLE
PRIOR_DATA_MISSING
TEMPORAL_CONFLICT
```

These states describe temporal interpretation, not disease diagnosis.

---

## 3. Correspondence states

Before judging interval change, decide whether the current and prior observations refer to the same entity/process:

```text
CORRESPONDENCE_CONFIRMED
CORRESPONDENCE_PROBABLE
CORRESPONDENCE_UNCERTAIN
CORRESPONDENCE_NOT_SAME
CORRESPONDENCE_UNKNOWN
```

Possible bases:
- explicit radiologist statement;
- lesion ID;
- matching lobe/segment and morphology;
- image registration or trusted structured tracking;
- explicit clinician linkage;
- pathology/specimen linkage.

Do not infer same-lesion correspondence from:
- both being called `Nodule/Mass`;
- overlapping but non-identical boxes;
- same side of chest alone;
- similar AI scores;
- similar generic finding labels.

---

## 4. Comparability states

After correspondence, judge whether measurements/observations are comparable:

```text
COMPARABLE
LIMITED_COMPARABILITY
NOT_COMPARABLE
COMPARABILITY_UNKNOWN
```

Factors that can limit comparability include:
- different modality;
- different acquisition technique;
- different projection;
- different slice thickness;
- different respiratory phase;
- different measurement software;
- different laboratory method;
- missing dates;
- incomplete anatomy coverage;
- interval intervention/treatment;
- observer/measurement uncertainty.

Different modality does not always mean impossible comparison, but it must not be silently treated as equivalent.

---

## 5. Observation time

Each observation should preserve:
- acquisition/sample timestamp if available;
- report/result timestamp if distinct;
- source;
- modality or test type;
- timezone if supplied;
- whether timestamp is exact or approximate.

Prefer acquisition/sample time for biologic/imaging sequence when available.

Do not silently use file-modification time or ingestion time as clinical event time.

---

## 6. Ordering rules

If current/prior order is known:

```text
earlier → later
```

If dates are equal or unresolved:
- do not invent order;
- use `INTERVAL_CHANGE_INDETERMINATE` or `COMPARISON_NOT_POSSIBLE`.

If one timestamp is approximate:
- preserve the uncertainty.

---

## 7. NEW

Use `NEW` only when:
- a valid prior comparator exists;
- the same relevant entity/region/process was adequately assessed previously;
- the feature was absent or explicitly not present previously;
- current evidence demonstrates it now.

Do not use `NEW` when:
- no prior study exists;
- prior anatomy was not covered;
- prior technique was insufficient to assess the feature;
- lesion correspondence is uncertain.

Example:

```text
current CT: 8 mm RUL nodule
prior CT: same region adequately imaged, no nodule
→ NEW
```

But:

```text
current CT nodule
no prior imaging
→ PRIOR_DATA_MISSING
not NEW
```

---

## 8. RESOLVED

Use `RESOLVED` only when:
- prior abnormality was established;
- same region/process is adequately evaluated now;
- current evidence supports absence/resolution.

Do not use `RESOLVED` merely because:
- an AI class becomes NEGATIVE;
- the current report omits the finding;
- the current study is technically less sensitive;
- a different modality fails to show it.

A missing current mention is not equivalent to resolution.

---

## 9. IMPROVED / WORSENED

Use these only when change direction is supported by:
- comparable qualitative interpretation;
- comparable quantitative measurement;
- explicit trusted report comparison;
- valid disease-specific serial criteria.

Do not use image-model score changes as evidence of biologic improvement/worsening.

```text
AI score 0.72 → 0.41
!= lesion improved
```

unless actual radiographic evidence supports improvement.

---

## 10. STABLE

Use `STABLE` only when:
- the same entity/process is compared;
- comparison is adequate;
- no meaningful interval change is supported within known measurement limitations.

Do not infer stability from:
- missing prior data;
- vague phrase "history of";
- different lesion;
- current value alone;
- one study.

If comparison is technically limited:
- prefer `LIMITED_COMPARABILITY` plus cautious wording rather than overconfident `STABLE`.

---

## 11. PERSISTENT

Use `PERSISTENT` when:
- the same abnormality/process remains present across valid timepoints;
- resolution was not documented between them.

Persistence does not automatically mean stability.

A lesion may be:
- persistent and stable;
- persistent and worsening;
- persistent and improving.

Keep these dimensions separable.

---

## 12. RECURRENT

Use `RECURRENT` only when:
1. an abnormality/process was previously present;
2. a valid interval assessment documented resolution/absence;
3. a later valid assessment shows it again.

Do not call recurrence if:
- there was never documented resolution;
- prior data are missing;
- the later finding may be a different lesion/process.

Without documented resolution, use `PERSISTENT` or `INTERVAL_CHANGE_INDETERMINATE` as supported.

---

## 13. TEMPORAL_CONFLICT

Use `TEMPORAL_CONFLICT` when trusted longitudinal sources disagree in a way that cannot be reconciled automatically.

Examples:
- radiologist says lesion enlarged; structured measurement suggests unchanged but technique differs;
- current AI says resolved; current human report says persistent;
- one report dates a prior study incorrectly;
- two external reports disagree on whether the same lesion was present.

Preserve all source/time provenance.

Do not silently choose one source unless an existing modality/source hierarchy specifically resolves that disease question.

---

## 14. PRIOR_DATA_MISSING

Use when the temporal question requires a prior comparator but no adequate prior evidence exists.

Examples:
- current nodule with no prior imaging;
- current pleural effusion with no prior study;
- current FVC with no prior PFT;
- current fibrosis severity with no earlier CT.

Missing prior evidence must not become:
- new;
- stable;
- progressive;
- recurrent.

---

## 15. COMPARISON_NOT_POSSIBLE

Use when prior data exist but cannot validly answer the comparison question.

Examples:
- current CT nodule vs prior chest radiograph where the lesion was below reliable resolution;
- current left lower-lobe lesion vs prior right upper-lobe lesion;
- current FVC vs prior noncomparable spirometry result with invalid test quality;
- current study covers anatomy absent from prior study.

This is different from `PRIOR_DATA_MISSING`.

---

## 16. Multi-modality reasoning

Cross-modality comparison must preserve modality-specific strengths and limitations.

Examples:

### CXR → CT
A lesion detected on CT but absent on prior CXR:

```text
not enough to call NEW
```

unless prior CXR was explicitly capable of evaluating that lesion and trusted interpretation supports absence.

### CT → CXR
A CT-confirmed lesion not seen on later CXR:

```text
not enough to call RESOLVED
```

because CXR may be less sensitive.

### CTA / definitive imaging
For AAS anatomy, later CTA may supersede CXR for disease confirmation while preserving the earlier CXR finding as historical evidence.

Newer does not mean all prior evidence is erased.

---

## 17. Measurement provenance

Every quantitative temporal comparison should retain:
- measurement value;
- unit;
- method;
- modality/test;
- software/algorithm if relevant;
- source;
- timestamp.

Do not compare values with mismatched units without explicit validated conversion.

Do not compare:
- AI bbox dimensions to CT nodule diameter;
- CXR apparent cardiac size to echo EF;
- FVC liters to FVC % predicted as if identical;
- uncorrected DLCO to Hb-corrected DLCO without noting the difference.

---

## 18. Pulmonary nodule / mass growth

Existing Pulmonary Malignancy rules remain authoritative.

Temporal layer requirements:
- same lesion correspondence;
- comparable imaging;
- actual interval;
- valid measurement provenance.

Fleischner guidance emphasizes review of prior imaging and recognizes that differences in scanning technique can make nodule-growth comparison less accurate [S2].

Therefore:

```text
larger current AI bbox
!= true lesion growth
```

and:

```text
different CT technique
→ possibly LIMITED_COMPARABILITY
```

Growth can support malignancy concern but does not confirm cancer.

---

## 19. ILD / PPF

Existing ILD/PPF rules remain authoritative.

Temporal layer must ensure:
- valid prior/current dates;
- one-year window when PPF rules require it;
- comparable FVC/DLCO;
- comparable HRCT for radiologic progression;
- alternative explanations preserved.

Single severe fibrosis study:

```text
severity known
progression unknown
```

No temporal layer shortcut may bypass the 2-of-3 PPF rule.

---

## 20. Pneumonia

Possible temporal states:
- new acute opacity when a valid prior comparator shows absence;
- improving/resolving opacity when comparable imaging documents decrease;
- persistent opacity when still present;
- unresolved temporal status when comparator is missing/inadequate.

Do not equate:
- AI class disappearing with radiographic resolution;
- persistent opacity with persistent infection automatically.

Disease-level interpretation remains owned by the Pneumonia module.

---

## 21. Heart failure / congestion

Congestion can improve/worsen over time, but temporal claims require actual comparable evidence.

Do not infer response to diuretics or other treatment merely because:
- effusion is smaller;
- opacity score decreases;
- symptoms improve.

Treatment exposure and observed change may coexist without proving causality.

Use wording like:
- "improved after interval treatment" only if sequence is known;
- avoid "improved because of treatment" unless source explicitly supports causality.

---

## 22. Pleural disease

Possible longitudinal states:
- persistent effusion;
- resolved effusion;
- recurrent effusion;
- progressive pleural thickening/nodularity.

`RECURRENT` requires documented resolution/absence between episodes.

Repeated effusions without documented resolution are persistent/repeated, not necessarily recurrent.

---

## 23. TB / chronic mycobacterial disease

Prior treated TB plus unchanged fibrotic scar:

```text
persistent residual change
!= active recurrence
```

New symptoms alone do not establish radiographic recurrence.

A new M. tuberculosis-specific positive result can establish current microbiologic evidence even if old imaging is unchanged.

Preserve historical disease, residual imaging, and current activity separately.

---

## 24. Aortic disease

Aortic enlargement may be chronic.

Do not infer acute progression from:
- one enlarged CXR;
- different projection;
- AP vs PA size difference.

Definitive interval aortic growth requires comparable anatomic measurements from appropriate imaging.

AAS remains a clinical/advanced-imaging disease module, not a temporal-size diagnosis.

---

## 25. Labs and physiology

A trend requires at least two temporally ordered comparable values.

For three or more observations, preserve the full sequence rather than reducing to only first/last when clinically relevant.

Do not infer trend from:
- one abnormal value;
- one normal and one value with incompatible method/unit;
- unknown sample times.

Disease-specific thresholds remain in their owning modules.

---

## 26. Treatment/intervention as temporal context

Preserve treatment/intervention events between observations when supplied:
- antibiotics;
- diuresis;
- drainage;
- surgery;
- biopsy;
- anti-TB therapy;
- cancer therapy;
- oxygen/ventilation;
- other interventions.

But temporal association is not automatically causal.

```text
intervention occurred
+ later improvement
!= proven treatment response
```

unless explicitly supported by a trusted clinician/source.

---

## 27. Source precedence and recency

Do not use a simple "newer always wins" rule.

Recency matters for current state, but source quality/modality and the question being asked also matter.

Examples:
- newer CXR does not automatically override earlier CT anatomy;
- newer preliminary report may not override finalized pathology;
- later culture may resolve an earlier negative NAAT;
- later definitive CTA may resolve AAS uncertainty.

Preserve:
- source type;
- status (preliminary/final if supplied);
- date/time;
- reason one source is more informative.

---

## 28. Missingness

Missing stays missing.

Do not convert:
- missing prior test to normal;
- missing symptom history to unchanged;
- missing measurement to stable;
- absent report mention to absent finding.

Unknown temporal states should be explicit.

---

## 29. Suggested temporal object

```yaml
temporal_comparison:
  entity_id: null
  entity_type: finding|lesion|disease|lab|physiology

  current:
    timestamp: null
    timestamp_precision: exact|date_only|approximate|unknown
    modality_or_test: null
    source: null
    value: null

  prior:
    timestamp: null
    timestamp_precision: exact|date_only|approximate|unknown
    modality_or_test: null
    source: null
    value: null

  correspondence:
    status: confirmed|probable|uncertain|not_same|unknown
    basis: []

  comparability:
    status: comparable|limited|not_comparable|unknown
    limitations: []

  interval:
    duration: null
    unit: null

  change:
    status: new|resolved|improved|worsened|stable|persistent|recurrent|indeterminate
    evidence: []

  interventions_between: []
  confounders: []
  missing_evidence: []
  conflicts: []

  interpretation:
    summary: ""
    causal_attribution: not_established
    requires_doctor_review: true
```

---

## 30. Hard constraints

Hermes MUST NOT:

1. Call a finding new when no valid prior comparator exists.
2. Call a finding stable when prior evidence is missing.
3. Call a lesion growing without same-lesion correspondence.
4. Use AI bbox change as lesion growth by itself.
5. Use AI score change as improvement/worsening.
6. Call a finding resolved merely because the current AI class is negative or omitted.
7. Call recurrence without documented interval resolution/absence.
8. Treat different modalities as automatically equivalent.
9. Treat different technical protocols as fully comparable without assessing limitations.
10. Compare mismatched units/methods as if identical.
11. Infer disease progression from one study.
12. Infer lab/physiology trend from one value.
13. Bypass PPF temporal rules.
14. Convert chronic TB scar into active recurrence.
15. Convert persistent pneumonia opacity into persistent infection automatically.
16. Infer treatment causality from temporal association alone.
17. Let newer low-information evidence automatically erase older higher-information evidence.
18. Drop old provenance when a later source supersedes disease interpretation.
19. Treat missing report mention as negative evidence.
20. Manufacture timestamps or study order.
21. Issue autonomous treatment/testing/procedure/disposition actions.
22. Omit doctor review.
