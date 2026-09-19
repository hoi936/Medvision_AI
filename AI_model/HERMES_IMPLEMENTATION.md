# Hermes Clinical Reasoning — Implementation Report

## A. Architecture before changes

The Streamlit form collected demographics, symptoms, history, and laboratory
information in four free-text fields. `hermes_report.py` converted these fields
to an XML-like prompt with a separate `field_presence` element. One Hermes skill
performed validation, evidence fusion, safety checking, differential reasoning,
and report generation in a single pass.

```text
Streamlit free text + 14 model results
        -> XML-like prompt / field_presence
        -> one disease-analysis skill
        -> Markdown report
```

## B. Problems found

- `field_presence=true` and `provided=true` were separate concepts, allowing
  valid data to be treated as unavailable.
- Vitals, laboratory results, missing tests, risk factors, and clinician
  requests could be mixed in free text.
- Model findings omitted margin and confidence band.
- Evidence provenance and clinical verification status were not represented.
- A single skill owned unrelated validation, fusion, safety, and reporting jobs.
- The frontend could not capture symptom duration or laboratory units/ranges in
  a stable structure.
- The report prompt repeated safety language and did not enforce the ten-section
  clinician-oriented output required by `yeucau.md`.

## C–D. Files and changes

- `clinical_schema.py`: canonical schema, legacy normalization, validation,
  provenance, score margin, and configurable confidence bands.
- `app.py`: structured form for demographics, symptoms/duration/severity,
  history, risk factors, vitals, laboratory results, missing tests, and clinician
  requests. The clinician request is never used as patient evidence.
- `hermes_report.py`: normalizes once, sends canonical JSON only, and preloads
  the three scoped skills with the `clarify` toolset.
- `.hermes/skills/medvision-evidence-fusion/SKILL.md`: evidence matrix,
  overlap, negative-evidence, localization, timing, and provenance rules.
- `.hermes/skills/medvision-safety-check/SKILL.md`: clinical-first safety check
  without autonomous emergency disposition.
- `.hermes/skills/medvision-disease-analysis/SKILL.md`: concise differential
  and report generation with mandatory physician review.
- `acceptance_case.py`: reusable canonical case from requirement section 21.
- `tests/test_clinical_schema.py` and `tests/test_hermes_report.py`: schema,
  compatibility, confidence-band, prompt, and CLI-boundary tests.

## E. Canonical request schema

```json
{
  "schema_version": "1.0",
  "workflow_mode": "WITH_LABS | MISSING_LABS",
  "general_info": {
    "provided": true,
    "verified": false,
    "source": "USER_PROVIDED",
    "value": {"age": 67, "sex": "Female"}
  },
  "symptoms": {
    "provided": true,
    "verified": false,
    "source": "USER_PROVIDED",
    "items": [{"name": "dyspnea", "duration": "2 months", "severity": "progressive"}]
  },
  "history": {"provided": true, "verified": false, "source": "USER_PROVIDED", "items": []},
  "risk_factors": {"provided": true, "verified": false, "source": "USER_PROVIDED", "items": []},
  "vitals": {"provided": true, "verified": false, "source": "VITAL_SIGN", "measurements": {}},
  "laboratory": {"provided": true, "verified": false, "source": "LAB", "results": []},
  "missing_tests": ["Chest CT"],
  "clinician_request": {"provided": true, "verified": false, "source": "USER_PROVIDED", "value": "..."},
  "model_findings": {
    "provided": true,
    "verified": false,
    "source": "IMAGE_MODEL",
    "score_calibrated_as_probability": false,
    "findings": [{
      "name": "Pulmonary fibrosis",
      "score": 0.8576,
      "threshold": 0.894,
      "margin": -0.0364,
      "decision": "NEGATIVE",
      "confidence_band": "NEAR_THRESHOLD_NEGATIVE",
      "bbox": null,
      "laterality": null,
      "anatomic_location": null,
      "gradcam_available": false
    }]
  }
}
```

Legacy `field_presence.x=true` is converted to `x.provided=true` only when the
corresponding content is non-empty. `provided` never implies `verified`.

## F. Updated skill flow

```text
Structured frontend / legacy adapter
        -> canonical normalization + validation
        -> model margin/confidence band
        -> medvision-evidence-fusion
        -> medvision-safety-check
        -> medvision-disease-analysis
        -> draft report
        -> mandatory physician review
```

## G–H. Tests and regression result

Ten deterministic unit tests pass. They verify:

- legacy `field_presence` compatibility;
- separation of `provided` and `verified`;
- all 14 acceptance-case findings survive normalization;
- pulmonary fibrosis remains `NEGATIVE / NEAR_THRESHOLD_NEGATIVE`;
- pneumothorax remains `NEGATIVE / CLEAR_NEGATIVE`;
- thresholds are unchanged;
- clinical and image provenance is retained;
- the prompt contains canonical JSON and mandatory review status;
- Hermes receives only the `clarify` toolset and all three clinical skills.

All three project-local skills pass the skill validator. Streamlit smoke testing
completed with zero exceptions. A live acceptance run requires configured LLM
credits; deterministic schema regression does not require network access.

