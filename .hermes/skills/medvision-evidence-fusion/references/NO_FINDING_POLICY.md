# NO_FINDING_POLICY.md

## Policy target

Integrate these rules into the existing:

`medvision-evidence-fusion`

Do NOT create a new skill.

## Canonical name

Use the exact canonical class name already present in project data:

`No finding`

Do not introduce an alias unless the canonicalization layer already supports one.

## Policy states

### State A — NO_FINDING_ONLY

Condition:

```text
No finding == POSITIVE
AND
zero of the 14 target findings == POSITIVE
```

Interpretation:

`NO_FINDING_WITHIN_14_CLASS_TAXONOMY`

Required:
- preserve score/decision;
- select no finding-specific skill;
- do not say healthy/no disease;
- continue core safety/disease reasoning.

### State B — NO_FINDING_CONTRADICTION

Condition:

```text
No finding == POSITIVE
AND
>=1 target finding == POSITIVE
```

Required:
- preserve all results;
- emit `NO_FINDING_CONTRADICTION`;
- preserve positive finding skill routing;
- list conflicting positive findings;
- no automatic winner;
- doctor review.

### State C — POSITIVE_FINDING_WITH_NO_FINDING_NEGATIVE

Condition:

```text
No finding != POSITIVE
AND
>=1 target finding == POSITIVE
```

Required:
- route positive findings normally;
- no No-finding contradiction.

### State D — NO_FINDING_NOT_ESTABLISHED

Condition:

```text
No finding == NEGATIVE
AND
zero target findings == POSITIVE
```

or, if policy schema permits:

```text
No finding is missing
AND
zero target findings == POSITIVE
```

Required:
- do not synthesize normal;
- do not synthesize abnormal;
- preserve missing/negative distinction.

## Selector contract

No finding must never change the frozen selector condition:

`canonical finding decision == POSITIVE`

for the 14 positive findings.

No finding must never be mapped to a skill.

## Conflict object

Preferred representation:

```yaml
no_finding_conflict:
  present: true
  type: NO_FINDING_CONTRADICTION
  conflicting_positive_findings:
    - Pneumothorax
    - Pleural effusion
  resolution: doctor_review_required
```

If the current schema already has `EVIDENCE_CONFLICT`, nest or alias this as a subtype rather than creating a parallel incompatible conflict system.

## Prompt behavior

Evidence-fusion reasoning should explicitly know:

- No finding means absence of the 14 target findings when used according to source taxonomy.
- It does not exclude all disease.
- Positive No finding and positive target finding are internally inconsistent AI evidence.
- Raw evidence must be preserved.
- Positive findings must not be suppressed.
- Severe clinical evidence still reaches safety-check even when No finding is positive.

## Missing-data behavior

Never convert:
- missing No finding → NEGATIVE;
- NEGATIVE No finding → abnormal;
- all 14 NEGATIVE → No finding POSITIVE.

Only use actual supplied decisions.

## No Finding and doctor review

Doctor review remains required in every state.

No Finding is not an autonomous clearance decision.
