
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

Pseudo bbox được tạo từ vùng attention của Grad-CAM và chỉ mang tính minh
họa. Đây không phải Doctor bbox, ground-truth hay annotation chuẩn của
radiologist.
