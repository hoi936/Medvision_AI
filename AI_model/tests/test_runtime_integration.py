"""Hermes runtime integration tests; these do not call an LLM provider."""

import json
import os
from pathlib import Path
import subprocess

from hermes_report import (
    CORE_HERMES_SKILLS,
    FINDING_SKILL_MAP,
    HERMES_HOME,
    HERMES_RUNTIME,
    HERMES_SKILLS_TOOLS,
    HERMES_TEXT_TOOLSETS,
    HERMES_VISION_TOOLSETS,
    discover_hermes_skills,
    get_hermes_status,
    hermes_environment,
    hermes_skill_write_approval_enabled,
    inspect_hermes_skill,
    locate_hermes,
)


def test_uses_project_isolated_executable_and_home():
    executable = locate_hermes()
    assert executable is not None
    assert executable == (HERMES_RUNTIME / "bin" / "hermes").resolve()
    assert HERMES_HOME == HERMES_RUNTIME.parent / "hermes-home"
    assert hermes_environment()["HERMES_HOME"] == str(HERMES_HOME)
    completed = subprocess.run(
        [str(executable), "--version"],
        cwd=Path(__file__).resolve().parents[2],
        env=hermes_environment(),
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    assert "0.21.4" in completed.stdout


def test_all_medvision_skills_are_discoverable_by_cli():
    expected = {*CORE_HERMES_SKILLS, *FINDING_SKILL_MAP.values()}
    assert discover_hermes_skills() == expected
    project_root = Path(__file__).resolve().parents[2]
    local_skills = {
        path.parent.name
        for path in (project_root / ".hermes" / "skills").glob("*/SKILL.md")
    }
    assert local_skills == expected
    assert len(local_skills) == 17
    assert "medvision-no-finding" not in local_skills
    status = get_hermes_status()
    assert status.core_ready is True
    assert status.available_finding_skills == [
        "medvision-aortic-enlargement",
        "medvision-atelectasis",
        "medvision-cardiomegaly",
        "medvision-calcification",
        "medvision-consolidation",
        "medvision-ild",
        "medvision-infiltration",
        "medvision-lung-opacity",
        "medvision-nodule-mass",
        "medvision-other-lesion",
        "medvision-pleural-effusion",
        "medvision-pleural-thickening",
        "medvision-pneumothorax",
        "medvision-pulmonary-fibrosis",
    ]
    assert status.missing_finding_skills == []


def test_finding_skills_use_frozen_frontmatter_template():
    project_root = Path(__file__).resolve().parents[2]
    expected_metadata_lines = {
        "medvision-aortic-enlargement": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: aortic_enlargement",
            "- Requires doctor review: true",
        },
        "medvision-pneumothorax": {
            "- Version: `1.0.0`",
            "- Domain: `thoracic-radiology`",
            "- Finding: `pneumothorax`",
            "- Doctor review required: `true`",
        },
        "medvision-pleural-effusion": {
            "- Version: `1.0.0`",
            "- Domain: `thoracic-radiology`",
            "- Finding: `pleural_effusion`",
            "- Doctor review required: `true`",
        },
        "medvision-atelectasis": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: atelectasis",
            "- Requires doctor review: true",
        },
        "medvision-consolidation": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: consolidation",
            "- Requires doctor review: true",
        },
        "medvision-cardiomegaly": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: cardiomegaly",
            "- Requires doctor review: true",
        },
        "medvision-calcification": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: calcification",
            "- Requires doctor review: true",
        },
        "medvision-nodule-mass": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: nodule_mass",
            "- Requires doctor review: true",
        },
        "medvision-other-lesion": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: other_lesion",
            "- Requires doctor review: true",
        },
        "medvision-lung-opacity": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: lung_opacity",
            "- Requires doctor review: true",
        },
        "medvision-infiltration": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: infiltration",
            "- Requires doctor review: true",
        },
        "medvision-ild": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: ild",
            "- Requires doctor review: true",
        },
        "medvision-pulmonary-fibrosis": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: pulmonary_fibrosis",
            "- Requires doctor review: true",
        },
        "medvision-pleural-thickening": {
            "- Version: 1.0.0",
            "- Domain: thoracic-radiology",
            "- Finding: pleural_thickening",
            "- Requires doctor review: true",
        },
    }

    for skill_name, metadata_lines in expected_metadata_lines.items():
        content = (
            project_root / ".hermes" / "skills" / skill_name / "SKILL.md"
        ).read_text(encoding="utf-8")
        frontmatter = content.split("---", 2)[1]
        keys = {
            line.split(":", 1)[0].strip()
            for line in frontmatter.splitlines()
            if ":" in line
        }

        assert keys == {"name", "description"}
        assert "## MedVision Metadata" in content
        assert all(line in content for line in metadata_lines)


