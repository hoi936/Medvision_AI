"""Regression tests for selecting one of the six versioned models."""

from pathlib import Path
import sys
from unittest import TestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_registry import (
    DEFAULT_MODEL_ID,
    MODEL_IDS,
    get_model_spec,
    load_model_package,
)


class ModelRegistryTests(TestCase):
    def test_six_models_are_registered_and_e2_is_default(self):
        self.assertEqual(MODEL_IDS, ("v1", "v2", "v3", "e0", "e1", "e2"))
        self.assertEqual(DEFAULT_MODEL_ID, "e2")
        self.assertTrue(get_model_spec("e2").recommended)

    def test_each_package_has_checkpoint_and_14_versioned_thresholds(self):
        thresholds_by_model = {}
        for model_id in MODEL_IDS:
            spec, classes, thresholds, preprocessing = load_model_package(model_id)
            self.assertTrue(spec.checkpoint_path.is_file())
            self.assertEqual(len(classes), 14)
            self.assertEqual(len(thresholds), 14)
            self.assertEqual(preprocessing["image_size"], 384)
            thresholds_by_model[model_id] = thresholds

        self.assertNotEqual(thresholds_by_model["v1"], thresholds_by_model["v2"])
        self.assertNotEqual(thresholds_by_model["v2"], thresholds_by_model["v3"])
        self.assertNotEqual(thresholds_by_model["e0"], thresholds_by_model["e1"])
        self.assertNotEqual(thresholds_by_model["e1"], thresholds_by_model["e2"])

    def test_cbam_version_uses_its_own_architecture(self):
        self.assertEqual(get_model_spec("v2").architecture, "densenet121_cbam")
        self.assertEqual(get_model_spec("v1").architecture, "densenet121")
        self.assertEqual(get_model_spec("v3").architecture, "densenet121")
        self.assertEqual(get_model_spec("e0").architecture, "densenet121")
        self.assertEqual(get_model_spec("e1").architecture, "densenet121")
        self.assertEqual(get_model_spec("e2").architecture, "densenet121")
