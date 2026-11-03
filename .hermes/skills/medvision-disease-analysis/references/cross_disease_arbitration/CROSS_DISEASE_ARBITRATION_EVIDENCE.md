# CROSS_DISEASE_ARBITRATION_EVIDENCE.md

## 0. Scope

Cross-cutting MedVision Disease Analysis v2 reference module for:

**Cross-Disease Differential Arbitration**

This layer combines bounded outputs from already-frozen disease modules without turning Hermes into:
- a winner-selection engine;
- a probability-ranking engine;
- an autonomous diagnostic authority;
- a treatment/action engine.

Target flow:

```text
medvision-evidence-fusion
→ finding-specific skills
→ medvision-safety-check
→ medvision-disease-analysis
   ↳ disease modules
   ↳ temporal reasoning
   ↳ cross-disease arbitration
```

The arbitration layer does not replace disease modules. It organizes their evidence relationships.

---

## 1. Core principles

```text
Most evidence != true diagnosis
Most modules supporting != highest probability
AI score != disease rank
Shared evidence != independent confirmations
Missing evidence != negative evidence
Urgency != certainty
Certainty != urgency
```

One supported disease hypothesis does not automatically exclude others.

Independent processes may coexist.

---

## 2. Hypothesis support states

Normalize disease-module outputs into:

```text
HYPOTHESIS_SUPPORTED
HYPOTHESIS_POSSIBLE
HYPOTHESIS_INDETERMINATE
HYPOTHESIS_CONFLICTED
HYPOTHESIS_NOT_ESTABLISHED
```

These are descriptive states, not numeric probabilities.

Do not map them to hidden percentages.

Do not rank hypotheses numerically.

---

## 3. Evidence ledger

Every relevant evidence item should have a stable evidence object:

```yaml
evidence:
  id: E1
  type: symptom|sign|lab|imaging|pathology|microbiology|history|temporal
  value: null
  source: null
  modality_or_test: null
  timestamp: null
  provenance: null
  certainty: explicit|derived|unknown
```

Each disease hypothesis refers to evidence IDs.

Do not duplicate the same underlying evidence merely because multiple disease modules use it.

Example:

```text
E1 = dyspnea
E2 = bilateral opacity
```

Both pneumonia and HF may reference E1/E2.

This does NOT create four independent evidence items.

---

## 4. Shared evidence

Use:

`SHARED_EVIDENCE_PRESENT`

when the same evidence object supports more than one hypothesis.

Examples:
- dyspnea supports pneumonia and HF;
- weight loss supports TB and malignancy;
- pleural effusion supports HF, infection, and malignancy concern;
- cavitation may support TB and malignancy concern.

Shared evidence must remain visible as shared.

Do not treat it as independent confirmation for each disease when summarizing overall differential structure.

---

## 5. Distinct evidence

Use:

`DISTINCT_EVIDENCE_PRESENT`

when a hypothesis has supporting evidence that is not merely shared with competing hypotheses.

Examples:

```text
Pneumonia:
  shared: dyspnea, opacity
  distinct: fever, acute cough, inflammatory syndrome

HF:
  shared: dyspnea, opacity
  distinct: elevated JVP, echo dysfunction, natriuretic-peptide context
```

Distinct evidence can strengthen a bounded support state, but still does not create a numeric ranking.

---

## 6. Evidence attribution unresolved

Use:

`EVIDENCE_ATTRIBUTION_UNRESOLVED`

when one abnormality could plausibly arise from multiple processes and the available data do not establish which one accounts for it.

Example:

```text
bilateral opacity
→ pneumonia?
→ cardiogenic edema?
→ ILD?
```

Do not force one etiology.

---

## 7. Duplicate evidence de-duplication

Use:

`DUPLICATE_EVIDENCE_DEDUPLICATED`

when multiple labels or module outputs plausibly describe the same underlying evidence.

Examples:
- `Consolidation` + `Lung Opacity` + `Infiltration` on the same region/process;
- `ILD` + `Pulmonary fibrosis` representing one fibrotic interstitial process;
- repeated mentions of the same symptom copied through multiple module payloads.