def test_selected_and_effective_tool_surfaces_have_no_unrelated_tools():
    executable = locate_hermes()
    assert executable is not None
    runtime_python = executable.parent / ("python.exe" if os.name == "nt" else "python")
    probe = r'''
import json, sys
from model_tools import get_tool_definitions
from toolsets import resolve_toolset
toolsets = list(sys.argv[1:])
selected = sorted(set().union(*(resolve_toolset(name) for name in toolsets)))
effective = sorted(
    item["function"]["name"]
    for item in get_tool_definitions(enabled_toolsets=toolsets, quiet_mode=True)
)
print(json.dumps({"selected": selected, "effective": effective}))
'''

    def resolve(toolsets):
        completed = subprocess.run(
            [str(runtime_python), "-c", probe, *toolsets],
            cwd=Path(__file__).resolve().parents[2],
            env=hermes_environment(),
            capture_output=True,
            text=True,
            check=True,
            shell=False,
        )
        result = json.loads(completed.stdout)
        return set(result["selected"]), set(result["effective"])

    text_selected, text_effective = resolve(HERMES_TEXT_TOOLSETS)
    vision_selected, vision_effective = resolve(HERMES_VISION_TOOLSETS)
    assert text_selected == {"clarify", *HERMES_SKILLS_TOOLS}
    assert vision_selected == {"clarify", "vision_analyze", *HERMES_SKILLS_TOOLS}
    assert text_effective == text_selected
    # With no configured vision provider, Hermes correctly filters vision_analyze
    # from effective definitions. Once configured, it is the only permitted addition.
    assert vision_effective in (text_effective, text_effective | {"vision_analyze"})
    forbidden = {
        "terminal",
        "process_manage",
        "browser_navigate",
        "read_file",
        "write_file",
        "patch",
        "execute_code",
        "delegate_task",
        "discord",
    }
    assert text_selected.isdisjoint(forbidden)
    assert vision_selected.isdisjoint(forbidden)
    assert text_effective.isdisjoint(forbidden)
    assert vision_effective.isdisjoint(forbidden)


