
MEDVISION AI - CHEST X-RAY DEMO
================================

Ứng dụng Streamlit chạy DenseNet121 baseline BEST (epoch 8) để đánh giá
14 chest X-ray findings. Ứng dụng không train lại hoặc thay đổi model.

Input
-----
- DICOM (.dcm, .dicom), grayscale một frame
- PNG, JPG, JPEG

Input type
----------
- Preprocessed PNG/JPG from VinBigData cache (mặc định): không percentile
  normalize lần nữa; chỉ grayscale và resize về 384x384 nếu cần.
- Raw DICOM: đảo MONOCHROME1 nếu cần, percentile normalize p0.5/p99.5,
  resize 384x384 và chuyển uint8.
- External PNG/JPG: percentile normalize đúng một lần. Dữ liệu ngoài có thể
  khác domain so với tập train.

Output
------
- 14 model sigmoid scores
- Threshold riêng của từng finding
- Kết quả POSITIVE / NEGATIVE
- Grad-CAM class-specific riêng cho từng finding POSITIVE
- Pseudo bbox suy ra từ connected components của từng Grad-CAM
- Tải bảng kết quả dưới dạng CSV
- Hermes Agent tổng hợp findings và bối cảnh lâm sàng thành báo cáo nháp
- Hermes xem ảnh gốc cùng Grad-CAM, overlay và pseudo bbox của từng finding
- Xuất báo cáo kèm ảnh ở Markdown (.md), PDF (.pdf) hoặc Word (.docx)

Thao tác
--------
1. Upload ảnh X-quang tại trang chính.
2. Nhấn "Phân tích ảnh".
3. Xem ảnh đã preprocess, findings POSITIVE và bảng đủ 14 findings.
4. Mở từng card trong "Chi tiết từng finding POSITIVE" để xem Original,
   Grad-CAM, Overlay và Pseudo bbox.
5. Điều chỉnh CAM threshold/min area ratio nếu cần.
6. Bật "Debug mode" ở sidebar để xem model input, class_id, raw score,
   threshold, số pseudo box và diện tích từng box.
7. Nhập bối cảnh lâm sàng không định danh, xác nhận điều khoản và chọn
   "Tạo báo cáo nháp với Hermes". Bác sĩ phải kiểm tra trước khi sử dụng.
8. Chọn Markdown, PDF hoặc Word tại mục "Xuất báo cáo kèm hình ảnh".

Các ô triệu chứng, tiền sử và xét nghiệm chỉ nhận dữ liệu thực tế do người bệnh
cung cấp hoặc nhân viên y tế ghi nhận. Không dán câu hỏi, đề xuất xét nghiệm hay
nội dung báo cáo do AI tạo vào các ô này. Triệu chứng thực tế là bắt buộc; nếu
không ghi nhận triệu chứng, nhập rõ "Không ghi nhận triệu chứng". Dùng nút
"Xóa dữ liệu ca" trước khi chuyển sang người bệnh/ảnh khác.

Cài đặt và chạy trên Windows
----------------------------
1. Mở PowerShell hoặc Command Prompt tại thư mục AI_model.
2. Khuyến nghị tạo môi trường ảo:

   py -3.13 -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1

3. Cài thư viện và chạy:

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m streamlit run app.py

Nếu máy không có GPU/CUDA tương thích, ứng dụng tự động sử dụng CPU.

Cấu hình Hermes Agent trên Windows
----------------------------------
Hermes được clone tại thư mục hermes-agent và cài trong môi trường riêng
.hermes-runtime ở thư mục gốc dự án. Tại PowerShell ở thư mục gốc, chạy:

   .\.hermes-runtime\Scripts\hermes.exe setup
   .\.hermes-runtime\Scripts\hermes.exe model
   .\.hermes-runtime\Scripts\hermes.exe doctor

Sau khi cấu hình provider/model/API key, chạy ứng dụng bằng môi trường của
AI_model (không dùng môi trường Hermes):

   cd AI_model
   .\.venv\Scripts\python.exe -m streamlit run app.py

Nếu ứng dụng đã chạy trong lúc source code Hermes được cập nhật, chỉ cần tải lại
trang. App sẽ phát hiện bridge cũ trong bộ nhớ và reload module. Nếu vẫn gặp lỗi
module cache, dừng tiến trình bằng Ctrl+C rồi chạy lại lệnh trên.

