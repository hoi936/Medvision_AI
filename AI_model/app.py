"""Simple Streamlit frontend for the MedVision chest X-ray model."""

import hashlib

import pandas as pd
import streamlit as st

from hermes_report import (
    HermesReportError,
    MISSING_LABS_MODE,
    WITH_LABS_MODE,
    WORKFLOW_MODES,
    generate_hermes_report,
    get_hermes_status,
)
from inference import (
    CACHE_IMAGE_MODE,
    EXTERNAL_IMAGE_MODE,
    INPUT_MODES,
    MedVisionError,
    RAW_DICOM_MODE,
    create_heatmap,
    create_overlay,
    draw_bboxes_on_image,
    extract_pseudo_bboxes_from_cam,
    generate_gradcam_for_class,
    get_device,
    load_configuration,
    load_model,
    predict_findings,
)


st.set_page_config(page_title="MedVision AI Demo", page_icon="🩻", layout="wide")

st.markdown(
    """
    <style>
        .block-container {max-width: 1200px; padding-top: 2rem;}
        [data-testid="stMetric"] {
            background: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 12px;
            padding: 14px 18px;
        }
        [data-testid="stFileUploaderDropzone"] {border-radius: 12px;}
        div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 12px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Đang tải mô hình DenseNet121...")
def get_cached_model():
    """Load the checkpoint once for the entire Streamlit process."""
    device = get_device()
    return load_model(device), device


def show_error(exc: Exception, prefix: str = "") -> None:
    message = str(exc) if isinstance(exc, MedVisionError) else f"{prefix}{exc}"
    st.error(message)


CLINICAL_FIELD_KEYS = (
    "clinical_demographics",
    "clinical_symptoms",
    "clinical_history",
    "clinical_laboratory",
)


def clear_clinical_context() -> None:
    """Clear case-specific text so it cannot leak into another image/case."""
    for key in CLINICAL_FIELD_KEYS:
        st.session_state[key] = ""
    st.session_state["clinical_source_confirmed"] = False
    st.session_state["privacy_confirmed"] = False
    st.session_state.hermes_report = None


def render_positive_finding_card(
    item,
    original_image,
    visualization,
    cam_threshold,
    min_area_ratio,
    debug_mode,
    expanded=False,
):
    """Render one isolated card for one positive finding and its own CAM."""
    with st.expander(
        f"{item['finding']} · Model score {item['score'] * 100:.2f}% · POSITIVE",
        expanded=expanded,
    ):
        name_col, score_col, threshold_col, result_col = st.columns([2, 1, 1, 1])
        name_col.markdown(f"**Finding**  \n{item['finding']}")
        score_col.metric("Model score", f"{item['score'] * 100:.2f}%")
        threshold_col.metric("Threshold", f"{item['threshold'] * 100:.2f}%")
        result_col.markdown("**Kết luận**  \n:red[**POSITIVE**]")

        original_col, heatmap_col, overlay_col, bbox_col = st.columns(4)
        original_col.image(
            original_image,
            caption="Original X-ray",
            clamp=True,
            use_container_width=True,
        )
        heatmap_col.image(
            visualization["heatmap"],
            caption="Grad-CAM heatmap",
            use_container_width=True,
        )
        overlay_col.image(
            visualization["overlay"],
            caption="Overlay",
            use_container_width=True,
        )
        bbox_col.image(
            visualization["boxed_image"],
            caption="Pseudo bbox from Grad-CAM",
            use_container_width=True,
        )

        pseudo_boxes = visualization["pseudo_boxes"]
        if not pseudo_boxes:
            st.warning("No pseudo bbox found với ngưỡng hiện tại.")
        st.caption("Grad-CAM là vùng model chú ý, không phải segmentation mask.")
        st.caption(
            "Pseudo bbox được tạo từ vùng attention của Grad-CAM, không phải "
            "bounding box chuẩn của bác sĩ. Bbox này chỉ mang tính minh họa."
        )

        if debug_mode:
            st.markdown("##### Debug mode")
            debug_a, debug_b, debug_c = st.columns(3)
            debug_a.code(
                f"class_id: {item['class_id']}\n"
                f"raw score: {item['score']:.8f}\n"
                f"threshold: {item['threshold']:.8f}"
            )
            debug_b.code(
                f"pseudo boxes: {len(pseudo_boxes)}\n"
                f"cam threshold: {cam_threshold:.2f}\n"
                f"min area ratio: {min_area_ratio:.3f}"
            )
            if pseudo_boxes:
                debug_c.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "bbox": (
                                    f"({box['x1']}, {box['y1']}) - "
                                    f"({box['x2']}, {box['y2']})"
                                ),
                                "area_px": box["area"],
                                "area_%": round(float(box["area_ratio"]) * 100, 3),
                            }
                            for box in pseudo_boxes
                        ]
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                debug_c.code("box areas: []")


st.title("🩻 MedVision AI - Chest X-ray Demo")
st.write("Giao diện thử nghiệm mô hình DenseNet121 nhận diện 14 chest X-ray findings.")

try:
    load_configuration()
    model, device = get_cached_model()
except Exception as exc:
    show_error(exc, "Lỗi khởi tạo: ")
    st.stop()

with st.sidebar:
    st.header("Hướng dẫn")
    st.markdown(
        """
        1. Chọn một ảnh X-quang.
        2. Nhấn **Phân tích ảnh**.
        3. Xem findings và model score.
        4. Chọn finding POSITIVE để tạo Grad-CAM.
        """
    )
    st.divider()
    st.subheader("Trạng thái hệ thống")
    st.success("Model đã sẵn sàng")
    st.caption(f"Thiết bị: **{device.type.upper()}**")
    st.caption("Input: PNG · JPG · JPEG · DCM · DICOM")
    st.caption("Kích thước model input: 384 × 384")
    st.divider()
    debug_enabled = st.checkbox(
        "Debug mode",
        help=(
            "Hiển thị model input, raw scores và thông tin pseudo bbox "
            "của từng finding."
        ),
    )

st.warning(
    "**Ứng dụng chỉ phục vụ nghiên cứu / demo.**  \n"
    "Không sử dụng kết quả để thay thế chẩn đoán của bác sĩ."
)

with st.container(border=True):
    st.subheader("1. Tải ảnh X-quang")
    input_mode = st.selectbox(
        "Input type",
        options=INPUT_MODES,
        index=0,
        help="Chọn đúng nguồn ảnh để tránh áp dụng preprocessing hai lần.",
    )
    if input_mode == CACHE_IMAGE_MODE:
        st.info(
            "Ảnh đã export từ VinBigData cache: chỉ đọc grayscale và resize nếu cần; "
            "không percentile-normalize lần nữa."
        )
        accepted_types = ["png", "jpg", "jpeg"]
    elif input_mode == RAW_DICOM_MODE:
        st.info(
            "DICOM gốc: xử lý MONOCHROME1 và percentile normalization p0,5/p99,5 "
            "đúng một lần."
        )
        accepted_types = ["dcm", "dicom"]
    else:
        st.warning(
            "Ảnh PNG/JPG bên ngoài sẽ được percentile-normalize một lần. "
            "Ảnh ngoài pipeline gốc có thể khác domain và cho kết quả kém tin cậy hơn."
        )
        accepted_types = ["png", "jpg", "jpeg"]
    uploaded_file = st.file_uploader(
        "Kéo thả file vào đây hoặc nhấn Browse files",
        type=accepted_types,
        help="Định dạng file được giới hạn theo Input type đã chọn.",
        label_visibility="visible",
        key=f"upload_{input_mode}",
    )
    analyze_clicked = st.button(
        "🔍 Phân tích ảnh",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None,
    )

if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "finding_visuals" not in st.session_state:
    st.session_state.finding_visuals = {}
if "hermes_report" not in st.session_state:
    st.session_state.hermes_report = None
for clinical_key in CLINICAL_FIELD_KEYS:
    if clinical_key not in st.session_state:
        st.session_state[clinical_key] = ""

current_hash = None
if uploaded_file is not None:
    current_hash = hashlib.sha256(
        input_mode.encode("utf-8") + uploaded_file.getvalue()
    ).hexdigest()

if analyze_clicked and uploaded_file is not None:
    try:
        with st.spinner("Đang tiền xử lý ảnh và chạy model..."):
            gray, results, debug_info, input_tensor = predict_findings(
                uploaded_file.getvalue(),
                uploaded_file.name,
                input_mode=input_mode,
                model=model,
                device=device,
            )
        previous_analysis = st.session_state.analysis
        if (
            previous_analysis is not None
            and previous_analysis.get("file_hash") != current_hash
        ):
            clear_clinical_context()
        st.session_state.analysis = {
            "file_hash": current_hash,
            "filename": uploaded_file.name,
            "input_mode": input_mode,
            "gray": gray,
            "results": results,
            "debug_info": debug_info,
            "input_tensor": input_tensor,
        }
        st.session_state.finding_visuals = {}
        st.session_state.hermes_report = None
        st.toast("Phân tích hoàn tất", icon="✅")
    except Exception as exc:
        st.session_state.analysis = None
        st.session_state.finding_visuals = {}
        st.session_state.hermes_report = None
        show_error(exc, "Lỗi xử lý: ")

analysis = st.session_state.analysis
if analysis is not None and analysis["file_hash"] == current_hash:
    gray = analysis["gray"]
    results = analysis["results"]
    debug_info = analysis["debug_info"]
    input_tensor = analysis["input_tensor"]
    positive_results = [item for item in results if item["positive"]]

    if debug_info["scores_above_95_percent"] >= 7:
        st.warning(
            f"Có {debug_info['scores_above_95_percent']}/14 score lớn hơn 95%. "
            "Không tự coi đây là kết quả đúng; hãy kiểm tra Input type, preprocessing, "
            "threshold và phần Debug model input."
        )

    st.subheader("2. Tổng quan kết quả")
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Findings POSITIVE", f"{len(positive_results)} / 14")
    metric_b.metric("Model score cao nhất", f"{results[0]['score'] * 100:.2f}%")
    metric_c.metric("Ảnh đầu vào", analysis["filename"])

    image_column, result_column = st.columns([1, 1.35], gap="large")
    with image_column:
        with st.container(border=True):
            st.markdown("#### Ảnh đã preprocess")
            st.image(gray, clamp=True, use_container_width=True)
            st.caption(
                f"Input size: {debug_info['image_shape'][1]} × "
                f"{debug_info['image_shape'][0]} · dtype: {debug_info['image_dtype']} · "
                f"min/max: {debug_info['image_min']}/{debug_info['image_max']}"
            )

    with result_column:
        with st.container(border=True):
            st.markdown("#### Findings vượt threshold")
            if positive_results:
                st.error(f"Có {len(positive_results)} finding POSITIVE.")
                for item in positive_results:
                    st.markdown(f"**{item['finding']}** — :red[POSITIVE]")
                    score_col, threshold_col = st.columns(2)
                    score_col.write(f"Model score: `{item['score'] * 100:.2f}%`")
                    threshold_col.write(f"Threshold: `{item['threshold'] * 100:.2f}%`")
                    st.progress(float(item["score"]))
            else:
                st.success("Không có finding nào vượt threshold hiện tại.")

    st.subheader("3. Bảng toàn bộ 14 findings")
    table = pd.DataFrame(
        {
            "Finding": [item["finding"] for item in results],
            "Model score (%)": [round(item["score"] * 100, 2) for item in results],
            "Threshold (%)": [round(item["threshold"] * 100, 2) for item in results],
            "Result": ["POSITIVE" if item["positive"] else "NEGATIVE" for item in results],
        }
    )
    st.dataframe(
        table.style.map(
            lambda value: "color: #d32f2f; font-weight: 700"
            if value == "POSITIVE"
            else "",
            subset=["Result"],
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "⬇️ Tải kết quả CSV",
        data=table.to_csv(index=False).encode("utf-8-sig"),
        file_name="medvision_result.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption(
        "Model score là đầu ra sigmoid của mô hình và chưa phải xác suất "
        "lâm sàng đã được calibration."
    )

    if debug_enabled:
        with st.expander("Debug model input", expanded=True):
            debug_left, debug_right = st.columns(2)
            debug_left.code(
                "\n".join(
                    [
                        f"filename: {debug_info['filename']}",
                        f"input mode: {debug_info['input_mode']}",
                        f"image shape: {debug_info['image_shape']}",
                        f"image dtype: {debug_info['image_dtype']}",
                        f"image min: {debug_info['image_min']}",
                        f"image max: {debug_info['image_max']}",
                    ]
                )
            )
            debug_right.code(
                "\n".join(
                    [
                        f"tensor shape: {debug_info['tensor_shape']}",
                        f"tensor min: {debug_info['tensor_min']:.6f}",
                        f"tensor max: {debug_info['tensor_max']:.6f}",
                        f"model device: {debug_info['model_device']}",
                        f"logits shape: {debug_info['logits_shape']}",
                    ]
                )
            )
            debug_table = pd.DataFrame(
                {
                    "Finding": list(debug_info["raw_scores"].keys()),
                    "Raw sigmoid score": list(debug_info["raw_scores"].values()),
                    "Threshold": [
                        debug_info["thresholds"][name]
                        for name in debug_info["raw_scores"]
                    ],
                }
            )
            st.dataframe(debug_table, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("4. Chi tiết từng finding POSITIVE")
    st.caption(
        "Mỗi finding sử dụng một Grad-CAM class-specific riêng; các heatmap không "
        "được cộng, trung bình hoặc chồng với finding khác."
    )

    if not positive_results:
        st.info("Không có finding POSITIVE nên không tạo Grad-CAM hoặc pseudo bbox.")
    else:
        control_a, control_b = st.columns(2)
        cam_threshold = control_a.slider(
            "CAM threshold",
            min_value=0.10,
            max_value=0.90,
            value=0.50,
            step=0.05,
            help="Pixel Grad-CAM lớn hơn hoặc bằng ngưỡng được giữ lại.",
        )
        min_area_ratio = control_b.slider(
            "Min component area ratio",
            min_value=0.001,
            max_value=0.100,
            value=0.010,
            step=0.001,
            format="%.3f",
            help="Loại connected component nhỏ hơn tỷ lệ diện tích này.",
        )
        st.warning(
            "**Pseudo bbox from Grad-CAM** chỉ là vùng attention minh họa. "
            "Ứng dụng web này không hiển thị Doctor bbox và không có annotation "
            "ground-truth của radiologist."
        )

        for index, item in enumerate(positive_results):
            visual_key = (
                current_hash,
                int(item["class_id"]),
                round(float(cam_threshold), 4),
                round(float(min_area_ratio), 4),
            )
            visualization = st.session_state.finding_visuals.get(visual_key)
            if visualization is None:
                try:
                    with st.spinner(
                        f"Đang tạo Grad-CAM riêng cho {item['finding']}..."
                    ):
                        cam = generate_gradcam_for_class(
                            model, input_tensor, item["class_id"]
                        )
                        pseudo_boxes = extract_pseudo_bboxes_from_cam(
                            cam,
                            cam_threshold=cam_threshold,
                            min_area_ratio=min_area_ratio,
                        )
                        visualization = {
                            "class_id": item["class_id"],
                            "cam": cam,
                            "heatmap": create_heatmap(cam),
                            "overlay": create_overlay(gray, cam),
                            "pseudo_boxes": pseudo_boxes,
                            "boxed_image": draw_bboxes_on_image(gray, pseudo_boxes),
                        }
                    st.session_state.finding_visuals[visual_key] = visualization
                except Exception as exc:
                    show_error(exc, f"Lỗi Grad-CAM cho {item['finding']}: ")
                    continue

            if visualization["class_id"] != item["class_id"]:
                st.error(f"Phát hiện cache Grad-CAM sai class cho {item['finding']}.")
                continue
            render_positive_finding_card(
                item=item,
                original_image=gray,
                visualization=visualization,
                cam_threshold=cam_threshold,
                min_area_ratio=min_area_ratio,
                debug_mode=debug_enabled,
                expanded=index == 0,
            )

    st.divider()
    st.subheader("5. Hermes Agent — tạo báo cáo hỗ trợ")
    st.warning(
        "Hermes chỉ tạo **báo cáo nháp hỗ trợ bác sĩ**, không đưa ra chẩn đoán "
        "cuối cùng. Không nhập họ tên, địa chỉ, số điện thoại, mã bệnh án hoặc "
        "thông tin có thể nhận diện người bệnh."
    )

    hermes_status = get_hermes_status()
    if hermes_status.installed:
        st.info(hermes_status.message)
    else:
        st.error(hermes_status.message)

    with st.container(border=True):
        instruction_col, clear_col = st.columns([4, 1])
        instruction_col.info(
            "Chỉ nhập dữ liệu thực tế do người bệnh cung cấp hoặc nhân viên y tế "
            "đo/ghi nhận. Không dán câu hỏi, đề xuất hoặc nội dung do AI tạo vào "
            "các ô này. Ảnh X-quang không tự cho biết triệu chứng."
        )
        clear_col.button(
            "🗑️ Xóa dữ liệu ca",
            on_click=clear_clinical_context,
            use_container_width=True,
            help="Xóa toàn bộ dữ liệu lâm sàng đang lưu trong phiên này.",
        )
        workflow_mode = st.radio(
            "Chế độ tổng hợp",
            options=WORKFLOW_MODES,
            horizontal=True,
            help=(
                "Khi thiếu xét nghiệm, Hermes chỉ tạo đánh giá ban đầu và nêu "
                "dữ liệu cần bổ sung để bác sĩ xem xét."
            ),
        )
        context_left, context_right = st.columns(2)
        with context_left:
            demographics = st.text_input(
                "Thông tin chung không định danh",
                placeholder="Ví dụ: nam, nhóm tuổi 50–59",
                max_chars=500,
                key="clinical_demographics",
            )
            symptoms = st.text_area(
                "Triệu chứng thực tế và thời gian xuất hiện (bắt buộc)",
                placeholder="Ví dụ: ho khan 5 ngày, sốt, khó thở khi gắng sức...",
                max_chars=4000,
                height=120,
                key="clinical_symptoms",
            )
            if not symptoms.strip():
                st.warning(
                    "Cần nhập triệu chứng thực tế. Nếu người bệnh không có triệu "
                    "chứng, hãy ghi rõ “Không ghi nhận triệu chứng”."
                )
        with context_right:
            history = st.text_area(
                "Tiền sử và yếu tố nguy cơ liên quan",
                placeholder="Ví dụ: tiền sử hút thuốc, bệnh tim phổi...",
                max_chars=4000,
                height=120,
                key="clinical_history",
            )
            laboratory = st.text_area(
                "Xét nghiệm / dấu hiệu sinh tồn liên quan",
                placeholder="Ví dụ: SpO2, CRP, bạch cầu... kèm đơn vị nếu có",
                max_chars=4000,
                height=120,
                key="clinical_laboratory",
            )
            if workflow_mode == WITH_LABS_MODE and not laboratory.strip():
                st.warning(
                    "Đang chọn chế độ đã có xét nghiệm nhưng chưa nhập kết quả. "
                    "Hermes sẽ phải đánh dấu dữ liệu không đầy đủ."
                )
            elif workflow_mode == MISSING_LABS_MODE:
                st.caption(
                    "Có thể để trống. Hermes sẽ đề xuất dữ liệu cần bổ sung để "
                    "bác sĩ cân nhắc."
                )

        with st.expander("Cấu hình model Hermes (tùy chọn)"):
            st.caption(
                "Để trống để dùng model/provider mặc định đã cấu hình bằng "
                "Hermes CLI. API key không được nhập hoặc lưu tại màn hình này."
            )
            config_left, config_right = st.columns(2)
            hermes_model = config_left.text_input(
                "Model override",
                placeholder="Để trống = model mặc định",
            )
            hermes_provider = config_right.text_input(
                "Provider override",
                placeholder="Để trống = provider mặc định",
            )

        clinical_source_confirmed = st.checkbox(
            "Tôi xác nhận các nội dung trên là dữ liệu thực tế của ca đang xem, "
            "không phải câu hỏi hoặc đề xuất do AI tạo.",
            key="clinical_source_confirmed",
        )
        privacy_confirmed = st.checkbox(
            "Tôi xác nhận dữ liệu nhập không chứa thông tin định danh người bệnh "
            "và hiểu rằng findings cùng nội dung này sẽ được gửi đến provider LLM "
            "đã cấu hình; báo cáo phải được bác sĩ duyệt.",
            key="privacy_confirmed",
        )
        generate_clicked = st.button(
            "🤖 Tạo báo cáo nháp với Hermes",
            type="primary",
            use_container_width=True,
            disabled=not (
                symptoms.strip()
                and clinical_source_confirmed
                and privacy_confirmed
                and hermes_status.installed
            ),
        )

    report_input_hash = hashlib.sha256(
        "\x1f".join(
            [
                current_hash or "",
                workflow_mode,
                demographics,
                symptoms,
                history,
                laboratory,
            ]
        ).encode("utf-8")
    ).hexdigest()

    if generate_clicked:
        try:
            with st.spinner("Hermes đang tổng hợp bằng chứng và soạn báo cáo nháp..."):
                report = generate_hermes_report(
                    results=results,
                    symptoms=symptoms,
                    history=history,
                    laboratory=laboratory,
                    demographics=demographics,
                    workflow_mode=workflow_mode,
                    model=hermes_model,
                    provider=hermes_provider,
                )
            st.session_state.hermes_report = {
                "file_hash": current_hash,
                "content": report,
                "workflow_mode": workflow_mode,
                "review_status": "PENDING",
                "input_hash": report_input_hash,
                "input_snapshot": {
                    "workflow_mode": workflow_mode,
                    "demographics": demographics or "Không được cung cấp",
                    "symptoms": symptoms,
                    "history": history or "Không được cung cấp",
                    "laboratory": laboratory or "Không được cung cấp",
                    "positive_findings": [
                        {
                            "finding": item["finding"],
                            "model_score": round(float(item["score"]), 4),
                            "threshold": round(float(item["threshold"]), 4),
                        }
                        for item in positive_results
                    ],
                },
            }
            st.session_state[f"doctor_report_editor_{current_hash}"] = report
            st.toast("Đã tạo báo cáo nháp", icon="✅")
        except HermesReportError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Lỗi không mong đợi khi gọi Hermes: {exc}")

    saved_report = st.session_state.hermes_report
    if saved_report and saved_report.get("file_hash") == current_hash:
        report_is_stale = saved_report.get("input_hash") != report_input_hash
        if report_is_stale:
            st.warning(
                "Dữ liệu lâm sàng đã thay đổi sau khi tạo báo cáo. Hãy nhấn "
                "**Tạo báo cáo nháp với Hermes** lại trước khi duyệt."
            )
        with st.expander("Dữ liệu đầu vào đã dùng để tạo báo cáo"):
            st.json(saved_report.get("input_snapshot", {}))
        st.markdown("#### Bản nháp do Hermes tạo")
        st.markdown(saved_report["content"])
        st.error(
            "Báo cáo do AI hỗ trợ soạn thảo, không phải chẩn đoán và chỉ có "
            "giá trị sau khi bác sĩ duyệt."
        )
        st.markdown("#### Cổng bác sĩ duyệt (bản demo)")
        st.caption(
            "Có thể sửa nội dung trước khi đánh dấu duyệt. Bản demo chưa có "
            "xác thực bác sĩ, chữ ký số, lưu database hoặc audit log."
        )
        editor_key = f"doctor_report_editor_{current_hash}"
        if editor_key not in st.session_state:
            st.session_state[editor_key] = saved_report["content"]
        edited_report = st.text_area(
            "Nội dung sau chỉnh sửa",
            height=420,
            key=editor_key,
        )
        reviewer_confirmed = st.checkbox(
            "Tôi xác nhận đây chỉ là thao tác mô phỏng duyệt của bác sĩ và đã "
            "tự kiểm tra lại ảnh, dữ liệu lâm sàng cùng nội dung báo cáo.",
            key=f"review_confirm_{current_hash}",
        )
        approve_col, reject_col = st.columns(2)
        approve_clicked = approve_col.button(
            "✅ Đánh dấu đã duyệt (demo)",
            use_container_width=True,
            disabled=not reviewer_confirmed or report_is_stale,
        )
        reject_clicked = reject_col.button(
            "❌ Từ chối bản nháp",
            use_container_width=True,
        )
        if approve_clicked:
            saved_report["review_status"] = "APPROVED_DEMO"
            saved_report["final_content"] = edited_report
        if reject_clicked:
            saved_report["review_status"] = "REJECTED"
            saved_report.pop("final_content", None)

        review_status = saved_report.get("review_status", "PENDING")
        if review_status == "APPROVED_DEMO":
            st.success("Trạng thái: ĐÃ ĐÁNH DẤU DUYỆT TRONG BẢN DEMO")
            download_content = saved_report.get("final_content", edited_report)
            download_name = "medvision_report_reviewed_demo.md"
            download_label = "⬇️ Tải báo cáo đã chỉnh sửa (demo)"
        elif review_status == "REJECTED":
            st.error("Trạng thái: BẢN NHÁP ĐÃ BỊ TỪ CHỐI")
            download_content = saved_report["content"]
            download_name = "medvision_hermes_report_rejected_draft.md"
            download_label = "⬇️ Tải bản nháp bị từ chối"
        else:
            st.info("Trạng thái: ĐANG CHỜ BÁC SĨ DUYỆT")
            download_content = saved_report["content"]
            download_name = "medvision_hermes_report_draft.md"
            download_label = "⬇️ Tải báo cáo nháp Markdown"

        st.download_button(
            download_label,
            data=download_content.encode("utf-8"),
            file_name=download_name,
            mime="text/markdown",
            use_container_width=True,
        )

elif uploaded_file is not None:
    st.info("Ảnh đã sẵn sàng. Nhấn **Phân tích ảnh** để xem kết quả.")
else:
    st.info("Hãy tải một ảnh X-quang để bắt đầu.")
