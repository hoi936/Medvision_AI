You are working on the MedVision AI Platform, specifically the Hermes Clinical Reasoning subsystem.

Your task is to AUDIT, REFACTOR, AND IMPROVE all existing Hermes skills, prompts, input schemas, validators, evidence-fusion logic, and report-generation logic.

Do not only edit wording. Inspect the complete Hermes workflow and fix architectural inconsistencies between:
- Frontend input
- Backend payload
- Hermes skills
- Prompt templates
- Evidence validation
- Model findings
- Clinical reasoning
- Missing-data reasoning
- Report generation

============================================================
1. PRIMARY GOAL
============================================================

Hermes is a clinical reasoning assistant for chest X-ray analysis.

The complete workflow is:

Chest X-ray
    ↓
Image AI model
    ↓
14 radiographic findings
    ↓
Clinical information
    ├── demographics
    ├── symptoms
    ├── symptom duration
    ├── medical history
    ├── risk factors
    ├── vital signs
    └── laboratory results
    ↓
Hermes Evidence Fusion
    ↓
Clinical interpretation
    ↓
Differential diagnosis
    ↓
Missing information / recommended confirmation
    ↓
Draft clinical report
    ↓
Mandatory physician review

Hermes MUST NOT treat radiographic findings as final diagnoses.

Example:

Pleural effusion = image finding.

It does NOT automatically mean:
- heart failure
- malignancy
- tuberculosis
- pneumonia

Hermes must combine imaging findings with clinical evidence before generating differential considerations.

============================================================
2. FIX THE INPUT CONTRACT FIRST
============================================================

The current implementation has an important bug:

Frontend/backend may send:

"field_presence": {
    "general_info": true,
    "symptoms": true,
    "history": true,
    "laboratory": true
}

while Hermes requires:

"provided": true

As a result, Hermes may receive real input but incorrectly mark it as unverified or unavailable.

Fix this permanently.

Implement ONE canonical normalized schema before any reasoning begins.

Recommended schema:

{
  "general_info": {
    "provided": true,
    "value": "Female, 67 years old"
  },

  "symptoms": {
    "provided": true,
    "items": [
      {
        "name": "dyspnea on exertion",
        "duration": "2 months",
        "severity": "progressive"
      },
      {
        "name": "dry cough",
        "duration": "6 weeks"
      }
    ]
  },

  "history": {
    "provided": true,
    "items": []
  },

  "risk_factors": {
    "provided": true,
    "items": []
  },

  "vitals": {
    "provided": true,
    "spo2": {
      "value": 93,
      "unit": "%",
      "context": "room air"
    },
    "respiratory_rate": {
      "value": 22,
      "unit": "/min"
    },
    "heart_rate": {
      "value": 88,
      "unit": "/min"
    },
    "blood_pressure": {
      "systolic": 138,
      "diastolic": 82,
      "unit": "mmHg"
    },
    "temperature": {
      "value": 36.8,
      "unit": "C"
    }
  },

  "laboratory": {
    "provided": true,
    "results": [
      {
        "name": "WBC",
        "value": 8.9,
        "unit": "10^9/L",
        "reference_range": null,
        "timestamp": null
      }
    ]
  },

  "missing_tests": [
    "Chest CT"
  ],

  "model_findings": {
    "provided": true,
    "model_name": null,
    "model_version": null,
    "findings": []
  }
}

IMPORTANT:

Normalize legacy inputs before sending them to reasoning skills.

For backward compatibility:

field_presence.x == true

MAY be normalized into:

x.provided == true

when the actual field contains non-empty patient data.

Do NOT force the reasoning model to understand multiple inconsistent schemas.

Create one normalization layer.

============================================================
3. SEPARATE DATA TYPES
============================================================

Do NOT combine all clinical information in free-text fields.

Separate:

A. demographics
B. symptoms
C. medical history
D. risk factors
E. vital signs
F. laboratory values
G. imaging findings
H. unavailable/missing tests
I. clinician/user requests

Example of a bad laboratory field:

"SpO2 93%, RR 22, WBC 8.9, no CT yet, please tell me
what tests are missing"

This contains:
- vital signs
- laboratory data
- missing-test status
- instruction text

These must be parsed into separate structures.

Never use user instructions as clinical evidence.

============================================================
4. MODEL FINDINGS SCHEMA
============================================================

Each image-model output must preserve ALL useful information.

Recommended structure:

{
  "name": "Pulmonary fibrosis",
  "score": 0.8576,
  "threshold": 0.8940,
  "margin": -0.0364,
  "decision": "NEGATIVE",
  "confidence_band": "NEAR_THRESHOLD_NEGATIVE",
  "bbox": null,
  "laterality": null,
  "anatomic_location": null,
  "gradcam_available": false
}

