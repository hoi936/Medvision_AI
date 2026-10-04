"""Risk lifecycle and template risks; software never accepts residual risk."""

from __future__ import annotations

from copy import deepcopy


RISK_STATES = {"OPEN", "MITIGATED", "ACCEPTANCE_REQUIRED", "ACCEPTED", "CLOSED"}
RESIDUAL_LEVELS = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
CORE_RISK_HAZARDS = (
    "unsupported diagnosis", "missing-as-negative", "score-as-probability",
    "temporal false progression", "conflict suppression", "autonomous action",
    "doctor-review bypass", "auto-finalization", "stale snapshot", "provider drift",
    "UI anchoring", "silent isolation breach", "wrong patient/data binding",
    "provider outage", "security issue",
)


class RiskRegisterError(ValueError):
    pass


def validate_risk(risk):
    required = {
        "risk_id", "category", "hazard", "cause", "affected_user", "potential_harm",
        "controls", "evidence", "residual_risk", "owner", "state",
    }
    if not isinstance(risk, dict) or not required <= set(risk):
        raise RiskRegisterError("risk record is incomplete")
    if risk["state"] not in RISK_STATES:
        raise RiskRegisterError("invalid risk lifecycle state")
    if risk["residual_risk"] not in RESIDUAL_LEVELS:
        raise RiskRegisterError("invalid residual-risk level")
    if not isinstance(risk["controls"], list) or not isinstance(risk["evidence"], list):
        raise RiskRegisterError("risk controls/evidence must be lists")
    if risk["state"] == "ACCEPTED":
        acceptance = risk.get("risk_acceptance")
        required_acceptance = {"decision", "accepted_by", "role", "date", "rationale", "scope"}
        if not isinstance(acceptance, dict) or not required_acceptance <= set(acceptance):
            raise RiskRegisterError("ACCEPTED requires explicit external risk_acceptance")
        if acceptance.get("decision") != "ACCEPTED" or not acceptance.get("accepted_by"):
            raise RiskRegisterError("software cannot accept residual risk")
    return risk


def seed_core_risk_templates():
    records = []
    for index, hazard in enumerate(CORE_RISK_HAZARDS, start=1):
        records.append({
            "risk_id": f"RISK-TEMPLATE-{index:02d}",
            "category": "CURRENT_PROJECT_RISK_TEMPLATE",
            "hazard": hazard,
            "cause": "foreseeable failure mode; no incident asserted",
            "affected_user": "clinician or patient depending on future stage",
            "potential_harm": "requires organization-specific assessment",
            "controls": ["frozen MedVision invariant and governance controls"],
            "evidence": ["provider-independent regression only"],
            "residual_risk": "MODERATE",
            "owner": "project governance assignment required",
            "state": "OPEN",
            "template_only": True,
            "incident_occurred": False,
        })
    return records


class RiskRegister:
    def __init__(self, risks=()):
        self._risks = {}
        for risk in risks:
            self.add(risk)

    def add(self, risk):
        validate_risk(risk)
        if risk["risk_id"] in self._risks:
            raise RiskRegisterError("duplicate risk_id")
        self._risks[risk["risk_id"]] = deepcopy(risk)

    def risks(self):
        return deepcopy(list(self._risks.values()))

    def blocking(self):
        return [
            risk for risk in self.risks()
            if risk["residual_risk"] in {"HIGH", "CRITICAL"}
            and risk["state"] not in {"ACCEPTED", "CLOSED"}
        ]
