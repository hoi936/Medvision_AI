# references.md — Final Report Generation v1

## S1 — ACR Practice Parameter for Communication of Diagnostic Imaging Findings

American College of Radiology.  
**ACR Practice Parameter for Communication of Diagnostic Imaging Findings.**  
Current ACR Practice Parameters & Technical Standards portal document.  
Portal: https://gravitas.acr.org/PPTS/GetDocumentView?docId=74

### Used for
- The final report is the definitive documentation of the imaging examination/procedure interpretation.
- Report components include patient/study identification, relevant clinical information, body/findings, potential limitations, comparison studies/reports when appropriate and available, and an impression/conclusion.
- The impression should communicate the clinically important conclusion/differential when appropriate.
- Standardized computer-generated templates may be used to support consistent reports.
- Preliminary/nonroutine communications are distinct from the final report.

### MedVision scope constraint
MedVision does not autonomously create physician conclusions or follow-up recommendations. Final-report content must originate from doctor-reviewed state, and any recommendation/action language must be explicitly clinician-authored or externally sourced.

---

## S2 — RSNA RadReport Reporting Templates

Radiological Society of North America.  
**RadReport reporting templates.**  
URL: https://www.rsna.org/practice-tools/data-tools-and-standards/radreport-reporting-templates

### Used for
- Structured reporting can improve consistency, completeness, readability and machine readability.
- Reports should use standardized, comprehensible structure and terminology.
- Template use must not replace clinical interpretation.

---

## S3 — RSNA RadLex and RadElement

Radiological Society of North America.  
**RadLex radiology lexicon.**  
URL: https://www.rsna.org/practice-tools/data-tools-and-standards/radlex-radiology-lexicon

Radiological Society of North America.  
**RadElement common data elements.**  
URL: https://www.rsna.org/practice-tools/data-tools-and-standards/radelement-common-data-elements

### Used for
- Standard terminology and structured data elements can improve consistency and interoperability.
- Controlled terminology should preserve, not distort, clinician-authored meaning.

---

## S4 — FDA Clinical Decision Support Software Guidance (January 2026)

U.S. Food and Drug Administration.  
**Clinical Decision Support Software: Guidance for Industry and Food and Drug Administration Staff.**  
Final Guidance. January 2026.  
URL: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software

### Used for
- The health-care professional should be able to independently review the basis of software recommendations.
- Relevant patient-specific information, knowns/unknowns, input information, logic/method basis, validation context and limitations support independent professional judgment.

### Important scope note
Because MedVision processes chest radiographs, this source must not be used to infer that MedVision is a non-device CDS function. It is used only for transparency/human-review principles.

---

## S5 — Existing MedVision frozen workflow

Authoritative internal workflow:

```text
AI_RESULT
→ Hermes assessment
→ DRAFT_REPORT
→ DOCTOR_REVIEW
→ FINAL_REPORT
```

Frozen constraints:
- `AI_RESULT`, `DOCTOR_REVIEW`, and `FINAL_REPORT` remain separate.
- Original AI/Hermes provenance is immutable.
- Doctor review is mandatory.
- Hermes cannot self-finalize.
- Missing stays missing.
- Conflicts/uncertainty are preserved.
- No autonomous treatment/procedure/disposition logic.
- Structured Doctor Review v1 owns review completion/readiness/finalization authority.

---

# MedVision internal final-report labels

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

These are MedVision workflow states, not formal ACR/FDA terminology.
