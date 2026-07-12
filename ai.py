"""AI analysis of policy documents.

Supports multiple providers, chosen by which key is present in Streamlit secrets:
  - Google Gemini   (gemini_api_key)     — has a free tier; preferred by default
  - Anthropic Claude (anthropic_api_key)

Takes the raw text extracted from a policy and returns:
  - a plain-language summary (what it covers, exclusions, waiting periods…)
  - extracted key field/value pairs
  - coverage highlights and gaps to review

Degrades gracefully: if no provider SDK or key is available, the AI button hides
and the regex parsing keeps working.
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

try:
    from google import genai
    from google.genai import types as genai_types

    _HAS_GEMINI = True
except Exception:  # pragma: no cover
    _HAS_GEMINI = False

DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
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

_JSON_SHAPE_HINT = (
    "Return a JSON object with exactly these keys: "
    '"summary" (a Markdown string), '
    '"fields" (an array of {"label","value"} objects), '
    '"coverage_highlights" (an array of strings), and '
    '"exclusions_or_gaps" (an array of strings).'
)

# Columns to extract, matching the user's tracking spreadsheet.
SG_TEMPLATE_COLUMNS = [
    "Policy Name", "Provider", "Policy Number", "Product Type", "Covers",
    "Coverage Details", "Coverage Amount", "Annual Premium", "Premium End Date",
    "Payment Method", "Premium Due Date",
]
CN_TEMPLATE_COLUMNS = [
    "产品名称", "保险公司", "保单号", "产品类型", "保障范围", "保额", "免赔额",
    "社保内报销比例", "社保外报销比例", "保证续保年限", "保费", "缴费方式", "下次缴费日",
]


def template_columns(region: str) -> list[str]:
    return CN_TEMPLATE_COLUMNS if region == "cn" else SG_TEMPLATE_COLUMNS


def _template_instruction(region: str) -> str:
    cols = " | ".join(template_columns(region))
    return (
        "In `fields`, the FIRST entries MUST be exactly one per column below, using "
        f"the column name as the `label` (verbatim), in this order: {cols}. "
        "Use an empty string for any value you cannot find in the document — never "
        "guess. You may append additional useful fields after these."
    )


# =============================================================================
# Provider selection
# =============================================================================
def _secret(name: str) -> str:
    try:
        return st.secrets.get(name) or ""
    except Exception:
        return ""


def provider() -> str | None:
    """Return the active provider name, or None if unconfigured."""
    forced = _secret("ai_provider").lower()
    if forced == "gemini" and _HAS_GEMINI and _secret("gemini_api_key"):
        return "gemini"
    if forced == "claude" and _HAS_ANTHROPIC and _secret("anthropic_api_key"):
        return "claude"
    # Auto: prefer whichever key is present (Gemini first — it has a free tier).
    if _HAS_GEMINI and _secret("gemini_api_key"):
        return "gemini"
    if _HAS_ANTHROPIC and _secret("anthropic_api_key"):
        return "claude"
    return None


def is_available() -> bool:
    return _HAS_ANTHROPIC or _HAS_GEMINI


def is_configured() -> bool:
    return provider() is not None


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


# =============================================================================
# Public entry point
# =============================================================================
def analyze(text: str, region: str) -> dict[str, Any]:
    """Analyze policy text with the configured provider. Returns the result dict."""
    truncated = text[:MAX_INPUT_CHARS]
    note = f" (input truncated to {MAX_INPUT_CHARS} characters)" if len(text) > MAX_INPUT_CHARS else ""
    system = _system_prompt(region) + " " + _template_instruction(region)
    user = f"Analyze this policy document text{note}:\n\n{truncated}"

    active = provider()
    if active == "gemini":
        return _analyze_gemini(system, user)
    return _analyze_claude(system, user)


# =============================================================================
# Gemini (free tier)
# =============================================================================
def _analyze_gemini(system: str, user: str) -> dict[str, Any]:
    model = _secret("gemini_model") or DEFAULT_GEMINI_MODEL
    client = genai.Client(api_key=st.secrets["gemini_api_key"])
    response = client.models.generate_content(
        model=model,
        contents=f"{user}\n\n{_JSON_SHAPE_HINT}",
        config=genai_types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            max_output_tokens=4096,
        ),
    )
    result = json.loads(response.text)
    result["_model"] = model
    return result


# =============================================================================
# Claude
# =============================================================================
def _analyze_claude(system: str, user: str) -> dict[str, Any]:
    model = _secret("anthropic_model") or DEFAULT_CLAUDE_MODEL
    client = anthropic.Anthropic(api_key=st.secrets["anthropic_api_key"])
    response = client.messages.create(
        model=model,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        system=system,
        output_config={"format": {"type": "json_schema", "schema": _RESULT_SCHEMA}},
        messages=[{"role": "user", "content": user}],
    )
    payload = next((b.text for b in response.content if b.type == "text"), "")
    result = json.loads(payload)
    result["_model"] = response.model
    return result