Do NOT send only:

Pulmonary fibrosis = NEGATIVE

because valuable model information is lost.

Calculate:

margin = score - threshold

============================================================
5. CONFIDENCE-BAND LOGIC
============================================================

Implement configurable confidence bands.

Suggested default:

if score >= threshold:
    decision = POSITIVE

if score < threshold and margin >= -0.05:
    confidence_band = NEAR_THRESHOLD_NEGATIVE

if score >= threshold and margin <= +0.05:
    confidence_band = NEAR_THRESHOLD_POSITIVE

otherwise:
    confidence_band = CLEAR_NEGATIVE or CLEAR_POSITIVE

Do NOT change the official binary model result.

The confidence band is additional information for clinical reasoning.

Example:

Pulmonary fibrosis
score = 0.8576
threshold = 0.8940
margin = -0.0364

Official decision:
NEGATIVE

Reasoning status:
NEAR_THRESHOLD_NEGATIVE

Compare with:

Pneumothorax
score = 0.0008
threshold = 0.9771

This should be:
CLEAR_NEGATIVE

Hermes must understand that these two NEGATIVE findings do not carry the same model evidence.

============================================================
6. DO NOT INTERPRET MODEL SCORE AS DISEASE PROBABILITY
============================================================

Enforce this globally.

Never write:

"99.97% probability the patient has calcification"

unless the model has specifically undergone appropriate probability calibration and this interpretation is explicitly supported.

Use wording such as:

"Model score: 0.9997, above the configured threshold of 0.9072."

or:

"The image model strongly activated for this finding."

Model score is not automatically disease probability.

============================================================
7. 14 CHEST X-RAY FINDINGS
============================================================

Hermes currently receives these findings:

1. Aortic enlargement
2. Atelectasis
3. Calcification
4. Cardiomegaly
5. Consolidation
6. ILD
7. Infiltration
8. Lung Opacity
9. Nodule/Mass
10. Other lesion
11. Pleural effusion
12. Pleural thickening
13. Pneumothorax
14. Pulmonary fibrosis

Treat these primarily as RADIOGRAPHIC FINDINGS.

Do not automatically convert them into diseases.

Examples:

Nodule/Mass
≠ lung cancer

Consolidation
≠ pneumonia

Pleural effusion
≠ heart failure

Calcification
≠ benign lesion

ILD finding
≠ a specific ILD diagnosis

============================================================
8. HANDLE OVERLAPPING FINDINGS
============================================================

The findings are not mutually exclusive.

Hermes must explicitly reason about possible overlap.

Examples:

Pleural effusion
+
Atelectasis

may coexist because pleural fluid can be associated with adjacent
compressive/passive atelectatic change.

Calcification
+
Nodule/Mass

may represent the same lesion, but Hermes MUST NOT assume they refer
to the same lesion unless localization information supports it.

ILD
+
Pulmonary fibrosis

may overlap but are not identical concepts.

Lung Opacity
+
Consolidation

may overlap.

Cardiomegaly
+
Lung Opacity
+
Pleural Effusion

may occur together in a congestive pattern, but this does not establish
heart failure without appropriate clinical context.

============================================================
9. LOCALIZATION RULES
============================================================

Never invent:
- laterality
- lung zone
- size
- number of lesions
- anatomical position

from classification scores alone.

If bbox/localization is available, use it.

If unavailable, explicitly state:

"Laterality and exact localization cannot be determined from the
classification output alone."

Grad-CAM must be treated as model interpretability support,
NOT as precise lesion segmentation or definitive localization.

============================================================
10. EVIDENCE FUSION
============================================================

Create or improve a dedicated Evidence Fusion skill.

It should build an evidence matrix for every relevant diagnostic hypothesis.

Each hypothesis should contain:

{
  "hypothesis": "...",

  "supporting_evidence": [
    {
      "source": "symptom | history | vital | lab | imaging_model",
      "evidence": "...",
      "strength": "strong | moderate | weak"
    }
  ],

  "contradicting_evidence": [],

  "uncertain_evidence": [],

  "missing_information": []
}

Do not count evidence mechanically.

Reason about clinical relationships.

============================================================
11. DIFFERENTIAL DIAGNOSIS LOGIC
============================================================

Hermes may generate differential considerations ONLY when enough
validated evidence exists.

For each consideration provide:

- supporting evidence
- evidence against
- unresolved uncertainty
- information required for confirmation

Avoid definitive diagnosis language.

Preferred:

