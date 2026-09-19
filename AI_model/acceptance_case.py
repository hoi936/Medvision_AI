"""Canonical regression case specified by yeucau.md."""

from clinical_schema import build_case_payload


FINDINGS = [
    ("Calcification", 0.9997, 0.9072),
    ("Pleural effusion", 0.9792, 0.9136),
    ("Nodule/Mass", 0.9172, 0.9043),
    ("Pleural thickening", 0.8682, 0.8369),
    ("Pulmonary fibrosis", 0.8576, 0.8940),
    ("Other lesion", 0.7630, 0.9492),
    ("Lung Opacity", 0.3563, 0.9326),
    ("ILD", 0.2909, 0.8730),
    ("Aortic enlargement", 0.2263, 0.8477),
    ("Atelectasis", 0.1747, 0.9512),
    ("Cardiomegaly", 0.0684, 0.8257),
    ("Consolidation", 0.0538, 0.9663),
    ("Infiltration", 0.0113, 0.9551),
    ("Pneumothorax", 0.0008, 0.9771),
]


def build_acceptance_case():
    results = [
        {"finding": name, "score": score, "threshold": threshold, "positive": score >= threshold}
        for name, score, threshold in FINDINGS
    ]
    return build_case_payload(
        workflow_mode="MISSING_LABS",
        general_info={"sex": "Female", "age": 67},
        symptoms=[
            {"name": "Progressive exertional dyspnea", "duration": "2 months", "severity": "worse last 2 weeks"},
            {"name": "Dry cough", "duration": "6 weeks"},
            {"name": "Mild left chest heaviness/discomfort"},
            {"name": "Reduced exercise tolerance"},
            {"name": "No high fever"},
            {"name": "No hemoptysis"},
        ],
        history=[
            "Previous pneumonia approximately 8 years ago",
            "Recurrent respiratory infections",
            "Mild hypertension",
            "No known heart failure",
        ],
        risk_factors=[
            "Passive smoking exposure",
            "Long-term occupational dust exposure",
            "Tuberculosis history unknown",
        ],
        vitals={
            "spo2": {"value": 93, "unit": "%", "context": "room air"},
            "respiratory_rate": {"value": 22, "unit": "/min"},
            "heart_rate": {"value": 88, "unit": "/min"},
            "blood_pressure": {"systolic": 138, "diastolic": 82, "unit": "mmHg"},
            "temperature": {"value": 36.8, "unit": "C"},
        },
        laboratory_results=[
            {"name": "WBC", "value": 8.9, "unit": "10^9/L", "reference_range": None, "timestamp": None},
            {"name": "Neutrophils", "value": 64, "unit": "%", "reference_range": None, "timestamp": None},
            {"name": "Hemoglobin", "value": 12.4, "unit": "g/dL", "reference_range": None, "timestamp": None},
            {"name": "Platelets", "value": 268, "unit": "10^9/L", "reference_range": None, "timestamp": None},
            {"name": "CRP", "value": 7.2, "unit": "mg/L", "reference_range": None, "timestamp": None},
            {"name": "ESR", "value": 28, "unit": "mm/h", "reference_range": None, "timestamp": None},
            {"name": "Creatinine", "value": 0.81, "unit": "mg/dL", "reference_range": None, "timestamp": None},
            {"name": "BNP", "value": 74, "unit": "pg/mL", "reference_range": None, "timestamp": None},
        ],
        missing_tests=["Chest CT"],
        clinician_request="Generate evidence-based differential considerations and a draft report.",
        model_results=results,
    )
