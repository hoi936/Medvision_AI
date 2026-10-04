# CLINICAL_DATASET_EVALUATION_EVIDENCE.md

## 0. Mục tiêu

Giai đoạn tiếp theo của MedVision là:

**Clinical Dataset Evaluation v1**

Mục tiêu là đánh giá hệ thống trên một bộ ca độc lập có chuẩn tham chiếu rõ ràng, thay vì chỉ kiểm tra các quy tắc nội bộ hoặc ca golden được xây để kiểm thử.

Đây là bước chuyển từ:

```text
"Hệ thống có tuân thủ quy tắc đã thiết kế không?"
```

sang:

```text
"Trên dữ liệu độc lập, hệ thống hoạt động như thế nào so với chuẩn tham chiếu?"
```

---

## 1. Không gọi nhầm là "clinical validation" hoàn chỉnh

Dataset Evaluation v1 là đánh giá hồi cứu/offline nếu dùng dữ liệu có sẵn.

Nó không tự chứng minh:
- lợi ích lâm sàng;
- cải thiện kết cục bệnh nhân;
- hiệu quả khi bác sĩ sử dụng trong môi trường thật;
- an toàn triển khai thực tế.

Các đánh giá đó thuộc giai đoạn live/clinical evaluation sau này.

---

## 2. Calibration không mặc định áp dụng cho Hermes

Hermes hiện chủ động không tạo:
- xác suất bệnh;
- disease score;
- ranking;
- top diagnosis.

Do đó không được ép dùng các chỉ số calibration xác suất như:
- Brier score;
- expected calibration error;
- calibration slope/intercept;

cho các đầu ra bệnh của Hermes.

Chỉ dùng calibration xác suất nếu một thành phần thực sự phát ra xác suất được định nghĩa và được đánh giá riêng.

Đối với Hermes, v1 tập trung vào:
- độ phù hợp trạng thái suy luận;
- lỗi ngữ nghĩa;
- lỗi an toàn;
- bảo toàn provenance;
- missingness;
- conflict;
- temporal correctness;
- report fidelity.

---

## 3. Bộ dữ liệu đánh giá phải độc lập với golden/test cases

Không được dùng:
- golden cases hiện có;
- E2E01–E2E36;
- PB01–PB24;
- ca đã dùng để viết rule;
- ca đã dùng để sửa regression;

làm bộ đánh giá độc lập chính.

Nếu dùng để sanity check thì phải ghi rõ là internal test, không phải external evaluation.

---

## 4. Đơn vị chia dữ liệu

Ưu tiên chia theo:

```text
patient-level
```

không chia ngẫu nhiên theo từng ảnh nếu cùng bệnh nhân có nhiều lần chụp.

Với longitudinal cases:
- toàn bộ timepoints của một bệnh nhân phải ở cùng một split;
- tránh một lần chụp vào development và lần khác vào evaluation.

Nếu có nhiều cơ sở:
- có thể dùng site-based external split.

Nếu có dữ liệu nhiều thời kỳ:
- có thể dùng temporal split.

---

## 5. Dataset provenance

Mỗi dataset cần ghi:

```yaml
dataset:
  name:
  source:
  institution:
  date_range:
  inclusion_criteria:
  exclusion_criteria:
  patient_count:
  study_count:
  timepoint_count:
  deidentification_method:
  split_method:
  overlap_check:
```

Không lưu thông tin định danh bệnh nhân trong test artifacts.

---

## 6. Case schema

Mỗi case đánh giá nên có:

```yaml
case:
  case_id:
  patient_group_id:

  imaging:
    cxr:
    ct:
    other:

  clinical:
    symptoms:
    signs:
    history:

  labs: []
  physiology: []
  microbiology: []
  pathology: []

  longitudinal:
    timepoints: []

  reference_standard:
    finding_reference:
    disease_reference:
    temporal_reference:
    report_reference:

  adjudication:
    reviewers:
    method:
    disagreement:
    final_reference:

  metadata:
    site:
    time_period:
    subgroup_labels: []
```

Chỉ chứa dữ liệu thực sự có trong dataset.

Missing phải được biểu diễn rõ.

---

## 7. Reference standard

Không dùng một chuẩn tham chiếu duy nhất cho mọi loại câu hỏi.

### Finding-level
Có thể dùng:
- báo cáo X-quang được bác sĩ chẩn đoán hình ảnh duyệt;
- đọc lại ảnh bởi chuyên gia;
- consensus/adjudication.

### Disease-level
Có thể cần:
- CT/HRCT;
- siêu âm tim;
- pathology/cytology;
- microbiology;
- hồ sơ chẩn đoán lâm sàng;
- hội chẩn chuyên khoa.

### Temporal
Cần:
- đúng lesion/process correspondence;
- đúng timepoints;
- đủ khả năng so sánh.

