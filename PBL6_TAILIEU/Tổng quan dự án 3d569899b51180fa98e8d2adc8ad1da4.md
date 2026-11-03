# Tổng quan dự án

## Tổng quan dự án MedVision AI

**MedVision AI** là nền tảng hỗ trợ bác sĩ quản lý, phân tích hình ảnh X-quang và tổng hợp dữ liệu lâm sàng bằng AI.

### 1. Mục tiêu

```
Dữ liệu bệnh nhân
      ↓
🩻 X-quang + 📝 Triệu chứng + 🧪 Xét nghiệm
      ↓
AI phân tích hình ảnh
      ↓
HERMES
      ↓
Tổng hợp bằng chứng + kiến thức y khoa
      ↓
Đánh giá hỗ trợ
      ↓
👨‍⚕️ Bác sĩ xem / sửa / xác nhận
      ↓
📄 Báo cáo cuối
```

**AI chỉ hỗ trợ bác sĩ, không tự thay thế bác sĩ.**

---

### 2. Các thành phần chính

**🩻 AI Image Service**

- Phân tích X-quang ngực.
- Phát hiện các bất thường.
- Bounding Box / Grad-CAM để giải thích vùng AI chú ý.
- Hiện tại đang nghiên cứu với **VinBigData**.

**🧠 Hermes**

- Trung tâm điều phối toàn bộ quá trình.
- Nhận kết quả AI + triệu chứng + xét nghiệm.
- Medical RAG / Knowledge Base.
- Disease Skills.
- Evidence Fusion.
- Phát hiện bằng chứng mâu thuẫn.
- Phát hiện trường hợp AI có khả năng sai.
- Tạo đánh giá và báo cáo nháp.
- Đề xuất thông tin/xét nghiệm bổ sung khi dữ liệu thiếu.

**🌐 Web Platform**

- Quản lý bệnh nhân.
- Quản lý ca khám / Study.
- Upload và xem DICOM.
- Hiển thị kết quả AI trên X-quang.
- Bác sĩ review kết quả.
- Chỉnh sửa báo cáo.
- Lưu lịch sử.

---

### 3. Hai chế độ Hermes

**🟢 Đủ dữ liệu**

```
X-quang
+ Triệu chứng
+ Xét nghiệm
↓
Hermes
↓
Đánh giá
↓
Báo cáo nháp
↓
Bác sĩ duyệt
```

**🟡 Thiếu dữ liệu**

```
X-quang
+ Triệu chứng
↓
Hermes
↓
Đánh giá ban đầu
↓
Phát hiện dữ liệu thiếu
↓
Đề xuất bổ sung để bác sĩ xem xét
↓
Có kết quả mới
↓
Hermes đánh giá lại
↓
Báo cáo
↓
Bác sĩ duyệt
```

---

### 4. Bác sĩ luôn kiểm soát

Bác sĩ có thể:

**✅ Xác nhận — ✏️ Chỉnh sửa — ❌ Từ chối — ➕ Bổ sung**

Hệ thống lưu riêng:

```
AI Result
    ↓
Doctor Review
    ↓
Final Report
```

để sau này đánh giá **AI sai ở đâu, bác sĩ sửa gì** và xây dựng Human-in-the-Loop.

---

### 5. AI hiện tại

Đã hoàn thành **RSNA Pneumonia baseline**:

- DenseNet121
- ROC-AUC ≈ **0.874**
- Grad-CAM
- đánh giá classification + localization

Đang triển khai **VinBigData**:

- 15.000 ảnh DICOM
- 14 loại **bất thường X-quang** + No Finding
- 17 bác sĩ gán nhãn
- bounding boxes
- sử dụng majority vote ≥2/3 cho label nghiên cứu
- DenseNet121 baseline
- tiếp theo: **DenseNet121 + CBAM**
- sau đó đánh giá Grad-CAM/localization.

**Hiện tại cache VinBigData 384×384 đang được xây, đã đạt khoảng 12.000/14.958 ảnh.**

---

### 6. Roadmap

```
PHASE 1
RSNA
DenseNet121 + Grad-CAM
        ✅

PHASE 2
VinBigData
EDA
↓
DenseNet121
↓
DenseNet121 + CBAM
↓
So sánh
↓
Explainability / Localization
        🔄

PHASE 3
AI Inference Service

PHASE 4
Hermes
+ RAG
+ Disease Skills
+ Evidence Engine
+ Clinical Reasoning
        ↓

PHASE 5
MedVision Web Platform
+ DICOM Viewer
+ Doctor Review
+ Report
+ Patient History

PHASE 6
Dashboard
+ Feedback
+ Model Versioning
+ Human-in-the-Loop
```

### 🎯 Tóm gọn trong một câu

> **MedVision AI = AI phân tích X-quang + Hermes tổng hợp X-quang, triệu chứng và xét nghiệm + Web quản lý bệnh nhân/ca khám + bác sĩ luôn kiểm soát và quyết định kết quả cuối cùng.**
>