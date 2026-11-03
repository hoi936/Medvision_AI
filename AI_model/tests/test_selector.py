from hermes_report import (
    CORE_HERMES_SKILLS,
    FINDING_SKILL_MAP,
    NO_FINDING_CONTRADICTION,
    NO_FINDING_WITHIN_14_CLASS_TAXONOMY,
    derive_no_finding_policy,
    resolve_hermes_skills,
)


def test_aortic_enlargement_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Aortic enlargement"] == "medvision-aortic-enlargement"


def test_atelectasis_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Atelectasis"] == "medvision-atelectasis"


def test_cardiomegaly_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Cardiomegaly"] == "medvision-cardiomegaly"


def test_consolidation_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Consolidation"] == "medvision-consolidation"


def test_pleural_effusion_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Pleural effusion"] == "medvision-pleural-effusion"


def test_nodule_mass_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Nodule/Mass"] == "medvision-nodule-mass"


def test_lung_opacity_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Lung Opacity"] == "medvision-lung-opacity"


def test_infiltration_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Infiltration"] == "medvision-infiltration"
    assert FINDING_SKILL_MAP["Infiltration"] != FINDING_SKILL_MAP["Lung Opacity"]


def test_ild_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["ILD"] == "medvision-ild"


def test_pulmonary_fibrosis_uses_exact_vinbigdata_canonical_label():
    assert FINDING_SKILL_MAP["Pulmonary fibrosis"] == (
        "medvision-pulmonary-fibrosis"
    )


def test_pleural_thickening_uses_exact_canonical_label():
    assert FINDING_SKILL_MAP["Pleural thickening"] == (
        "medvision-pleural-thickening"
    )


def test_calcification_uses_exact_canonical_label():
    assert FINDING_SKILL_MAP["Calcification"] == "medvision-calcification"


def test_other_lesion_uses_exact_label_without_no_finding_mapping():
    assert FINDING_SKILL_MAP["Other lesion"] == "medvision-other-lesion"
    assert "No finding" not in FINDING_SKILL_MAP


def test_positive_pneumothorax_selects_finding_skill():
    payload = {"model_findings": {"findings": [{"name": "Pneumothorax", "decision": "POSITIVE"}]}}
    skills = resolve_hermes_skills(payload)
    assert "medvision-pneumothorax" in skills


def test_no_positive_pneumothorax_does_not_select_finding_skill():
    payload = {"model_findings": {"findings": [{"name": "Pneumothorax", "decision": "NEGATIVE"}]}}
    skills = resolve_hermes_skills(payload)
    assert "medvision-pneumothorax" not in skills


def test_positive_pleural_effusion_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Pleural effusion", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-pleural-effusion" in skills


def test_negative_pleural_effusion_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Pleural effusion", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-pleural-effusion" not in skills


def test_positive_atelectasis_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Atelectasis", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-atelectasis" in skills


def test_negative_atelectasis_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Atelectasis", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-atelectasis" not in skills


def test_positive_consolidation_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Consolidation", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-consolidation" in skills


def test_negative_consolidation_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Consolidation", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-consolidation" not in skills


def test_positive_cardiomegaly_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Cardiomegaly", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-cardiomegaly" in skills


def test_negative_cardiomegaly_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Cardiomegaly", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-cardiomegaly" not in skills


def test_positive_aortic_enlargement_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Aortic enlargement", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-aortic-enlargement" in skills


def test_negative_aortic_enlargement_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Aortic enlargement", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-aortic-enlargement" not in skills


def test_positive_nodule_mass_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Nodule/Mass", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-nodule-mass" in skills


def test_negative_nodule_mass_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Nodule/Mass", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-nodule-mass" not in skills


def test_positive_lung_opacity_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Lung Opacity", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-lung-opacity" in skills


def test_negative_lung_opacity_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Lung Opacity", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-lung-opacity" not in skills


def test_positive_infiltration_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Infiltration", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-infiltration" in skills
    assert "medvision-lung-opacity" not in skills


def test_negative_infiltration_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Infiltration", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-infiltration" not in skills


def test_positive_ild_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "ILD", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-ild" in skills


def test_negative_ild_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "ILD", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-ild" not in skills


def test_positive_pulmonary_fibrosis_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "Pulmonary fibrosis", "decision": "POSITIVE"}
            ]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-pulmonary-fibrosis" in skills


def test_negative_pulmonary_fibrosis_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "Pulmonary fibrosis", "decision": "NEGATIVE"}
            ]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-pulmonary-fibrosis" not in skills


def test_positive_pleural_thickening_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "Pleural thickening", "decision": "POSITIVE"}
            ]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-pleural-thickening" in skills


def test_negative_pleural_thickening_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "Pleural thickening", "decision": "NEGATIVE"}
            ]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-pleural-thickening" not in skills