### Final report
Có thể so:
- finding content;
- impression semantics;
- uncertainty;
- provenance-sensitive facts;

nhưng không nên dùng exact-string match làm chỉ số chính.

---

## 8. Adjudication

Nếu chuẩn tham chiếu cần bác sĩ đọc:

Khuyến nghị:
- ít nhất hai người đọc độc lập ở subset quan trọng;
- disagreement được ghi lại;
- có quy trình adjudication;
- reviewer không thấy output Hermes khi tạo reference nếu thiết kế cho phép.

Không biến một báo cáo lâm sàng đơn lẻ thành ground truth tuyệt đối nếu câu hỏi cần bằng chứng mạnh hơn.

---

## 9. Đánh giá theo tầng

Không dùng một điểm tổng hợp duy nhất.

Tách ít nhất thành:

```text
A. Finding-level evaluation
B. Disease-reasoning evaluation
C. Temporal evaluation
D. Cross-disease arbitration evaluation
E. Safety-semantic evaluation
F. Doctor-review/final-report fidelity
```

---

## 10. Finding-level evaluation

Đánh giá các 14 finding classes riêng.

Có thể báo:
- sensitivity;
- specificity;
- PPV;
- NPV;
- F1;
- confusion counts;

nếu reference standard phù hợp.

Tuy nhiên phải phân biệt:
- performance của upstream image model;
- performance của Hermes reasoning.

Nếu Hermes chỉ nhận canonical AI output, sai số detection của image model không được gán nhầm thành lỗi reasoning của Hermes.

---

## 11. Disease-reasoning evaluation

Hermes có bounded states thay vì binary diagnosis.

Không ép mọi output thành yes/no nếu không phù hợp.

Đánh giá:
- state agreement;
- unsupported confirmation rate;
- unsupported etiology rate;
- correct preservation of indeterminate state;
- correct use of definitive evidence;
- false-upgrade rate.

Ví dụ:

```text
Nodule/Mass + no pathology
```

Hermes giữ concern/indeterminate là đúng hơn việc ép thành cancer/no cancer.

---

## 12. Suggested disease-state evaluation matrix

Có thể chuẩn hóa cho từng module:

```text
SUPPORTED
POSSIBLE / INDETERMINATE
CONFLICTED
NOT_ESTABLISHED
CONFIRMED_BY_DEFINITIVE_SOURCE
```

Nhưng mapping phải được định nghĩa trước theo từng disease module.

Không tạo một mapping chung nếu làm mất semantics của module.

---

## 13. Safety-semantic metrics

Bắt buộc báo riêng các tỷ lệ:

```text
unsupported diagnosis rate
unsupported etiology rate
score-to-probability violation rate
missing-to-negative violation rate
autonomous-action violation rate
doctor-review-bypass rate
ranking violation rate
provenance-loss rate
conflict-erasure rate
```

Mục tiêu safety gate có thể là:

```text
0 critical semantic violations
```

trên bộ evaluation được chọn.

---

## 14. Temporal metrics

Đánh giá riêng:

```text
NEW correctness
RESOLVED correctness
STABLE correctness
PERSISTENT correctness
RECURRENT correctness
IMPROVED/WORSENED correctness
INDETERMINATE correctness
```

Quan trọng nhất là false progression/new/resolution rate.

Không chỉ đo số trạng thái đúng; phải ghi những trường hợp model đáng ra phải abstain/indeterminate nhưng lại kết luận cứng.

---

## 15. Arbitration metrics

Đánh giá:
- shared evidence recognized;
- duplicate evidence deduplicated;
- coexistence preserved;
- unresolved attribution preserved;
- ranking violation;
- forced single-diagnosis rate.

Không yêu cầu Hermes chọn "bệnh đúng nhất" nếu kiến trúc không có chức năng đó.

---

## 16. Abstention / indeterminate quality

Với hệ thống an toàn, `INDETERMINATE` đôi khi là output đúng.

Phải đánh giá:
- appropriate indeterminate;
- unnecessary indeterminate;
- unsafe overcommitment.

Không tối ưu đơn thuần để giảm số ca indeterminate.

---

## 17. Report fidelity

Đánh giá report candidate sau doctor-review fixture hoặc doctor-reviewed data.

Kiểm tra:
- rejected content không quay lại;
- modified content dùng đúng doctor value;
- deferred uncertainty được giữ;
- missing metadata không bị bịa;
- no autonomous recommendation;
- no auto-finalization;
- version binding đúng.

Text similarity chỉ là phụ trợ.

---

## 18. Subgroup analysis

Nếu dataset đủ số lượng, xem xét các nhóm:
- tuổi;
- giới tính;
- cơ sở;
- loại máy/chế độ chụp;
- AP/PA nếu metadata có;
- inpatient/outpatient nếu có;
- bệnh phổ biến/hiếm;
- single vs multiple findings;
- có/không có dữ liệu bổ sung;
- single-timepoint vs longitudinal.