De-duplication does not delete original evidence provenance.

---

## 8. Competing hypotheses

Use:

`COMPETING_HYPOTHESES_PRESENT`

when two or more hypotheses plausibly explain at least part of the same clinical problem.

Examples:
- pneumonia vs HF for acute dyspnea/opacities;
- TB vs malignancy for chronic cavitary lesion;
- ILD vs HF for interstitial opacity and dyspnea;
- pleural malignancy vs pleural TB for unilateral effusion.

Competing does not mean mutually exclusive.

---

## 9. Coexisting processes

Use:

`COEXISTING_PROCESSES_POSSIBLE`

when evidence supports the possibility that more than one disease process may be present.

Use:

`COEXISTING_PROCESSES_SUPPORTED`

only when independent evidence supports multiple processes simultaneously.

Example:

```text
microbiologically confirmed TB
+
separate pathology-confirmed malignancy
```

may support coexistence.

Do not force a single unifying diagnosis.

---

## 10. Mutual exclusivity

Default:

`MUTUAL_EXCLUSIVITY_NOT_ESTABLISHED`

unless the frozen disease rules or explicit source evidence makes two states genuinely incompatible.

Do not assume:
- pneumonia excludes HF;
- TB excludes malignancy;
- malignancy excludes infection;
- ILD excludes acute edema;
- pleural malignancy excludes HF-related effusion.

---

## 11. Support state is separate from evidence completeness

Each hypothesis should carry both:

```yaml
support_state: supported|possible|indeterminate|conflicted|not_established
evidence_completeness: minimal|partial|substantial|unknown
```

A hypothesis can be:
- high concern but incomplete;
- well-supported but still missing etiologic detail;
- conflicted despite substantial evidence.

Completeness is not probability.

---

## 12. Support state is separate from safety/review priority

Each hypothesis should also carry:

```yaml
review_priority: routine|elevated|high
```

This means urgency of clinician review, not diagnostic confidence.

Examples:
- AAS may be `HYPOTHESIS_INDETERMINATE` with `REVIEW_PRIORITY_HIGH`.
- Pathology-confirmed indolent malignancy may be diagnostically certain but not an immediate emergency.
- Pneumothorax with severe compromise may be high priority despite limited etiologic detail.

Never equate high priority with high probability.

---

## 13. No universal evidence hierarchy

There is no single global hierarchy such as:

```text
pathology > CT > CXR > labs > symptoms
```

Instead, evidence strength is question-specific.

Examples:
- pathology may establish malignancy histology;
- CT/CTA may be definitive for aortic anatomy;
- microbiology may confirm TB;
- echo may be stronger than CXR for cardiac structure/function;
- CXR may be the only direct evidence for a specific radiographic finding.

Use disease-module rules for source hierarchy.

---

## 14. Specific evidence refines generic evidence

A more specific source may refine a generic one without erasing provenance.

Example:

```text
AI: Other lesion
CT: pleural mass
Pathology: metastatic carcinoma
```

Represent:
- AI generic evidence;
- CT anatomic characterization;
- pathology disease confirmation.

Do not rewrite the original AI class as if it predicted metastasis.

---

## 15. Missing evidence

Missing stays missing.

Missing evidence must not be added to:
- contradicting evidence;
- negative evidence;
- exclusion criteria.

Example:

```text
BNP missing
```

does not count against HF.

```text
TB culture not done
```

does not count as negative culture.

---

## 16. Explicit negative evidence

Only explicit, reliable negative evidence may be used as contradicting evidence.

Examples:
- definitive CTA explicitly negative for AAS;
- pathology explicitly benign for the sampled corresponding lesion;
- microbiology explicitly negative in a context where the owning disease module permits bounded exclusion semantics.

Even explicit negative evidence may have scope/false-negative limitations.

Disease-specific modules decide how strongly it contradicts a hypothesis.

---

## 17. No Finding semantics

`No Finding` only describes absence of the 14 target CXR findings under the existing policy.

It is not global negative evidence for:
- pneumonia;
- HF;
- malignancy;
- AAS;
- ILD;
- pleural disease;
- TB.

