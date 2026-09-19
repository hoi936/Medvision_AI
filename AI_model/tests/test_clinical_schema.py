"""Regression tests for the canonical Hermes clinical schema."""

from pathlib import Path
import sys
from unittest import TestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clinical_schema import (
    build_case_payload,
    calculate_confidence_band,
    legacy_case_payload,
    normalize_case_payload,
)


ACCEPTANCE_FINDINGS = [
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


def acceptance_results():
    return [
        {
            "finding": name,
            "score": score,
            "threshold": threshold,
            "positive": score >= threshold,
        }
        for name, score, threshold in ACCEPTANCE_FINDINGS
    ]


class ClinicalSchemaTests(TestCase):
    def test_confidence_bands_preserve_binary_decision(self):
        decision, band, margin = calculate_confidence_band(0.8576, 0.8940)
        self.assertEqual(decision, "NEGATIVE")
        self.assertEqual(band, "NEAR_THRESHOLD_NEGATIVE")
        self.assertAlmostEqual(margin, -0.0364)

        decision, band, _ = calculate_confidence_band(0.0008, 0.9771)
        self.assertEqual(decision, "NEGATIVE")
        self.assertEqual(band, "CLEAR_NEGATIVE")

    def test_legacy_field_presence_normalizes_to_provided(self):
        legacy = legacy_case_payload(
            results=acceptance_results(),
            symptoms="Progressive exertional dyspnea",
            history="Mild hypertension",
            laboratory="WBC 8.9 x10^9/L",
            demographics="Female, 67",
        )
        normalized = normalize_case_payload(legacy)

        self.assertTrue(normalized.payload["symptoms"]["provided"])
        self.assertFalse(normalized.payload["symptoms"]["verified"])
        self.assertTrue(any("field_presence.symptoms" in w for w in normalized.warnings))

    def test_full_acceptance_case_is_canonical_and_lossless(self):
        payload = build_case_payload(
            workflow_mode="MISSING_LABS",
            general_info={"sex": "Female", "age": 67},
            symptoms=[
                {"name": "Progressive exertional dyspnea", "duration": "2 months", "severity": "worse last 2 weeks"},
                {"name": "Dry cough", "duration": "6 weeks"},
                {"name": "Mild left chest discomfort"},
                {"name": "Reduced exercise tolerance"},
                {"name": "No high fever"},
                {"name": "No hemoptysis"},
            ],
            history=["Previous pneumonia 8 years ago", "Recurrent respiratory infections", "Mild hypertension", "No known heart failure"],
            risk_factors=["Passive smoking", "Long-term occupational dust exposure", "Tuberculosis history unknown"],
            vitals={
                "spo2": {"value": 93, "unit": "%", "context": "room air"},
                "respiratory_rate": {"value": 22, "unit": "/min"},
                "heart_rate": {"value": 88, "unit": "/min"},
                "blood_pressure": {"value": "138/82", "unit": "mmHg"},
                "temperature": {"value": 36.8, "unit": "C"},
            },
            laboratory_results=[
                {"name": "WBC", "value": 8.9, "unit": "10^9/L", "reference_range": None, "timestamp": None},
                {"name": "CRP", "value": 7.2, "unit": "mg/L", "reference_range": None, "timestamp": None},
                {"name": "BNP", "value": 74, "unit": "pg/mL", "reference_range": None, "timestamp": None},
            ],
            missing_tests=["Chest CT"],
            clinician_request="Generate differential considerations",
            model_results=acceptance_results(),
        )
        normalized = normalize_case_payload(payload).payload
        findings = {item["name"]: item for item in normalized["model_findings"]["findings"]}

        self.assertEqual(len(findings), 14)
        self.assertEqual(findings["Pulmonary fibrosis"]["decision"], "NEGATIVE")
        self.assertEqual(findings["Pulmonary fibrosis"]["confidence_band"], "NEAR_THRESHOLD_NEGATIVE")
        self.assertEqual(findings["Pneumothorax"]["confidence_band"], "CLEAR_NEGATIVE")
        self.assertEqual(findings["Calcification"]["threshold"], 0.9072)
        self.assertFalse(normalized["model_findings"]["score_calibrated_as_probability"])
        self.assertTrue(normalized["vitals"]["provided"])
        self.assertTrue(normalized["laboratory"]["provided"])
        self.assertEqual(normalized["missing_tests"], ["Chest CT"])