def test_native_skill_view_reads_skill_and_reference():
    skill = inspect_hermes_skill("medvision-pneumothorax")
    reference = inspect_hermes_skill(
        "medvision-pneumothorax", "references/references.md"
    )
    assert skill["_source_path"].endswith("medvision-pneumothorax/SKILL.md")
    assert "MedVision Pneumothorax Skill" in skill["content"]
    assert reference["file"] == "references/references.md"
    assert reference["content"]

    no_finding_evidence = inspect_hermes_skill(
        "medvision-evidence-fusion", "references/NO_FINDING_EVIDENCE.md"
    )
    no_finding_references = inspect_hermes_skill(
        "medvision-evidence-fusion", "references/NO_FINDING_REFERENCES.md"
    )
    no_finding_policy = inspect_hermes_skill(
        "medvision-evidence-fusion", "references/NO_FINDING_POLICY.md"
    )
    assert no_finding_evidence["file"] == "references/NO_FINDING_EVIDENCE.md"
    assert "NO_FINDING_CONTRADICTION" in no_finding_evidence["content"]
    assert no_finding_references["file"] == "references/NO_FINDING_REFERENCES.md"
    assert "## Source S1" in no_finding_references["content"]
    assert no_finding_policy["file"] == "references/NO_FINDING_POLICY.md"
    assert "## Policy states" in no_finding_policy["content"]

    effusion = inspect_hermes_skill("medvision-pleural-effusion")
    effusion_reference = inspect_hermes_skill(
        "medvision-pleural-effusion", "references/references.md"
    )
    assert effusion["_source_path"].endswith("medvision-pleural-effusion/SKILL.md")
    assert "MedVision Pleural Effusion Skill" in effusion["content"]
    assert effusion_reference["file"] == "references/references.md"
    assert "S1 — Fleischner Society 2024" in effusion_reference["content"]

    atelectasis = inspect_hermes_skill("medvision-atelectasis")
    atelectasis_reference = inspect_hermes_skill(
        "medvision-atelectasis", "references/references.md"
    )
    assert atelectasis["_source_path"].endswith("medvision-atelectasis/SKILL.md")
    assert "MedVision Atelectasis Skill" in atelectasis["content"]
    assert atelectasis_reference["file"] == "references/references.md"
    assert "## Source S1" in atelectasis_reference["content"]
    assert "Fleischner Society: Glossary of Terms for Thoracic Imaging" in (
        atelectasis_reference["content"]
    )

    consolidation = inspect_hermes_skill("medvision-consolidation")
    consolidation_reference = inspect_hermes_skill(
        "medvision-consolidation", "references/references.md"
    )
    assert consolidation["_source_path"].endswith("medvision-consolidation/SKILL.md")
    assert "MedVision Consolidation Skill" in consolidation["content"]
    assert consolidation_reference["file"] == "references/references.md"
    assert "## Source S1" in consolidation_reference["content"]
    assert "Fleischner Society: Glossary of Terms for Thoracic Imaging" in (
        consolidation_reference["content"]
    )

    cardiomegaly = inspect_hermes_skill("medvision-cardiomegaly")
    cardiomegaly_reference = inspect_hermes_skill(
        "medvision-cardiomegaly", "references/references.md"
    )
    assert cardiomegaly["_source_path"].endswith("medvision-cardiomegaly/SKILL.md")
    assert "MedVision Cardiomegaly Skill" in cardiomegaly["content"]
    assert cardiomegaly_reference["file"] == "references/references.md"
    assert "## Source S1" in cardiomegaly_reference["content"]
    assert "Radiological Cardiothoracic Ratio in Evidence-Based Medicine" in (
        cardiomegaly_reference["content"]
    )
    assert "Truszkiewicz K, Poręba R, Gać P" in cardiomegaly_reference["content"]

    aortic_enlargement = inspect_hermes_skill("medvision-aortic-enlargement")
    aortic_reference = inspect_hermes_skill(
        "medvision-aortic-enlargement", "references/references.md"
    )
    assert aortic_enlargement["_source_path"].endswith(
        "medvision-aortic-enlargement/SKILL.md"
    )
    assert "MedVision Aortic Enlargement Skill" in aortic_enlargement["content"]
    assert aortic_reference["file"] == "references/references.md"
    assert "## Source S1" in aortic_reference["content"]
    assert "2024 ESC Guidelines for the management of peripheral arterial and aortic diseases" in (
        aortic_reference["content"]
    )
    assert "Mazzolai L, Teixido-Tura G, Lanzi S" in aortic_reference["content"]

    nodule_mass = inspect_hermes_skill("medvision-nodule-mass")
    nodule_reference = inspect_hermes_skill(
        "medvision-nodule-mass", "references/references.md"
    )
    assert nodule_mass["_source_path"].endswith("medvision-nodule-mass/SKILL.md")
    assert "MedVision Nodule/Mass Skill" in nodule_mass["content"]
    assert nodule_reference["file"] == "references/references.md"
    assert "## Source S1" in nodule_reference["content"]
    assert "Fleischner Society: Glossary of Terms for Thoracic Imaging" in (
        nodule_reference["content"]
    )
    assert "Bankier AA, MacMahon H, Colby T" in nodule_reference["content"]

    lung_opacity = inspect_hermes_skill("medvision-lung-opacity")
    opacity_reference = inspect_hermes_skill(
        "medvision-lung-opacity", "references/references.md"
    )
    assert lung_opacity["_source_path"].endswith("medvision-lung-opacity/SKILL.md")
    assert "MedVision Lung Opacity Skill" in lung_opacity["content"]
    assert opacity_reference["file"] == "references/references.md"
    assert "## Source S1" in opacity_reference["content"]
    assert "Fleischner Society: Glossary of Terms for Thoracic Imaging" in (
        opacity_reference["content"]
    )
    assert "## Source S2" in opacity_reference["content"]
    assert "VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations" in (
        opacity_reference["content"]
    )

    infiltration = inspect_hermes_skill("medvision-infiltration")
    infiltration_reference = inspect_hermes_skill(
        "medvision-infiltration", "references/references.md"
    )
    assert infiltration["_source_path"].endswith("medvision-infiltration/SKILL.md")
    assert "MedVision Infiltration Skill" in infiltration["content"]
    assert infiltration_reference["file"] == "references/references.md"
    assert "Fleischner Society: Glossary of Terms for Thoracic Imaging" in (
        infiltration_reference["content"]
    )
    assert "VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations" in (
        infiltration_reference["content"]
    )
    assert "Is infiltrate a useful term in the interpretation of chest radiographs?" in (
        infiltration_reference["content"]
    )
    assert "Patterson HS, Sponaugle DN" in infiltration_reference["content"]

    ild = inspect_hermes_skill("medvision-ild")
    ild_reference = inspect_hermes_skill(
        "medvision-ild", "references/references.md"
    )
    assert ild["_source_path"].endswith("medvision-ild/SKILL.md")
    assert "MedVision ILD Skill" in ild["content"]
    assert ild_reference["file"] == "references/references.md"
    assert "Update of the international multidisciplinary classification of the interstitial pneumonias: an ERS/ATS statement" in ild_reference["content"]
    assert "Idiopathic Pulmonary Fibrosis (an Update) and Progressive Pulmonary Fibrosis in Adults" in ild_reference["content"]
    assert "Approach to the Evaluation and Management of Interstitial Lung Abnormalities" in ild_reference["content"]

    pulmonary_fibrosis = inspect_hermes_skill("medvision-pulmonary-fibrosis")
    fibrosis_reference = inspect_hermes_skill(
        "medvision-pulmonary-fibrosis", "references/references.md"
    )
    assert pulmonary_fibrosis["_source_path"].endswith(
        "medvision-pulmonary-fibrosis/SKILL.md"
    )
    assert "MedVision Pulmonary Fibrosis Skill" in pulmonary_fibrosis["content"]
    assert fibrosis_reference["file"] == "references/references.md"
    assert "VinDr-CXR: An open dataset of chest X-rays with radiologist's annotations" in fibrosis_reference["content"]
    assert "Progressive Pulmonary Fibrosis in Adults" in fibrosis_reference["content"]
    assert "High-Resolution Computed Tomography of Fibrotic Interstitial Lung Disease" in fibrosis_reference["content"]
    assert "Imaging in the diagnosis and management of fibrosing interstitial lung diseases" in fibrosis_reference["content"]
    assert "Update of the international multidisciplinary classification of the interstitial pneumonias" in fibrosis_reference["content"]

    pleural_thickening = inspect_hermes_skill("medvision-pleural-thickening")
    thickening_reference = inspect_hermes_skill(
        "medvision-pleural-thickening", "references/references.md"
    )
    assert pleural_thickening["_source_path"].endswith(
        "medvision-pleural-thickening/SKILL.md"
    )
    assert "MedVision Pleural Thickening Skill" in pleural_thickening["content"]
    assert thickening_reference["file"] == "references/references.md"
    assert "Pictorial Review of Pleural Disease" in thickening_reference["content"]
    assert "British Thoracic Society Guideline for pleural disease" in thickening_reference["content"]
    assert "Alfudhili KM" in thickening_reference["content"]
    assert "Miles SE" in thickening_reference["content"]

    calcification = inspect_hermes_skill("medvision-calcification")
    calcification_reference = inspect_hermes_skill(
        "medvision-calcification", "references/references.md"
    )
    assert calcification["_source_path"].endswith(
        "medvision-calcification/SKILL.md"
    )
    assert "MedVision Calcification Skill" in calcification["content"]
    assert calcification_reference["file"] == "references/references.md"
    assert "VinDr-CXR: An open dataset of chest X-rays" in calcification_reference["content"]
    assert "Pulmonary Calcification and Ossification" in calcification_reference["content"]
    assert "Chest calcifications beyond the lung parenchyma" in calcification_reference["content"]
    assert "Calcified Lung Nodules" in calcification_reference["content"]
    assert "Fleischner Society: Glossary of Terms for Thoracic Imaging" in calcification_reference["content"]

    other_lesion = inspect_hermes_skill("medvision-other-lesion")
    other_lesion_reference = inspect_hermes_skill(
        "medvision-other-lesion", "references/references.md"
    )
    assert other_lesion["_source_path"].endswith(
        "medvision-other-lesion/SKILL.md"
    )
    assert "MedVision Other Lesion Skill" in other_lesion["content"]
    assert other_lesion_reference["file"] == "references/references.md"
    assert "VinDr-CXR: An open dataset of chest X-rays" in other_lesion_reference["content"]
    assert "VinBigData Chest X-ray Abnormalities Detection" in other_lesion_reference["content"]
    assert "Fleischner Society: Glossary of Terms for Thoracic Imaging" in other_lesion_reference["content"]
    assert "Deployment and validation of an AI system" in other_lesion_reference["content"]