"Findings may be compatible with..."

"One consideration is..."

"The available evidence supports consideration of..."

"Confirmation requires..."

Avoid:

"The patient has..."

unless the diagnosis was already explicitly confirmed in the provided
clinical record.

============================================================
12. USE NEGATIVE EVIDENCE CORRECTLY
============================================================

Negative evidence can alter reasoning but usually should not be used
as absolute exclusion.

Example:

No fever
Normal WBC
Low/normal inflammatory markers
Very low consolidation model score

may make an acute bacterial pneumonia pattern less supported.

But do not write:

"Pneumonia excluded."

Similarly:

Cardiomegaly model score low
+
BNP not elevated in context

may reduce support for a congestive cardiac explanation.

Do not claim absolute exclusion without appropriate evidence.

============================================================
13. LAB INTERPRETATION
============================================================

Laboratory values should contain:

- value
- unit
- reference range when available
- timestamp when available

If reference range is unavailable:

Hermes may describe the raw value but should avoid claiming
"high" or "low" unless interpretation is sufficiently standard and safe.

Prefer:

"CRP was reported as 7.2 mg/L; laboratory-specific reference range
was not supplied."

instead of inventing a normal range.

============================================================
14. TIME CONTEXT
============================================================

Clinical reasoning must account for timing.

Track when possible:

- symptom onset
- symptom duration
- lab collection time
- vital-sign measurement time
- imaging time
- admission time

Do not assume measurements were simultaneous.

If timestamps are missing, say so only when timing materially affects reasoning.

Do not repeat the warning excessively.

============================================================
15. MISSING-DATA MODE
============================================================

Missing-data reasoning must be clinically relevant and concise.

Do not ask for every possible medical test.

Identify the smallest set of missing information that could materially
change the differential.

Separate:

ESSENTIAL
USEFUL
OPTIONAL

Example:

Essential:
- original X-ray / radiologist interpretation when model finding is uncertain

Useful:
- prior imaging for stability of a pulmonary nodule

Conditional:
- CT chest if clinically indicated after physician review

Do not generate indiscriminate test shopping lists.

============================================================
16. SAFETY / URGENCY
============================================================

Create a separate safety-check skill.

Urgent escalation should be based primarily on clinical evidence, such as:

- severe or rapidly worsening dyspnea
- severe hypoxemia
- hemodynamic instability
- altered consciousness
- severe chest pain
- evidence compatible with tension pneumothorax
- other emergency features

Do not create emergency alerts merely because an image model has a high score.

Model findings can contribute to urgency but should be integrated with
clinical state.

============================================================
17. REPORT OUTPUT
============================================================

Final report should be concise enough for clinicians.

Recommended structure:

# Clinical Decision Support Draft

## 1. Available data
Short summary.

## 2. Image-model findings
Table:
Finding | Score | Threshold | Margin | Decision | Interpretation status

## 3. Clinical evidence
Relevant symptoms, history, vitals and labs.

## 4. Evidence integration
Explain which imaging and clinical evidence agrees or conflicts.

## 5. Differential considerations
For each:
- Supporting evidence
- Evidence against
- Uncertainty

## 6. Missing information
Only meaningful missing data.

## 7. Suggested confirmation steps for clinician consideration
No automatic orders.

## 8. Safety flags
Only when appropriate.

## 9. Limitations
Short, not repetitive.

## 10. Review status

review_status: PENDING_CLINICIAN_REVIEW
requires_doctor_review: true

============================================================
18. REDUCE EXCESSIVE DISCLAIMERS
============================================================

Safety warnings are important, but do not repeat the same disclaimer in
every section.

One concise limitation/safety section is enough unless a specific finding
requires immediate warning.

Current reports are too defensive when data-validation flags fail.

Fix the validation pipeline rather than generating pages of warnings.

============================================================
19. PROVENANCE
============================================================

Every piece of evidence should retain its source.

Possible sources:

USER_PROVIDED
EHR
LAB
VITAL_SIGN
IMAGE_MODEL
RADIOLOGY_REPORT
CLINICIAN_CONFIRMED

Optional fields:

{
  "source": "IMAGE_MODEL",
  "provided": true,
  "verified": false
}

Important distinction:

provided = data exists

verified = data has been clinically verified

Do NOT treat:

provided=false

and:

verified=false

as the same thing.

Data can be provided but not clinician-verified.

============================================================
20. PHYSICIAN REVIEW
============================================================

Hermes is a clinical decision-support prototype.

It must never silently convert AI output into an approved medical diagnosis.

Keep:

requires_doctor_review = true

for AI-generated reports.