Arbitration must not use No Finding as a universal disease down-ranker.

---

## 18. Temporal integration

Temporal reasoning may update the current support state.

Examples:
- resolving opacity may reduce pneumonia concern;
- true nodule growth may increase malignancy concern;
- later M. tuberculosis culture may confirm TB;
- definitive CTA may resolve earlier AAS uncertainty.

Historical evidence remains preserved.

Do not delete old evidence when support state changes.

---

## 19. Conflict handling

A hypothesis is `HYPOTHESIS_CONFLICTED` when trusted evidence both supports and contradicts it without a valid resolution.

Examples:
- suspicious imaging but discordant pathology with uncertain lesion correspondence;
- current AI negative but current trusted report positive;
- chronic fibrosis with acute edema obscuring interval ILD assessment.

Use conflict objects:

```yaml
conflict:
  id: C1
  hypothesis: heart_failure
  supporting_evidence: [E1, E2]
  contradicting_evidence: [E7]
  unresolved_reason: ""
```

Do not silently choose a winner.

---

## 20. Disease-specific confirmation remains local

The arbitration layer MUST NOT invent confirmation.

Examples:
- pneumonia module controls pneumonia support semantics;
- HF module controls HF support semantics;
- TB module controls microbiologic confirmation;
- pulmonary malignancy module controls pathology confirmation;
- pleural module controls malignant pleural effusion and mesothelioma confirmation;
- AAS module controls definitive imaging confirmation;
- ILD module controls PPF criteria.

Arbitration consumes those states.

---

## 21. Cross-disease evidence matrix

Recommended representation:

```yaml
evidence_matrix:
  - evidence_id: E1
    value: dyspnea
    supports:
      - pneumonia
      - heart_failure
    contradicts: []
    shared: true

  - evidence_id: E2
    value: fever
    supports:
      - pneumonia
    contradicts: []
    shared: false
```

No numeric weights are required.

---

## 22. Recommended hypothesis object

```yaml
hypothesis:
  id: H1
  name: pneumonia
  module: pneumonia

  support_state: supported
  evidence_completeness: partial
  review_priority: elevated

  supporting_evidence: [E1, E2]
  distinct_supporting_evidence: [E2]
  shared_supporting_evidence: [E1]
  contradicting_evidence: []
  missing_evidence: [E5]
  conflicts: []

  temporal_state: null
  confirmation_state: null

  uncertainty: ""
  requires_doctor_review: true
```

---

## 23. Recommended arbitration output

```yaml
arbitration:
  hypotheses: []
  evidence_ledger: []
  evidence_matrix: []

  relations:
    competing_hypotheses: []
    possible_coexisting_processes: []
    supported_coexisting_processes: []
    shared_evidence_groups: []
    unresolved_attribution: []

  global_conflicts: []
  missing_information: []

  review:
    highest_priority: routine|elevated|high
    priority_drivers: []
    doctor_review_required: true

  synthesis:
    summary: ""
    uncertainty: ""
    no_numeric_ranking: true
```

---

## 24. Pneumonia vs Heart Failure

Common shared evidence:
- dyspnea;
- hypoxemia;
- bilateral opacity;
- pleural effusion.

Potential distinct pneumonia evidence:
- acute infectious syndrome;
- fever;
- inflammatory context;
- microbiology if supplied.

Potential distinct HF evidence:
- JVP;
- orthopnea/PND;
- echo dysfunction/filling pressure;
- NP context;
- explicit congestion morphology.

Do not assign the shared opacity automatically to either cause.

Both processes may coexist.

---

## 25. TB vs Pulmonary Malignancy

Shared evidence can include:
- weight loss;
- cough;
- upper-lobe lesion;
- cavitation;
- chronic symptoms.

Distinct evidence:
- M. tuberculosis-specific microbiology supports TB;
- pathology-confirmed malignancy supports cancer.

If both exist in separate evidence streams:

`COEXISTING_PROCESSES_SUPPORTED`

may be appropriate.

Do not force one process to explain every lesion.

---

