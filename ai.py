"""AI analysis of policy documents via the Claude API.

Takes the raw text extracted from a policy (one or several documents) and asks
Claude to read the whole thing and return:
  - a plain-language summary (what it covers, exclusions, waiting periods…)
  - extracted key field/value pairs
  - coverage highlights and gaps to review

Degrades gracefully: if the anthropic SDK or the API key is missing, the AI
button simply hides and the regex parsing keeps working.
"""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

try:
    import anthropic

    _HAS_ANTHROPIC = True
except Exception:  # pragma: no cover
    _HAS_ANTHROPIC = False

DEFAULT_MODEL = "claude-opus-4-8"
MAX_INPUT_CHARS = 100_000  # policy text is small; guard against runaway cost

_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "Plain-language explanation of the policy in Markdown.",
        },
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["label", "value"],
                "additionalProperties": False,
            },
        },
        "coverage_highlights": {"type": "array", "items": {"type": "string"}},
        "exclusions_or_gaps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "fields", "coverage_highlights", "exclusions_or_gaps"],
    "additionalProperties": False,
}


def is_available() -> bool:
    return _HAS_ANTHROPIC


def is_configured() -> bool:
    if not _HAS_ANTHROPIC:
        return False
    try:
        return bool(st.secrets.get("anthropic_api_key"))
    except Exception:
        return False


def _model() -> str:
    try:
        return st.secrets.get("anthropic_model") or DEFAULT_MODEL
    except Exception:
        return DEFAULT_MODEL


def _system_prompt(region: str) -> str:
    if region == "cn":
        locale = (
            "These are Chinese internet insurance products (e.g. 百万医疗险, 重疾险). "
            "Write the `summary` in Simplified Chinese. Pay special attention to "
            "免赔额, 社保内/外报销比例, 保证续保年限, 等待期, 自动续保, and 续保条件."
        )
    else:
        locale = (
            "These are Singapore insurance products. Write the `summary` in English. "
            "Pay special attention to Integrated Shield Plan tier, deductible, "
            "co-insurance / co-payment, Sum Assured, riders, TPD, Critical Illness, "
            "premium term, and Medisave usage."
        )
    return (
        "You are a meticulous insurance analyst helping someone understand a policy. "
        f"{locale} Read the provided policy document text carefully and extract the "
        "facts faithfully — never invent numbers or terms that are not present; if "
        "something is unclear or missing, say so. In `fields`, list the concrete "
        "extracted key values (label/value pairs). In `coverage_highlights`, list what "
        "the policy covers well. In `exclusions_or_gaps`, list notable exclusions, "
        "waiting periods, caveats, or gaps worth reviewing. Keep the `summary` concise "
        "and easy to understand for a non-expert."
    )


def analyze(text: str, region: str) -> dict[str, Any]:
    """Analyze policy text with Claude. Returns the parsed result dict.

    Raises the underlying anthropic error on failure so the caller can surface it.
    """
    api_key = st.secrets["anthropic_api_key"]
    client = anthropic.Anthropic(api_key=api_key)

    truncated = text[:MAX_INPUT_CHARS]
    note = ""
    if len(text) > MAX_INPUT_CHARS:
        note = f"(input truncated to {MAX_INPUT_CHARS} characters)"

    response = client.messages.create(
        model=_model(),
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=_system_prompt(region),
        output_config={"format": {"type": "json_schema", "schema": _RESULT_SCHEMA}},
        messages=[
            {
                "role": "user",
                "content": f"Analyze this policy document text {note}:\n\n{truncated}",
            }
        ],
    )

    payload = next((b.text for b in response.content if b.type == "text"), "")
    result = json.loads(payload)
    result["_model"] = response.model
    return result