MedVision gọi Hermes CLI với toolset giới hạn (`clarify,skills`, hoặc
`clarify,vision,skills` khi có ảnh) và không lưu API key. Toolset `skills` của
Hermes v0.21.4 cung cấp `skills_list`, `skill_view`, `skill_manage`; không bật
terminal, browser, messaging hoặc công cụ sửa file tùy ý. Phiên bản này không
hỗ trợ tắt riêng `skill_manage`, vì vậy cấu hình runtime bắt buộc đặt
`skills.write_approval: true`; bridge sẽ từ chối chạy nếu gate này bị tắt. Mọi
yêu cầu sửa skill chỉ được staged và không được ghi cho đến khi có phê duyệt rõ
ràng. Không nhập
thông tin định danh người bệnh vào phần bối cảnh lâm sàng. Findings và nội dung
được nhập, ảnh X-quang đã preprocess, Grad-CAM, overlay và pseudo bbox sẽ được
gửi tới provider LLM đã cấu hình trong Hermes. Cần xem chính
sách lưu trữ/xử lý dữ liệu của provider trước khi dùng dữ liệu thật. Nếu muốn
thay model hoặc provider cho một lần tạo báo cáo, mở mục cấu hình Hermes trong
giao diện; không nhập API key tại đó.

Skill phân tích bệnh của Hermes
-------------------------------
Skill project-local nằm tại:

   .hermes\skills\medvision-disease-analysis\SKILL.md

Skill thực hiện kiểm tra chất lượng dữ liệu, ma trận bằng chứng, đối chiếu mâu
thuẫn, chẩn đoán phân biệt có giới hạn, phát hiện dữ liệu thiếu và bắt buộc cổng
bác sĩ duyệt. Skill không chẩn đoán xác định, kê đơn hoặc biến model score thành
xác suất bệnh.

Sau khi clone dự án trên một máy mới, chạy một lần tại thư mục gốc:

   .\.hermes-runtime\Scripts\hermes.exe skills trust .
   .\.hermes-runtime\Scripts\hermes.exe skills list --source local

Ứng dụng nạp tường minh skill `medvision-disease-analysis` cho mỗi lần tạo báo
cáo và chỉ bật toolset `clarify,skills` (thêm `vision` khi có ảnh); không cấp
terminal, file hoặc web tools
cho phiên xử lý ca bệnh. Ảnh tạm dùng cho Hermes được xóa ngay sau khi tiến
trình tạo báo cáo kết thúc.

Kiểm thử runtime thật là opt-in. Pytest chạy bằng môi trường dự án, còn mọi lệnh
Hermes vẫn chạy qua runtime đã pin ở `.runtime/hermes-venv`. Từ thư mục gốc dự
án, chạy launcher có preflight bắt buộc:

   PROJECT_TEST_PYTHON="$PWD/AI_model/.venv/bin/python" \
     bash AI_model/scripts/run_real_validation.sh

Không cài pytest vào Hermes runtime. Nếu không đặt RUN_HERMES_REAL, các golden
clinical cases được skip với lý do rõ ràng. Nếu preflight thất bại, launcher dừng
trước khi chạy clinical cases. Quy trình cấu hình và lệnh thủ công nằm trong
AI_model/PROVIDER_ACTIVATION_RUNBOOK.md.

Kiến trúc Hermes, schema chuẩn hóa, kết quả kiểm thử và báo cáo mẫu acceptance
case được mô tả trong HERMES_IMPLEMENTATION.md.

Các file bắt buộc phải nằm cạnh app.py
--------------------------------------
- model.pth
- class_names.json
- thresholds.json
- preprocessing.json

Lưu ý
-----
Model score là đầu ra sigmoid và chưa phải xác suất lâm sàng đã được
calibration. Ứng dụng chỉ phục vụ nghiên cứu/demo, không sử dụng kết quả
để thay thế chẩn đoán của bác sĩ.

Báo cáo Hermes là bản nháp hỗ trợ tổng hợp bằng chứng. Nội dung không phải chẩn
đoán xác định, không được dùng để tự điều trị hoặc kê đơn và chỉ có giá trị sau
khi bác sĩ có chuyên môn kiểm tra, chỉnh sửa và phê duyệt.

Pseudo bbox được tạo từ vùng attention của Grad-CAM và chỉ mang tính minh
họa. Đây không phải Doctor bbox, ground-truth hay annotation chuẩn của
radiologist.