def test_positive_calcification_selects_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Calcification", "decision": "POSITIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-calcification" in skills


def test_negative_calcification_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Calcification", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-calcification" not in skills


def test_positive_other_lesion_selects_finding_skill_once_for_multiple_objects():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "Other lesion", "decision": "POSITIVE"},
                {"name": "Other lesion", "decision": "POSITIVE"},
            ]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert skills.count("medvision-other-lesion") == 1


def test_negative_other_lesion_does_not_select_finding_skill():
    payload = {
        "model_findings": {
            "findings": [{"name": "Other lesion", "decision": "NEGATIVE"}]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert "medvision-other-lesion" not in skills


def test_no_finding_is_not_mapped_to_other_lesion():
    payload = {
        "model_findings": {
            "findings": [{"name": "No finding", "decision": "POSITIVE"}]
        }
    }
    assert "medvision-other-lesion" not in resolve_hermes_skills(payload)


def test_selection_is_ordered_and_deduplicated():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "Pneumothorax", "decision": "POSITIVE"},
                {"name": "Pneumothorax", "decision": "POSITIVE"},
                {"name": "No finding", "decision": "POSITIVE"}
            ]
        }
    }
    skills = resolve_hermes_skills(payload)
    assert skills.count("medvision-pneumothorax") == 1
    assert skills == [
        "medvision-evidence-fusion",
        "medvision-pneumothorax",
        "medvision-safety-check",
        "medvision-disease-analysis",
    ]


def test_all_fourteen_positive_findings_are_selected_once_in_payload_order():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "Pneumothorax", "decision": "POSITIVE"},
                {"name": "Pleural effusion", "decision": "POSITIVE"},
                {"name": "Atelectasis", "decision": "POSITIVE"},
                {"name": "Consolidation", "decision": "POSITIVE"},
                {"name": "Cardiomegaly", "decision": "POSITIVE"},
                {"name": "Aortic enlargement", "decision": "POSITIVE"},
                {"name": "Nodule/Mass", "decision": "POSITIVE"},
                {"name": "Other lesion", "decision": "POSITIVE"},
                {"name": "Lung Opacity", "decision": "POSITIVE"},
                {"name": "Infiltration", "decision": "POSITIVE"},
                {"name": "ILD", "decision": "POSITIVE"},
                {"name": "Pulmonary fibrosis", "decision": "POSITIVE"},
                {"name": "Pleural thickening", "decision": "POSITIVE"},
                {"name": "Calcification", "decision": "POSITIVE"},
                {"name": "Pleural effusion", "decision": "POSITIVE"},
                {"name": "Pneumothorax", "decision": "POSITIVE"},
                {"name": "Atelectasis", "decision": "POSITIVE"},
                {"name": "Consolidation", "decision": "POSITIVE"},
                {"name": "Cardiomegaly", "decision": "POSITIVE"},
                {"name": "Aortic enlargement", "decision": "POSITIVE"},
                {"name": "Nodule/Mass", "decision": "POSITIVE"},
                {"name": "Other lesion", "decision": "POSITIVE"},
                {"name": "Lung Opacity", "decision": "POSITIVE"},
                {"name": "Infiltration", "decision": "POSITIVE"},
                {"name": "ILD", "decision": "POSITIVE"},
                {"name": "Pulmonary fibrosis", "decision": "POSITIVE"},
                {"name": "Pleural thickening", "decision": "POSITIVE"},
                {"name": "Calcification", "decision": "POSITIVE"},
            ]
        }
    }
    skills = resolve_hermes_skills(payload)
    finding_skills = {
        "medvision-pneumothorax",
        "medvision-pleural-effusion",
        "medvision-atelectasis",
        "medvision-consolidation",
        "medvision-cardiomegaly",
        "medvision-aortic-enlargement",
        "medvision-nodule-mass",
        "medvision-other-lesion",
        "medvision-lung-opacity",
        "medvision-infiltration",
        "medvision-ild",
        "medvision-pulmonary-fibrosis",
        "medvision-pleural-thickening",
        "medvision-calcification",
    }

    assert all(skills.count(skill) == 1 for skill in finding_skills)
    assert skills[0] == "medvision-evidence-fusion"
    assert set(skills[1:-2]) == finding_skills
    assert skills[1:-2] == [
        "medvision-pneumothorax",
        "medvision-pleural-effusion",
        "medvision-atelectasis",
        "medvision-consolidation",
        "medvision-cardiomegaly",
        "medvision-aortic-enlargement",
        "medvision-nodule-mass",
        "medvision-other-lesion",
        "medvision-lung-opacity",
        "medvision-infiltration",
        "medvision-ild",
        "medvision-pulmonary-fibrosis",
        "medvision-pleural-thickening",
        "medvision-calcification",
    ]
    assert skills[-2:] == [
        "medvision-safety-check",
        "medvision-disease-analysis",
    ]