## I. Example expected report for the acceptance case

The following is an expected-format example, not a physician-approved report
and not a claim that a live LLM produced it.

# BÁO CÁO HỖ TRỢ QUYẾT ĐỊNH LÂM SÀNG — BẢN NHÁP

## 1. Dữ liệu hiện có

Nữ, 67 tuổi; khó thở khi gắng sức tiến triển khoảng 2 tháng, nặng hơn trong 2
tuần gần đây; ho khan khoảng 6 tuần; giảm khả năng gắng sức. SpO₂ được báo cáo
93% khí phòng và nhịp thở 22/phút. Có dữ liệu xét nghiệm nhưng không kèm khoảng
tham chiếu hoặc thời điểm lấy mẫu. Chưa có CT ngực.

## 2. Findings từ mô hình ảnh

| Finding | Score | Threshold | Margin | Decision | Confidence band |
|---|---:|---:|---:|---|---|
| Calcification | 0.9997 | 0.9072 | +0.0925 | POSITIVE | CLEAR_POSITIVE |
| Pleural effusion | 0.9792 | 0.9136 | +0.0656 | POSITIVE | CLEAR_POSITIVE |
| Nodule/Mass | 0.9172 | 0.9043 | +0.0129 | POSITIVE | NEAR_THRESHOLD_POSITIVE |
| Pleural thickening | 0.8682 | 0.8369 | +0.0313 | POSITIVE | NEAR_THRESHOLD_POSITIVE |
| Pulmonary fibrosis | 0.8576 | 0.8940 | -0.0364 | NEGATIVE | NEAR_THRESHOLD_NEGATIVE |

Các score là đầu ra mô hình chưa calibration, không phải xác suất mắc bệnh.

## 3. Bằng chứng lâm sàng

Khó thở tiến triển, SpO₂ 93% khí phòng và RR 22/phút là dữ liệu cần đối chiếu
trực tiếp. Không sốt cao, WBC 8,9 và nhiệt độ 36,8°C làm bằng chứng cho nhiễm
trùng cấp kém nổi bật hơn, nhưng không loại trừ nhiễm trùng. Khoảng tham chiếu
xét nghiệm không được cung cấp nên các giá trị chỉ được mô tả theo số đo.

## 4. Tích hợp bằng chứng

Pleural effusion và pleural thickening tạo một pattern bất thường màng phổi cần
được bác sĩ/radiologist xác nhận. Calcification và Nodule/Mass có thể liên quan
hoặc là hai finding khác nhau; classification output không có localization nên
không thể kết luận chúng thuộc cùng một tổn thương. Pulmonary fibrosis vẫn là
uncertainty gần threshold dù quyết định nhị phân chính thức là NEGATIVE.

## 5. Chẩn đoán phân biệt

- Bất thường màng phổi mạn hoặc có dịch: được hỗ trợ bởi hai finding màng phổi
  và triệu chứng hô hấp; thiếu localization, mô tả phim chuẩn và CT để xác nhận.
- Tổn thương dạng nốt/khối có vôi hóa: cần được xem xét, nhưng finding này không
  đồng nghĩa ung thư. Chưa có kích thước, số lượng, bên, vùng phổi hay độ ổn định.
- Pattern nhiễm trùng cấp hiện ít được hỗ trợ hơn do không sốt cao, nhiệt độ và
  WBC được báo cáo không nổi bật, cùng score Consolidation rất thấp; không được
  xem là đã loại trừ.

## 6. Thông tin còn thiếu

- ESSENTIAL: bác sĩ/radiologist đọc phim gốc và xác nhận findings/localization.
- USEFUL: phim cũ để đánh giá tính ổn định của finding Nodule/Mass.
- OPTIONAL/CONDITIONAL: CT ngực nếu bác sĩ thấy phù hợp sau khi khám và đọc phim.

## 7. Bước xác nhận để bác sĩ cân nhắc

Đối chiếu triệu chứng, khám trực tiếp, đo lại SpO₂/RR và đọc phim chuẩn. Cân nhắc
hình ảnh bổ sung dựa trên đánh giá của bác sĩ; đây không phải chỉ định tự động.

## 8. Safety flags

SpO₂ 93% khí phòng cùng khó thở tiến triển cần được đánh giá trực tiếp kịp thời.
Dữ liệu hiện có không đủ để hệ thống tự xác định mức độ cấp cứu.

## 9. Giới hạn

Bản nháp dùng kết quả classification không có localization và dữ liệu chưa được
xác minh lâm sàng; không phải chẩn đoán hoặc kế hoạch điều trị.

## 10. Trạng thái duyệt

review_status: PENDING_CLINICIAN_REVIEW
requires_doctor_review: true

## J. Remaining limitations

- No authentication, role-based physician identity, digital signature, database,
  audit trail, FHIR/EHR integration, or production privacy controls.
- No prospective clinical validation, calibration study, regulatory clearance,
  or evidence that generated reports improve outcomes.
- Structured values are accepted as entered; production deployment needs strict
  numeric/unit/range validation and terminology coding.
- The LLM can still make errors; deterministic post-generation validation of
  every clinical claim is not yet implemented.