def test_skill_manage_is_approval_gated_and_cannot_write_directly():
    assert hermes_skill_write_approval_enabled() is True
    runtime_python = locate_hermes().parent / ("python.exe" if os.name == "nt" else "python")
    probe = r'''
import json
from hermes_constants import get_hermes_home
from tools.write_approval import SKILLS, discard_pending, write_approval_enabled
if not write_approval_enabled(SKILLS):
    raise SystemExit("skill write approval is disabled")
from tools.skill_manager_tool import skill_manage
name = "medvision-runtime-write-gate-probe"
target = get_hermes_home() / "skills" / name
if target.exists():
    raise SystemExit(f"probe target already exists: {target}")
raw = skill_manage(
    action="create",
    name=name,
    content="---\nname: medvision-runtime-write-gate-probe\ndescription: gate probe\n---\n# Probe\n",
)
result = json.loads(raw)
pending_id = result.get("pending_id", "")
payload = {
    "staged": result.get("staged") is True,
    "target_exists": target.exists(),
    "pending_removed": bool(pending_id and discard_pending(SKILLS, pending_id)),
}
print(json.dumps(payload))
'''
    completed = subprocess.run(
        [str(runtime_python), "-c", probe],
        cwd=Path(__file__).resolve().parents[2],
        env=hermes_environment(),
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    result = json.loads(completed.stdout)
    assert result == {
        "staged": True,
        "target_exists": False,
        "pending_removed": True,
    }
