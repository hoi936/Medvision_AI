Hãy sửa ứng dụng web test model X-quang ngực của tôi theo các yêu cầu dưới đây.

1. Mục tiêu

Ứng dụng hiện tại đang hiển thị Grad-CAM chưa đúng khi một ảnh có nhiều finding POSITIVE. Nhiều vùng attention đang bị gộp/chồng trong cùng một phần hiển thị, làm khó đọc. Tôi muốn sửa lại để:

Tách riêng từng finding dương tính
Với mỗi finding POSITIVE, hiển thị riêng:
Ảnh gốc
Ảnh Grad-CAM heatmap
Ảnh overlay (heatmap chồng lên ảnh gốc)
Ảnh gốc có ô vuông pseudo-bbox được suy ra từ Grad-CAM
2. Yêu cầu hiển thị mới

Khi người dùng upload ảnh và bấm phân tích:

A. Bảng tổng quan giữ nguyên

Vẫn hiển thị:

số finding POSITIVE
score cao nhất
tên file input
bảng 14 findings với:
finding
model score
threshold
kết quả POSITIVE / NEGATIVE
B. Thêm một khu vực mới: “Chi tiết từng finding POSITIVE”

Khu vực này phải hiển thị danh sách riêng cho từng finding POSITIVE.

Ví dụ:

Atelectasis
Pleural effusion
Pulmonary fibrosis

Mỗi finding là một expander/card riêng, không được gộp heatmap giữa các finding.

Trong mỗi finding card, hiển thị:

Tên finding
Score (%)
Threshold (%)
Kết luận POSITIVE / NEGATIVE
4 ảnh đặt theo grid 2x2 hoặc 4 cột:
Original X-ray
Grad-CAM heatmap
Overlay
Original + pseudo bbox
3. Pseudo-bbox từ Grad-CAM

Tôi muốn ngoài heatmap đỏ, có thêm một ảnh giống kiểu bác sĩ đánh dấu ô vuông.

Lưu ý rất quan trọng:

Đây không phải bbox ground-truth của bác sĩ
Đây chỉ là pseudo bounding box sinh ra từ Grad-CAM
Phải ghi chú rõ trong UI:
“Pseudo bbox được tạo từ vùng attention của Grad-CAM, không phải bounding box chuẩn của bác sĩ.”
4. Cách tạo pseudo-bbox

Hãy dùng quy trình sau cho từng finding riêng biệt:

Sinh Grad-CAM map cho đúng class/finding được chọn.
Chuẩn hóa map về [0, 1].
Threshold map, ví dụ mặc định:
cam_threshold = 0.5
Tạo binary mask:
vùng nào cam >= threshold thì giữ lại
Tìm connected components / contours
Loại bỏ component quá nhỏ bằng min_area_ratio
ví dụ 0.01 hoặc 1% diện tích ảnh
Với mỗi component hợp lệ:
tạo bounding rectangle (x1, y1, x2, y2)
Vẽ bbox màu xanh lá lên ảnh gốc
Nếu không có component đủ lớn:
fallback sang vùng peak-centered bbox hoặc hiển thị “No pseudo bbox found”
5. Không được gộp Grad-CAM nhiều finding

Bug hiện tại là vùng hiển thị đang có cảm giác bị chồng/gộp. Hãy đảm bảo:

Mỗi finding gọi Grad-CAM riêng theo class_id
Không reuse nhầm heatmap của finding khác
Không cộng / trung bình / overlay nhiều class chung một ảnh
Mỗi item trong danh sách phải giữ state riêng
6. UI/UX mong muốn

Hãy sửa giao diện theo hướng dễ đọc:

Phần danh sách finding dương tính:

Mỗi finding card gồm:

Header

Finding name
Model score
Threshold
POSITIVE badge

Body

4 ảnh:
Original
Grad-CAM
Overlay
Original + pseudo bbox

Footer note

“Grad-CAM là vùng model chú ý, không phải segmentation mask.”
“Pseudo bbox được sinh từ Grad-CAM, chỉ mang tính minh họa.”
7. Nếu có nhiều finding POSITIVE

Ví dụ ảnh có 7 finding POSITIVE, thì phải hiển thị:

7 card riêng
mỗi card có bộ ảnh riêng
không đè hình lên nhau

Có thể thêm:

expander mặc định đóng
hoặc selectbox để chọn finding
nhưng tôi ưu tiên danh sách riêng từng finding
8. Nếu finding NEGATIVE

Không cần hiển thị block Grad-CAM chi tiết cho NEGATIVE, trừ khi tôi bật chế độ debug.

9. Cần hỗ trợ debug

Thêm một checkbox hoặc expander “Debug mode” để hiển thị:

class_id
raw score
threshold
số lượng pseudo boxes
diện tích từng pseudo box
cam threshold đang dùng
min area ratio
10. Yêu cầu code

Hãy refactor code cho rõ ràng, tách hàm như sau:

predict_findings(...)
generate_gradcam_for_class(...)
create_overlay(...)
extract_pseudo_bboxes_from_cam(...)
draw_bboxes_on_image(...)
render_positive_finding_card(...)
11. Gợi ý kỹ thuật

Nếu app đang dùng Streamlit, hãy triển khai theo kiểu:

Sau khi predict xong:
lấy danh sách positive findings
Loop qua từng finding positive:
generate gradcam riêng
generate overlay riêng
generate pseudo bbox riêng
render ra 1 expander/card riêng

Pseudo code mong muốn:

positive_findings = [f for f in findings if f["is_positive"]]

for item in positive_findings:
    class_id = item["class_id"]
    finding_name = item["finding"]
    score = item["score"]
    threshold = item["threshold"]

    cam = generate_gradcam_for_class(model, input_tensor, class_id)
    overlay = create_overlay(original_image, cam)
    pseudo_boxes = extract_pseudo_bboxes_from_cam(cam, cam_threshold=0.5, min_area_ratio=0.01)
    boxed_image = draw_bboxes_on_image(original_image, pseudo_boxes)

    render_positive_finding_card(
        finding_name=finding_name,
        score=score,
        threshold=threshold,
        original_image=original_image,
        cam=cam,
        overlay=overlay,
        boxed_image=boxed_image,
        pseudo_boxes=pseudo_boxes,
    )
12. Yêu cầu đầu ra

Hãy:

Sửa trực tiếp code app
Ghi rõ những file đã sửa
Giải thích ngắn gọn bug cũ và cách đã fix
Đảm bảo app chạy được sau khi sửa
Nếu có thể, thêm label phân biệt:
“Doctor bbox” = chỉ dùng khi có ground truth trong notebook debug
“Pseudo bbox from Grad-CAM” = dùng trong web deploy
13. Điều cực kỳ quan trọng

Trong web deploy hiện tại không được làm người dùng hiểu nhầm rằng ô vuông đó là bác sĩ đánh dấu thật.
Phải ghi rõ:

đây là pseudo bbox từ Grad-CAM
chỉ mang tính hỗ trợ trực quan
không phải annotation chuẩn của radiologist