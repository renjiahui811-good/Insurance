"""Build, save and list policy records as Markdown files.

Singapore records are saved in English under my_policies/.
China records keep Chinese field labels under parents_policies/.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
MY_POLICIES = BASE_DIR / "my_policies"
PARENTS_POLICIES = BASE_DIR / "parents_policies"


def slugify(value: str, fallback: str = "policy") -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^\w一-鿿]+", "-", value)
    value = value.strip("-")
    return value or fallback


def _row(label: str, value: Any) -> str:
    return f"| {label} | {value if value not in (None, '') else '—'} |"


# =============================================================================
# Singapore (English) record
# =============================================================================
def build_sg_markdown(d: dict[str, Any]) -> str:
    lines = [
        f"# Policy Record — {d.get('nickname') or d.get('product_name') or 'Untitled'}",
        "",
        "> Singapore policy. All fields in English.",
        "",
        "## Overview",
        "",
        "| Field | Value |",
        "|-------|-------|",
        _row("Policy Nickname", d.get("nickname")),
        _row("Policyholder", d.get("policyholder")),
        _row("Life Assured", d.get("life_assured")),
        _row("Insurer", d.get("insurer")),
        _row("Product Name", d.get("product_name")),
        _row("Policy Number", d.get("policy_number")),
        _row("Policy Type", d.get("policy_type")),
        _row("Status", d.get("status")),
        "",
        "## Coverage & Benefits",
        "",
        "| Field | Value |",
        "|-------|-------|",
        _row("Sum Assured", _sgd(d.get("sum_assured"))),
        _row("Critical Illness Coverage", _sgd(d.get("ci_coverage"))),
        _row("TPD Benefit", _sgd(d.get("tpd"))),
        _row("Riders", d.get("riders")),
        "",
        "## Integrated Shield Plan",
        "",
        "| Field | Value |",
        "|-------|-------|",
        _row("Ward / Hospital Class", d.get("ward_class")),
        _row("Deductible", _sgd(d.get("deductible"))),
        _row("Co-Insurance", d.get("co_insurance")),
        _row("Panel / Non-Panel", d.get("panel")),
        "",
        "## Premium & Payment",
        "",
        "| Field | Value |",
        "|-------|-------|",
        _row("Premium Amount", _sgd(d.get("premium"))),
        _row("Payment Frequency", d.get("frequency")),
        _row("Premium Term", d.get("premium_term")),
        _row("Medisave Pay", d.get("medisave_pay")),
        _row("Next Due Date", d.get("next_due")),
        "",
        "## Key Dates",
        "",
        "| Field | Value |",
        "|-------|-------|",
        _row("Policy Start Date", d.get("start_date")),
        _row("Maturity Date", d.get("maturity_date")),
        "",
        "## Notes",
        "",
        (d.get("notes") or "—"),
        "",
        f"_Saved via Insurance Portal on {date.today().isoformat()}._",
        "",
    ]
    return "\n".join(lines)


def _sgd(value: Any) -> str:
    if value in (None, ""):
        return ""
    return f"S$ {value}"


# =============================================================================
# China (Chinese) record
# =============================================================================
def build_cn_markdown(d: dict[str, Any]) -> str:
    lines = [
        f"# 保单记录 — {d.get('nickname') or d.get('product_name') or '未命名'}",
        "",
        "> 中国互联网保险保单。关键字段保留中文。",
        "",
        "## 基本信息 (Overview)",
        "",
        "| 字段 Field | 数值 Value |",
        "|-----------|-----------|",
        _row("保单昵称 Nickname", d.get("nickname")),
        _row("投保人 Policyholder", d.get("policyholder")),
        _row("被保险人 Insured", d.get("insured_person")),
        _row("与我关系 Relationship", d.get("relationship")),
        _row("保险公司 Insurer", d.get("insurer")),
        _row("产品名称 Product", d.get("product_name")),
        _row("保单号 Policy No.", d.get("policy_number")),
        _row("产品类型 Type", d.get("policy_type")),
        _row("保单状态 Status", d.get("status")),
        "",
        "## 保障内容 (Coverage)",
        "",
        "| 字段 Field | 数值 Value |",
        "|-----------|-----------|",
        _row("保额 Sum Assured", d.get("sum_assured")),
        _row("免赔额 Deductible", d.get("deductible")),
        _row("社保内报销比例 In-Scheme %", d.get("reimburse_in")),
        _row("社保外报销比例 Out-of-Scheme %", d.get("reimburse_out")),
        _row("保证续保年限 Guaranteed Renewal", d.get("guaranteed_renewal")),
        _row("等待期 Waiting Period", d.get("waiting_period")),
        "",
        "## 缴费信息 (Premium & Payment)",
        "",
        "| 字段 Field | 数值 Value |",
        "|-----------|-----------|",
        _row("保费 Premium", d.get("premium")),
        _row("缴费频率 Frequency", d.get("frequency")),
        _row("是否自动续保 Auto-Renew", d.get("auto_renew")),
        _row("自动续保扣款账户 Auto-Debit Account", d.get("debit_account")),
        _row("下次缴费日 Next Due", d.get("next_due")),
        "",
        "## 关键日期 (Key Dates)",
        "",
        "| 字段 Field | 数值 Value |",
        "|-----------|-----------|",
        _row("保险期间起 Start Date", d.get("start_date")),
        _row("保险期间止 End Date", d.get("end_date")),
        "",
        "## 备注 (Notes)",
        "",
        (d.get("notes") or "—"),
        "",
        f"_由 Insurance Portal 于 {date.today().isoformat()} 保存。_",
        "",
    ]
    return "\n".join(lines)


# =============================================================================
# Save / list
# =============================================================================
def save_record(folder: Path, filename_stem: str, content: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{slugify(filename_stem)}.md"
    path.write_text(content, encoding="utf-8")
    return path


def list_records(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    files = sorted(folder.glob("*.md"))
    records = [f for f in files if not f.name.startswith(("_", "README"))]
    others = [f for f in files if f.name.startswith(("_", "README"))]
    return records + others
