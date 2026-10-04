# HUMAN_AI_READER_STUDY_EVIDENCE.md

## 0. Mục tiêu

Giai đoạn tiếp theo sau Clinical Dataset Evaluation scaffold là:

**Human-AI Reader Study / Clinician Evaluation v1**

Mục tiêu là xây hạ tầng để đánh giá câu hỏi:

```text
Khi bác sĩ sử dụng MedVision/Hermes,
độ chính xác, mức an toàn, thời gian làm việc
và cách xử lý sai lệch thay đổi như thế nào
so với khi không có Hermes?
```

Đây là đánh giá của **đội người–AI**, không chỉ đánh giá model.

---

## 1. Trạng thái v1

V1 chỉ triển khai **study/evaluation infrastructure**.

Nếu chưa có:
- dataset độc lập;
- provider/model;
- người đọc tham gia;
- protocol hoàn chỉnh;
- quyết định về đạo đức/nghiên cứu và quyền riêng tư của cơ sở thực hiện;

thì phải báo:

```text
HUMAN-AI READER STUDY HARNESS: IMPLEMENTED
HUMAN-AI READER STUDY: NOT RUN
```

Không tạo kết quả giả.

---

## 2. Không dùng trên bệnh nhân thật ở v1

Mặc định Reader Study v1 là:
- retrospective;
- offline;
- de-identified;
- không ảnh hưởng chăm sóc bệnh nhân hiện tại.

Không triển khai silent/live/prospective use trong phase này.

Nếu sau này chuyển sang môi trường thật, phải có protocol riêng.

---

## 3. Đối tượng đánh giá

Reader nên đại diện người dùng dự kiến của MedVision.

Có thể gồm:
- bác sĩ chẩn đoán hình ảnh;
- bác sĩ nội trú/chuyên khoa phù hợp;

nhưng protocol phải định nghĩa trước.

Không trộn các nhóm kinh nghiệm mà không ghi nhận.

Mỗi reader cần metadata tối thiểu:

```yaml
reader:
  reader_id:
  role:
  specialty:
  years_experience:
  training_level:
  prior_ai_experience:
  site:
```

Không lưu thông tin cá nhân không cần thiết.

---

## 4. Thiết kế ưu tiên

Khi mục tiêu là so sánh cùng bác sĩ với/không có Hermes, ưu tiên thiết kế paired multireader multicase khi khả thi.

Ví dụ:

```text
Session A:
reader đọc case không có Hermes

washout

Session B:
reader đọc case có Hermes hỗ trợ
```

Hoặc counterbalanced:

```text
Nhóm reader/case 1: unaided → aided
Nhóm reader/case 2: aided → unaided
```

để giảm order effect.

---

## 5. Không dùng một thứ tự cố định cho mọi reader nếu tránh được

Nếu mọi người đều đọc:
```text
unaided trước
aided sau
```

thì improvement có thể bị ảnh hưởng bởi:
- nhớ case;
- learning;
- familiarity với giao diện.

Khuyến nghị:
- randomize case order;
- counterbalance session order;
- pre-specify washout;
- dùng case order riêng hoặc random seed được lưu.

---

## 6. Washout

Washout cần đủ để giảm nhớ case nhưng không có một khoảng thời gian duy nhất phù hợp cho mọi study.

Protocol phải ghi rõ:
- thời gian washout;
- lý do;
- cách giảm memory effect.

Không hard-code "4 tuần" chỉ vì một nghiên cứu trước dùng 4 tuần.

---

## 7. Training/familiarization

Trước study chính:
- reader được hướng dẫn giao diện;
- được giải thích Hermes là hỗ trợ quyết định;
- được giải thích giới hạn;
- được thực hành trên case không thuộc evaluation set.

Training cases:
- không được tính vào study;
- không được dùng làm evaluation cases chính.

---

## 8. Hai điều kiện so sánh

### UNAIDED

Reader nhận:
- ảnh;
- clinical context theo protocol;
- dữ liệu phụ trợ theo protocol;

nhưng không thấy Hermes output.

### HERMES_ASSISTED

Reader nhận cùng dữ liệu cơ sở cộng:
- Hermes assessment;
- evidence provenance;
- uncertainty/conflicts;
- draft report nếu mode đánh giá có dùng;
- safety/review priority khi được phép.

Không cho thấy reference standard.

---

## 9. Chọn đúng mode sử dụng Hermes

Protocol phải chỉ rõ Hermes được dùng ở mode nào.

Ví dụ:

```text
SECOND_READER
DRAFT_REPORT_ASSIST
CONCURRENT_DECISION_SUPPORT
```

Không trộn nhiều mode trong cùng phân tích nếu không pre-specify.

Với kiến trúc MedVision hiện tại, mode phù hợp nhất để scaffold trước là:

```text
DRAFT_REPORT_ASSIST
```

hoặc:

```text
CONCURRENT_DECISION_SUPPORT
```

vì Hermes tạo assessment/draft trước bác sĩ review.

---

## 10. Nhiệm vụ của reader

Task phải pre-specify.

Ví dụ:
- xác nhận/sửa findings;
- đánh giá disease states;
- viết impression;
- nhận diện urgent/high-priority issue;
- hoàn thành report;
- chấp nhận/sửa/bác bỏ/defer từng mục.

Không yêu cầu reader đưa disease probability nếu workflow thực tế không dùng probability.

---

## 11. Reference standard

Reader study vẫn cần chuẩn tham chiếu độc lập.

Có thể reuse Clinical Dataset Evaluation reference-standard contract.

Không dùng:
- Hermes output;
- assisted reader consensus sau khi thấy Hermes;

làm ground truth chính.

Nếu adjudication cần bác sĩ:
- reference readers nên độc lập với study readers khi khả thi;
- phải ghi rõ bất kỳ overlap nào.

---

## 12. Primary endpoint phải pre-specify

Không mặc định một endpoint cho mọi study.

Protocol phải chọn primary endpoint phù hợp mục tiêu.

Ví dụ:
- major clinical error rate;
- disease-state agreement;
- sensitivity/specificity cho finding xác định;
- report-quality score theo rubric;
- time-to-completion.

Không đổi primary endpoint sau khi xem kết quả.

---

## 13. Secondary endpoints

Có thể gồm:

```text
reading/reporting time
edit burden
accept/modify/reject/defer rates
high-priority acknowledgement rate
critical miss rate
incorrect-AI acceptance rate
correct-AI rejection rate
confidence change
workflow completion rate
```

Không coi acceptance rate cao là tốt tự động.

---

## 14. Automation-bias proxy

Một chỉ số quan trọng:

```text
incorrect suggestion acceptance rate
```

Có thể dùng như proxy thực nghiệm cho nguy cơ over-reliance/automation bias.

Nhưng không được chẩn đoán tâm lý reader chỉ từ metric này.

Cần tách:
- AI/Hermes sai + reader chấp nhận;
- AI/Hermes đúng + reader bác bỏ;
- AI/Hermes không chắc + reader over-upgrade.

---

## 15. Safety endpoints

Bắt buộc theo dõi riêng:

```text
critical semantic errors
missed high-priority finding
unsafe over-commitment
doctor-review bypass attempt
autonomous-action carryover
provenance misunderstanding
conflict suppression
```

Nếu assisted mode làm tăng critical safety error, không được che bởi average time improvement.

---

## 16. Time metrics

Đo ít nhất:
- case start;
- first decision nếu cần;
- report complete;
- total review duration.

Không dùng system clock thiếu đồng bộ giữa clients nếu có thể.

Có thể loại outlier do interruption theo rule pre-specified, không loại sau khi xem kết quả tùy ý.

---

## 17. Edit burden

Với draft-report assist, ghi:
- số finding accepted;
- modified;
- rejected;
- added;
- hypothesis changes;
- narrative changes.

Text edit distance chỉ là kỹ thuật phụ.

Không dùng edit distance như clinical correctness.

---

## 18. Reader confidence

Có thể thu confidence trước/sau hỗ trợ nếu protocol muốn.

Nhưng:
- confidence không phải accuracy;
- tăng confidence khi sai có thể là tín hiệu nguy cơ;
- không dùng confidence thay reference standard.

---

## 19. Blinding

Reader không được thấy:
- ground truth;
- adjudication result;
- performance của reader khác;
- future diagnostic outcome ngoài dữ liệu protocol cho phép.

Assisted condition chỉ thấy Hermes content được định nghĩa trước.

---

## 20. Case randomization

Case order:
- random hoặc counterbalanced;
- random seed được lưu;
- không sắp theo disease label khiến reader đoán prevalence.

Nếu enriched dataset:
- prevalence enrichment phải được báo rõ.

---

## 21. Reader and case correlation

Không phân tích mỗi interpretation như độc lập.

Cùng reader đọc nhiều case và cùng case được nhiều reader đọc tạo correlation.

Nếu dùng MRMC:
- statistical method phải account reader + case effects.

Không dùng t-test đơn giản trên hàng nghìn interpretation như độc lập.

---

## 22. Sample-size/power

Không hard-code reader count hoặc case count.

Power/sample-size phụ thuộc:
- primary endpoint;
- expected effect;
- case prevalence;
- between-reader variation;
- paired design;
- alpha/power assumptions.

Scaffold v1 chỉ định contract; actual protocol cần calculation trước study.

---

## 23. Suggested study event schema

