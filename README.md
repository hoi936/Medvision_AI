# Medvision_AI

Ứng dụng Streamlit thử nghiệm mô hình DenseNet121 nhận diện 14 findings trên ảnh X-quang ngực.

## Chạy ứng dụng trên Windows

```powershell
cd ".\AI_model"
py -3.13 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Ứng dụng chỉ phục vụ nghiên cứu/demo. Kết quả AI, Grad-CAM và pseudo-bbox không thay thế chẩn đoán hoặc annotation của bác sĩ.