Không báo subgroup khi cỡ mẫu quá nhỏ mà không kèm cảnh báo.

Không tự suy race/ethnicity hoặc thuộc tính nhạy cảm nếu dataset không có.

---

## 19. Confidence intervals

Các metric chính nên kèm:
- numerator/denominator;
- point estimate;
- 95% confidence interval.

Có thể dùng:
- exact/binomial CI;
- bootstrap ở patient-level;

tùy metric.

Bootstrap phải resample theo patient, không theo image khi một bệnh nhân có nhiều ảnh.

---

## 20. Pre-specification

Trước khi chạy evaluation chính, khóa:

```text
dataset version
system version
Hermes version/commit
provider/model
prompt/skill snapshot
metrics
primary endpoints
subgroups
reference-standard rules
missing-data handling
failure policy
```

Không sửa metric sau khi xem kết quả chỉ để đẹp hơn.

---

## 21. Freeze evaluated system

Evaluation chính phải gắn với một system snapshot.

Ví dụ:

```yaml
system_under_evaluation:
  repository_commit:
  hermes_version: v0.21.4
  hermes_commit: 2552fb543bd12a326d23449f41a9c13c48eb4e9a
  provider:
  model:
  skills_hash:
  configuration_hash:
```

Nếu thay model/skill/rule:
- đó là system version khác;
- cần rerun hoặc ghi rõ phần bị ảnh hưởng.

---

## 22. Provider variability

Nếu dùng LLM provider:
- REAL_GATE có thể chạy 1 trial/case;
- robustness evaluation dùng fixed repeated trials.

Dataset evaluation phải ghi rõ:
- số trial/case;
- temperature/settings nếu provider expose;
- model version;
- provider date/version nếu có.

Không cherry-pick.

---

## 23. Data leakage

Phải kiểm tra:
- duplicate patient/study;
- exact duplicate image;
- duplicated report;
- case overlap với golden/test fixtures;
- development/evaluation overlap.

Với foundation model provider, không thể khẳng định chắc dataset chưa từng xuất hiện trong pretraining nếu không có bằng chứng từ provider.

Phải ghi đây là limitation nếu phù hợp.

---

## 24. Dataset shift

Khi có thể, báo:
- site shift;
- temporal shift;
- equipment/protocol shift;
- disease-prevalence shift;
- documentation style shift.

Một internal test set tốt không thay thế external-site evaluation.

---

## 25. Primary endpoints đề xuất

Không dùng một single composite score.

Đề xuất primary safety endpoints:

```text
critical semantic violation rate
unsupported diagnosis rate
autonomous action violation rate
doctor-review bypass rate
provenance failure rate
```

Primary clinical-semantic endpoints tùy module:

```text
disease-state agreement
definitive-evidence confirmation correctness
temporal-state correctness
```

---

## 26. Secondary endpoints

Có thể gồm:
- latency;
- parse success;
- completeness;
- indeterminate rate;
- conflict-preservation rate;
- report fidelity;
- token usage/cost.

Không dùng cost/latency để che safety failure.

---

## 27. Error analysis

Mỗi error nên được phân loại:

```text
input/data error
reference-standard ambiguity
finding error
disease semantic error
temporal error
arbitration error
safety error
doctor-review boundary error
report rendering error
provider formatting error
```

Error analysis phải giữ case examples de-identified.

---

## 28. Dataset evaluation report

Báo cáo cuối nên có:
- dataset provenance;
- inclusion/exclusion;
- patient/study counts;
- missingness;
- reference-standard method;
- system snapshot;
- provider/model;
- metrics + CI;
- subgroup results;
- failure examples;
- limitations;
- data leakage considerations;
- versioning.

---

## 29. Không gọi "clinical utility"

Nếu chỉ offline retrospective evaluation:
- không kết luận cải thiện patient outcomes;
- không kết luận giúp bác sĩ tốt hơn trong thực tế;
- không kết luận an toàn triển khai.

Giai đoạn sau mới có thể dùng:
- reader study;
- silent deployment;
- prospective evaluation;
- early live clinical evaluation.

---

## 30. Hard constraints

Dataset Evaluation v1 MUST NOT:

1. dùng golden cases làm independent test set chính;
2. gộp patient timepoints qua nhiều split;
3. tự tạo ground truth thiếu bằng chứng;
4. coi report đơn lẻ là definitive standard cho mọi task;
5. ép probability calibration lên outputs không phải xác suất;
6. giảm indeterminate chỉ để tăng apparent accuracy;
7. dùng exact text match làm clinical correctness chính;
8. thay system sau khi evaluation bắt đầu mà không version;
9. cherry-pick provider trials;
10. gọi offline test là clinical utility;
11. thêm clinical rules để sửa kết quả;
12. thay Hermes pin/provider config âm thầm.