```yaml
reader_event:
  study_id:
  session_id:
  reader_id:
  case_id:
  condition: UNAIDED|HERMES_ASSISTED
  case_order:
  started_at:
  completed_at:

  finding_decisions: []
  hypothesis_decisions: []
  report_text:
  high_priority_acknowledgements: []

  confidence:
  comments:

  hermes_snapshot_id:
  ui_version:
```

Không lưu chain-of-thought của reader.

---

## 24. Hermes snapshot

Assisted session phải bind chính xác tới:
- Hermes version;
- repo commit;
- skills hash;
- provider/model;
- output snapshot;
- interface version.

Không để Hermes output thay đổi giữa readers trong cùng experimental condition trừ khi protocol chủ ý đánh giá stochasticity.

Khuyến nghị offline reader study dùng precomputed/frozen Hermes outputs cho mỗi case để mọi reader nhận cùng assistance.

---

## 25. Precomputed assistance vs live generation

### Precomputed/frozen assistance
Ưu điểm:
- reproducible;
- cùng input cho mọi reader;
- tách human-factor effect khỏi provider variability.

Khuyến nghị cho Reader Study v1.

### Live provider generation
Chỉ nên dùng nếu mục tiêu study bao gồm variability/latency thực.

Nếu live:
- phải ghi model version;
- trial policy;
- output hash;
- latency;
- failures.

---

## 26. UI transparency

Assisted UI cần cho reader thấy tối thiểu:
- đây là AI/Hermes assistance;
- evidence provenance;
- uncertainty;
- conflicts;
- limitations có liên quan;
- trạng thái chưa final.

Không thiết kế UI khiến draft trông như kết luận bác sĩ đã ký.

---

## 27. Avoid anchoring by presentation

Presentation order có thể gây anchoring.

Nên pre-specify:
- Hermes impression hiển thị ở đâu;
- findings/evidence có expandable không;
- confidence/score có hiển thị không;
- high-priority item hiển thị thế nào.

Vì MedVision không dùng AI score như disease probability, UI không được làm score trông như disease risk.

---

## 28. Report finalization trong reader study

Reader có thể thực hiện simulated doctor-review/finalization action trong study UI.

Nhưng đó là:
```text
study outcome
```

không phải hồ sơ bệnh án thật.

Không kết nối với chăm sóc bệnh nhân trong v1.

---

## 29. Reader-study states

```text
READER_STUDY_SCAFFOLD_READY
READER_STUDY_PROTOCOL_INCOMPLETE
READER_STUDY_DATASET_MISSING
READER_STUDY_PROVIDER_BLOCKED
READER_STUDY_ETHICS_STATUS_UNRESOLVED
READER_STUDY_READERS_MISSING
READER_STUDY_READY
READER_STUDY_RUNNING
READER_STUDY_COMPLETE
READER_STUDY_FAILED
```

---

## 30. Ethics/privacy boundary

Harness không tự quyết định study có cần ethics/IRB approval, consent waiver hay privacy review hay không.

Trước actual reader study, cơ sở thực hiện phải ghi nhận:
- ethics/IRB determination nếu áp dụng;
- data-use authorization;
- de-identification/privacy handling;
- reader consent/participation process nếu áp dụng.

Nếu trạng thái này chưa được xác định:

```text
READER_STUDY_ETHICS_STATUS_UNRESOLVED
```

Không tự suy "exempt".

---

## 31. Reader-study report

Báo cáo cần có:
- system version;
- UI version;
- dataset;
- reference standard;
- readers;
- experience distribution;
- study design;
- randomization;
- washout;
- training;
- endpoint definitions;
- missing data;
- assisted/unaided results;
- safety errors;
- time;
- human-AI interaction;
- limitations.

---

## 32. Không kết luận patient benefit

Reader study có thể cho thấy:
- accuracy change;
- reporting quality change;
- time change;
- safety/error change.

Nhưng không đủ để khẳng định:
- giảm tử vong;
- cải thiện outcome bệnh nhân;
- an toàn triển khai rộng;
- effectiveness trong môi trường thực.

Những câu hỏi đó cần giai đoạn prospective/live sau.

---

## 33. Hard constraints

Human-AI Reader Study v1 MUST NOT:

1. thêm clinical rule mới;
2. thay `.hermes/skills`;
3. dùng golden cases làm reader dataset chính;
4. dùng study reader output làm ground truth chính;
5. cho reader thấy reference standard;
6. dùng AI output đã thay đổi giữa conditions mà không ghi nhận;
7. tự chọn result tốt nhất từ nhiều provider trials;
8. coi acceptance rate là benefit;
9. bỏ qua reader/case correlation;
10. gọi retrospective reader study là patient-outcome validation;
11. tự quyết ethics exemption;
12. dùng study finalization như real clinical finalization;
13. thêm autonomous treatment logic;
14. bỏ doctor-control boundary.
