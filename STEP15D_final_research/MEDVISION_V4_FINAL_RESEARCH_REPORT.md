# MedVision AI V4 — Final Model Research Report

## Research status

- Primary research model: **DenseNet121 V4 E2 BEST, epoch 11**
- Number of findings: **14**
- Validation images: **2,992**
- Validation-positive image-class pairs: **1,762**
- No additional training performed during finalization
- Not validated for clinical diagnosis

## Controlled V4 comparison

| model | macro_pr_auc | micro_pr_auc | macro_roc_auc | micro_roc_auc |
| --- | --- | --- | --- | --- |
| E0 | 0.589099 | 0.793447 | 0.968744 | 0.980068 |
| E1 | 0.604774 | 0.789945 | 0.969113 | 0.979882 |
| E2 | 0.606153 | 0.791075 | 0.968667 | 0.978881 |

E2 achieves the highest observed macro average precision.
E0 achieves the highest micro average precision.
E1 remains a competitive alternative to E2.

E2 improves over E0 on 10/14 classes and over
E1 on 7/14 classes by average precision.

Approximately 88.85% of the total E2-E0
macro AP gain comes from Atelectasis, which has only
12 positive validation images.

## E2 classification and calibration

- Macro AP: 0.606153
- Micro AP: 0.791075
- Macro ROC-AUC: 0.968667
- Micro ROC-AUC: 0.978881
- Validation-tuned Macro F1: 0.612965
- Validation-tuned Micro F1: 0.722967
- Mean Brier Score: 0.052864
- Macro ECE (10 bins): 0.167910

Threshold selection and evaluation used the same
validation set. Tuned F1 is therefore exploratory
and potentially optimistic.

Calibration remains inadequate for interpreting sigmoid
outputs as clinically reliable disease probabilities.

## E2 localization

- Grad-CAM evaluated on all 1,762 positive pairs
- Macro pointing: 0.584934
- Micro pointing: 0.560726
- Macro IoU Top-10%: 0.242252
- Micro IoU Top-20%: 0.172402

The localization reference is a union of individual-reader
bounding boxes, not an independently verified
segmentation mask.

## Per-class findings

| finding | validation_positives | E2_AP | f1_optimized | pointing_accuracy | ece_10bins |
| --- | --- | --- | --- | --- | --- |
| Aortic enlargement | 469 | 0.9287 | 0.8490 | 0.6205 | 0.1303 |
| Atelectasis | 12 | 0.5200 | 0.6316 | 0.8333 | 0.1824 |
| Calcification | 35 | 0.2626 | 0.3571 | 0.3429 | 0.2442 |
| Cardiomegaly | 363 | 0.9086 | 0.8257 | 0.6722 | 0.1211 |
| Consolidation | 24 | 0.3833 | 0.4242 | 0.7917 | 0.1223 |
| ILD | 30 | 0.4099 | 0.4912 | 0.9333 | 0.1484 |
| Infiltration | 49 | 0.4907 | 0.5298 | 0.7959 | 0.1537 |
| Lung Opacity | 109 | 0.5772 | 0.5882 | 0.4954 | 0.1941 |
| Nodule/Mass | 81 | 0.4689 | 0.4812 | 0.3333 | 0.1912 |
| Other lesion | 72 | 0.2799 | 0.2897 | 0.1250 | 0.2219 |
| Pleural effusion | 127 | 0.9288 | 0.8759 | 0.6772 | 0.1559 |
| Pleural thickening | 176 | 0.6730 | 0.6529 | 0.2273 | 0.1727 |
| Pneumothorax | 12 | 0.8855 | 0.8696 | 0.7500 | 0.1230 |
| Pulmonary fibrosis | 203 | 0.7691 | 0.7153 | 0.5911 | 0.1895 |

## Exact-match stratification

- Positive-label images:
  351/888
  = 39.5270%
- Zero-positive-label images:
  2071/2104
  = 98.4316%
- All-negative prediction baseline:
  70.3209%

Overall exact-match should not be interpreted without
these prevalence-based group differences.

## Historical research context

V1/V2/V3 results are historical benchmarks, not
controlled ablations under the V4 training protocol.

## Major limitations

1. No independent held-out test set.
2. Patient-level independence is unverified.
3. Model checkpoint chosen using validation metrics.
4. Decision thresholds tuned on validation.
5. Rare findings have few positive cases.
6. Calibration is poor despite high ROC-AUC.
7. Grad-CAM is coarse and does not validate lesion location.
8. Clinical diagnostic performance has not been established.

## Frozen model identification

- E2 BEST SHA256: `87ae815b758b1b7425157d419da5a5e1d116d9d5f1225347274e3c84e7a97c19`
- Inference weights and metadata are in the exported
  MedVision V4 E2 inference package.
- E0 and E1 research checkpoints remain separate.

**Conclusion:** MedVision V4 E2 is the selected
research candidate, not a clinically validated system.