## 26. ILD vs Heart Failure

Shared evidence:
- dyspnea;
- interstitial/reticular opacity;
- hypoxemia.

Distinct ILD evidence:
- HRCT fibrosis;
- traction bronchiectasis/honeycombing;
- longitudinal fibrotic progression.

Distinct HF evidence:
- cardiac structural/functional abnormality;
- elevated filling pressure;
- explicit congestion pattern.

Acute edema may coexist with chronic fibrotic ILD.

Do not count edema as PPF progression.

---

## 27. Pneumonia vs ILD

Acute opacity and dyspnea may overlap.

Temporal pattern, HRCT morphology, infection context and pre-existing fibrosis may distinguish evidence streams.

Do not make acute infection evidence erase established chronic ILD.

Do not call every ILD worsening an infection.

---

## 28. Pleural malignancy vs pleural TB

Shared evidence:
- unilateral effusion;
- pleural thickening;
- constitutional symptoms.

Distinct malignancy evidence:
- malignant cytology/pathology;
- explicit metastatic pleural involvement.

Distinct TB evidence:
- M. tuberculosis-specific pleural microbiology;
- compatible pathology plus supporting context.

ADA alone is supportive, not definitive.

Do not force a winner if only shared evidence exists.

---

## 29. Pulmonary malignancy + pleural malignancy

A pulmonary lesion and pleural malignancy may be related or independent.

Do not infer:
- primary lung cancer caused pleural metastasis;
- pleural malignancy arose from the pulmonary lesion;

unless explicit pathology/clinical source establishes origin.

If origin is established, preserve that relationship.

---

## 30. AAS vs other acute chest syndromes

Acute chest pain may coexist with evidence for:
- AAS;
- pneumothorax;
- pneumonia;
- PE/ACS if externally represented.

Safety priority may be high even if diagnosis remains indeterminate.

Do not suppress one urgent hypothesis because another seems plausible.

---

## 31. Coexisting acute and chronic disease

Examples:
- chronic fibrotic ILD + acute pneumonia;
- prior treated TB scar + new pneumonia;
- chronic HF + acute pneumonia;
- malignancy + superimposed infection.

Arbitration should explicitly represent multi-process possibilities rather than forcing a single explanation.

---

## 32. Review priority aggregation

Global review priority is the highest justified safety/review priority among current supported/possible hypotheses and severe findings.

But:

```text
highest review priority
!= highest diagnostic probability
```

Priority drivers must be listed explicitly.

---

## 33. No hidden scoring

Do not create:
- evidence counts;
- weighted scores;
- Bayes-like pseudo-probabilities;
- confidence percentages;
- disease rankings;
- top-1 diagnosis.

A future calibrated probabilistic model would require separate validation and is out of scope.

---

## 34. Doctor review

The arbitration output is an organized differential for clinician review.

It must not:
- finalize diagnosis;
- choose treatment;
- suppress unresolved alternatives;
- convert itself directly into FINAL_REPORT without doctor review.

---

## 35. Hard constraints

Hermes MUST NOT:

1. Rank diseases by number of supporting items.
2. Rank diseases by AI scores.
3. Convert support states into hidden probabilities.
4. Count shared evidence as independent confirmation.
5. Count duplicate labels as multiple independent evidence items.
6. Treat missing evidence as negative evidence.
7. Treat No Finding as global disease exclusion.
8. Assume competing hypotheses are mutually exclusive.
9. Force a single unifying diagnosis.
10. Erase a hypothesis merely because another becomes confirmed.
11. Ignore possible coexistence of independent diseases.
12. Use a universal evidence hierarchy across all diseases.
13. Let newer evidence erase old provenance.
14. Turn urgency into diagnostic certainty.
15. Turn diagnostic certainty into urgency.
16. Invent disease-specific confirmation outside the owning module.
17. Infer causal relationship between two diseases without evidence.
18. Infer metastasis/source relationship without explicit support.
19. Generate a top-1 diagnosis or numeric disease ranking.
20. Issue autonomous treatment/testing/procedure/disposition actions.
21. Omit doctor review.
