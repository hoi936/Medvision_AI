"""Suggestion interaction summaries for assisted reader events."""

from __future__ import annotations

from .endpoints import rate


ACTIONS = {"ACCEPTED", "MODIFIED", "REJECTED"}


def _suggestions(events):
    return [
        suggestion
        for event in events if event.get("condition") == "HERMES_ASSISTED"
        for suggestion in event.get("ai_suggestions", [])
    ]


def human_ai_endpoints(events):
    suggestions = _suggestions(events)
    for suggestion in suggestions:
        if suggestion.get("action") not in ACTIONS or not isinstance(suggestion.get("ai_correct"), bool):
            raise ValueError("AI suggestion records require action and ai_correct")
    incorrect = [item for item in suggestions if not item["ai_correct"]]
    correct = [item for item in suggestions if item["ai_correct"]]
    return {
        "ai_suggestion_accepted": rate(sum(item["action"] == "ACCEPTED" for item in suggestions), len(suggestions)),
        "ai_suggestion_modified": rate(sum(item["action"] == "MODIFIED" for item in suggestions), len(suggestions)),
        "ai_suggestion_rejected": rate(sum(item["action"] == "REJECTED" for item in suggestions), len(suggestions)),
        "incorrect_ai_accepted": rate(sum(item["action"] == "ACCEPTED" for item in incorrect), len(incorrect)),
        "correct_ai_rejected": rate(sum(item["action"] == "REJECTED" for item in correct), len(correct)),
        "assistance_use": rate(sum(item["action"] in ACTIONS for item in suggestions), len(suggestions)),
    }