No medication prescribing, dosing, treatment initiation, discharge decision,
or autonomous emergency disposition should be generated by Hermes.

============================================================
21. CURRENT TEST CASE / ACCEPTANCE TEST
============================================================

Use this case as a regression test.

Patient:
Female, age 67.

Symptoms:
- Progressive exertional dyspnea for approximately 2 months
- Worse during the last 2 weeks
- Dry cough for approximately 6 weeks
- Mild left chest heaviness/discomfort
- Reduced exercise tolerance
- No high fever
- No hemoptysis

History:
- Previous pneumonia approximately 8 years ago
- Recurrent respiratory infections
- Passive smoking exposure
- Long-term occupational dust exposure
- Mild hypertension
- No known heart failure
- Tuberculosis history unknown

Vitals:
SpO2 = 93% on room air
RR = 22/min
HR = 88/min
BP = 138/82 mmHg
Temperature = 36.8 C

Labs:
WBC = 8.9 x10^9/L
Neutrophils = 64%
Hemoglobin = 12.4 g/dL
Platelets = 268 x10^9/L
CRP = 7.2 mg/L
ESR = 28 mm/h
Creatinine = 0.81 mg/dL
BNP = 74 pg/mL

No chest CT currently available.

Image model:

Calcification
score 0.9997
threshold 0.9072
POSITIVE

Pleural effusion
score 0.9792
threshold 0.9136
POSITIVE

Nodule/Mass
score 0.9172
threshold 0.9043
POSITIVE

Pleural thickening
score 0.8682
threshold 0.8369
POSITIVE

Pulmonary fibrosis
score 0.8576
threshold 0.8940
NEGATIVE but NEAR_THRESHOLD_NEGATIVE

Other lesion
0.7630 / 0.9492
NEGATIVE

Lung Opacity
0.3563 / 0.9326
NEGATIVE

ILD
0.2909 / 0.8730
NEGATIVE

Aortic enlargement
0.2263 / 0.8477
NEGATIVE

Atelectasis
0.1747 / 0.9512
NEGATIVE

Cardiomegaly
0.0684 / 0.8257
NEGATIVE

Consolidation
0.0538 / 0.9663
NEGATIVE

Infiltration
0.0113 / 0.9551
NEGATIVE

Pneumothorax
0.0008 / 0.9771
NEGATIVE

EXPECTED BEHAVIOR:

1. Hermes MUST recognize the patient data as provided.
2. It MUST NOT stop reasoning because "provided=true" is missing from a
legacy frontend payload if field_presence=true and valid content exists.
3. It should recognize a pleural-abnormality pattern as a relevant
consideration.
4. It should integrate dyspnea and mild oxygen desaturation.
5. It should recognize that Calcification + Nodule/Mass may or may not
represent the same lesion.
6. It MUST NOT call the nodule cancer.
7. It should preserve Pulmonary fibrosis as near-threshold uncertainty.
8. It should recognize that acute infection has limited support from the
currently supplied evidence, rather than treating all differential
diagnoses equally.
9. It should avoid claiming laterality unless localization data is supplied.
10. It should recommend confirmation using appropriate imaging/clinical
review without issuing autonomous medical orders.
11. It should produce a useful clinical reasoning report rather than mainly
reporting schema-validation failures.
12. Physician review must remain mandatory.

============================================================
22. IMPLEMENTATION TASK
============================================================

Now inspect the actual repository.

Locate all relevant files related to:
- Hermes skills
- prompt templates
- JSON/Pydantic schemas
- frontend request payload
- backend request models
- evidence normalization
- clinical reasoning
- missing-data reasoning
- safety checks
- report generation

Do not assume filenames.

First map the current architecture.

Then:

1. Identify inconsistencies.
2. Explain root causes.
3. Refactor the input schema.
4. Add a normalization layer.
5. Update affected skills.
6. Add score-margin/confidence-band logic.
7. Improve evidence fusion.
8. Improve missing-data handling.
9. Improve report output.
10. Add unit tests.
11. Add the regression test case above.
12. Preserve backward compatibility where reasonable.
13. Do not break existing Image AI APIs.
14. Do not change the model's trained thresholds unless explicitly required.
15. Do not fabricate clinical information.

============================================================
23. REQUIRED OUTPUT AFTER IMPLEMENTATION
============================================================

At completion provide:

A. Architecture before changes
B. Problems found
C. Files modified
D. Explanation of each change
E. New normalized request schema
F. Updated skill flow
G. Unit tests added
H. Regression-test result
I. Example final Hermes report for the test case
J. Remaining limitations

Do not merely recommend changes.

IMPLEMENT THEM in the repository.