def test_core_skills_keep_their_order_without_a_finding_skill():
    skills = resolve_hermes_skills({})
    assert skills == list(CORE_HERMES_SKILLS)


def _no_finding_payload(no_finding_decision, positive=()):
    findings = [
        {"name": "No finding", "decision": no_finding_decision},
        *[
            {
                "name": name,
                "decision": "POSITIVE" if name in positive else "NEGATIVE",
            }
            for name in FINDING_SKILL_MAP
        ],
    ]
    return {"model_findings": {"findings": findings}}


def test_no_finding_positive_with_all_targets_negative_uses_core_chain_only():
    payload = _no_finding_payload("POSITIVE")

    assert resolve_hermes_skills(payload) == list(CORE_HERMES_SKILLS)
    policy = derive_no_finding_policy(payload)
    assert policy["policy_state"] == NO_FINDING_WITHIN_14_CLASS_TAXONOMY
    assert policy["no_finding_conflict"]["present"] is False


def test_no_finding_positive_with_pneumothorax_routes_once_and_flags_conflict():
    payload = _no_finding_payload("POSITIVE", ("Pneumothorax",))

    skills = resolve_hermes_skills(payload)
    policy = derive_no_finding_policy(payload)
    assert skills.count("medvision-pneumothorax") == 1
    assert policy["policy_state"] == NO_FINDING_CONTRADICTION
    assert policy["no_finding_conflict"]["conflicting_positive_findings"] == [
        "Pneumothorax"
    ]


def test_no_finding_positive_with_multiple_findings_has_one_ordered_conflict():
    payload = _no_finding_payload(
        "POSITIVE", ("Cardiomegaly", "Pleural effusion")
    )

    skills = resolve_hermes_skills(payload)
    conflict = derive_no_finding_policy(payload)["no_finding_conflict"]
    assert skills.count("medvision-cardiomegaly") == 1
    assert skills.count("medvision-pleural-effusion") == 1
    assert conflict == {
        "present": True,
        "parent_type": "EVIDENCE_CONFLICT",
        "type": NO_FINDING_CONTRADICTION,
        "conflicting_positive_findings": [
            "Cardiomegaly", "Pleural effusion"
        ],
        "resolution": "doctor_review_required",
    }


def test_no_finding_negative_with_nodule_mass_routes_without_contradiction():
    payload = _no_finding_payload("NEGATIVE", ("Nodule/Mass",))

    skills = resolve_hermes_skills(payload)
    policy = derive_no_finding_policy(payload)
    assert skills.count("medvision-nodule-mass") == 1
    assert policy["policy_state"] == (
        "POSITIVE_FINDING_WITH_NO_FINDING_NEGATIVE"
    )
    assert policy["no_finding_conflict"]["present"] is False


def test_no_finding_negative_with_all_targets_negative_is_not_established():
    payload = _no_finding_payload("NEGATIVE")
    policy = derive_no_finding_policy(payload)

    assert resolve_hermes_skills(payload) == list(CORE_HERMES_SKILLS)
    assert policy["policy_state"] == "NO_FINDING_NOT_ESTABLISHED"
    assert policy["assessment"]["no_target_finding_within_taxonomy"] == (
        "not_established"
    )


def test_missing_no_finding_stays_missing_with_all_targets_negative():
    payload = _no_finding_payload("NEGATIVE")
    payload["model_findings"]["findings"] = payload["model_findings"][
        "findings"
    ][1:]
    policy = derive_no_finding_policy(payload)

    assert policy["policy_state"] == "NO_FINDING_MISSING"
    assert policy["no_finding"]["decision"] == "MISSING"
    assert policy["no_finding"]["present_in_payload"] is False


def test_no_finding_positive_with_all_fourteen_routes_all_once_and_one_conflict():
    payload = _no_finding_payload("POSITIVE", tuple(FINDING_SKILL_MAP))
    skills = resolve_hermes_skills(payload)
    policy = derive_no_finding_policy(payload)

    assert skills[0] == "medvision-evidence-fusion"
    assert skills[1:-2] == list(FINDING_SKILL_MAP.values())
    assert skills[-2:] == [
        "medvision-safety-check", "medvision-disease-analysis"
    ]
    assert all(skills.count(skill) == 1 for skill in FINDING_SKILL_MAP.values())
    assert policy["no_finding_conflict"]["present"] is True
    assert policy["no_finding_conflict"]["conflicting_positive_findings"] == (
        list(FINDING_SKILL_MAP)
    )
    assert len(policy["no_finding_conflict"]["conflicting_positive_findings"]) == 14
