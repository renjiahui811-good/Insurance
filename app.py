"""Personal Insurance Portal — Streamlit app.

Sections:
  - My Policies (Singapore)   — English fields, Integrated Shield / Medisave etc.
  - Parents' Policies (China) — Chinese fields, 免赔额 / 社保报销 / 保证续保 etc.
  - AIA Products              — advisory product summaries
  - Client Profiles           — advisory client records

Each policy page offers two entry modes:
  A. Upload a policy PDF/image → auto text extraction + best-effort parsing.
  B. Manual form → adjust / complete any field, then save as a Markdown record.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import parsers
import records as rec

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="Personal Insurance Portal", page_icon="🛡️", layout="wide")


# =============================================================================
# Shared helpers
# =============================================================================
def render_record_browser(folder: Path, empty_hint: str) -> None:
    """Sidebar-style record picker + main-area Markdown viewer."""
    files = rec.list_records(folder)
    if not files:
        st.info(empty_hint)
        return

    def label(p: Path) -> str:
        if p.name.startswith("_"):
            return f"📄 {p.stem.lstrip('_')} (template)"
        if p.name == "README.md":
            return "ℹ️ README"
        return f"📝 {p.stem}"

    choice = st.selectbox("Saved records", files, format_func=label)
    if choice:
        st.caption(f"Source: `{choice.relative_to(BASE_DIR)}`")
        st.markdown(choice.read_text(encoding="utf-8"))


def upload_and_parse(parse_fn, key: str) -> dict:
    """File uploader → extract text → parse fields. Returns parsed dict (or {})."""
    caps = []
    caps.append("PDF ✅" if parsers.CAPABILITIES["pdf"] else "PDF ❌")
    caps.append("Image OCR ✅" if parsers.CAPABILITIES["ocr"] else "Image OCR ❌")
    st.caption("Parser capabilities: " + " · ".join(caps))

    uploaded = st.file_uploader(
        "Upload Policy PDF / Image",
        type=["pdf", "png", "jpg", "jpeg", "webp", "tiff", "bmp", "txt", "md"],
        key=f"upload_{key}",
    )
    if uploaded is None:
        return {}

    file_bytes = uploaded.getvalue()
    with st.spinner("Extracting text…"):
        text, note = parsers.extract_text(file_bytes, uploaded.name)

    if note:
        st.warning(note)
    if not text:
        return {}

    parsed = parse_fn(text)
    found = {k: v for k, v in parsed.items() if v}
    st.success(f"Extracted {len(text)} characters · auto-filled {len(found)} field(s).")

    with st.expander("View extracted raw text"):
        st.text(text[:5000] + ("…" if len(text) > 5000 else ""))

    if found:
        st.write("**Auto-detected fields** (review & adjust below):")
        st.json(found)

    # Stash into session so the form below can pre-fill.
    st.session_state[f"parsed_{key}"] = parsed
    return parsed


def _pf(key: str, field: str, default: str = "") -> str:
    """Read a previously-parsed field from session state as form default."""
    parsed = st.session_state.get(f"parsed_{key}", {})
    return parsed.get(field) or default


# =============================================================================
# Page: My Policies (Singapore) — English
# =============================================================================
def page_my_policies() -> None:
    st.title("🇸🇬 My Policies — Singapore")
    st.write("Manage your own Singapore insurance policies (English).")

    tab_add, tab_view = st.tabs(["➕ Add Policy", "📚 View Saved"])

    with tab_add:
        st.subheader("A. Upload & Auto-Parse")
        upload_and_parse(parsers.parse_sg_fields, key="sg")

        st.subheader("B. Policy Form")
        with st.form("sg_form"):
            c1, c2 = st.columns(2)
            with c1:
                nickname = st.text_input("Policy Nickname", value=_pf("sg", "product_name"))
                policyholder = st.text_input("Policyholder")
                life_assured = st.text_input("Life Assured", value=_pf("sg", "life_assured"))
                insurer = st.text_input("Insurer", value=_pf("sg", "insurer") or "AIA")
                product_name = st.text_input("Product Name", value=_pf("sg", "product_name"))
                policy_number = st.text_input("Policy Number", value=_pf("sg", "policy_number"))
                policy_type = st.selectbox(
                    "Policy Type",
                    ["", "Integrated Shield Plan", "Whole Life", "Term Life",
                     "Critical Illness", "Endowment", "Investment-Linked (ILP)",
                     "Personal Accident", "Disability Income"],
                    index=0,
                )
                status = st.selectbox("Status", ["In Force", "Lapsed", "Paid-Up", "Matured", "Claimed"])
            with c2:
                sum_assured = st.text_input("Sum Assured (S$)", value=_pf("sg", "sum_assured"))
                ci_coverage = st.text_input("Critical Illness Coverage (S$)")
                tpd = st.text_input("TPD Benefit (S$)")
                riders = st.text_input("Riders")

            st.markdown("**Integrated Shield Plan**")
            c3, c4 = st.columns(2)
            with c3:
                ward_class = st.selectbox("Ward / Hospital Class", ["", "Private", "A", "B1", "B2", "C"])
                deductible = st.text_input("Deductible (S$)", value=_pf("sg", "deductible"))
            with c4:
                co_insurance = st.text_input("Co-Insurance (%)", value=_pf("sg", "co_insurance"))
                panel = st.selectbox("Panel / Non-Panel", ["", "Panel", "Non-Panel"])

            st.markdown("**Premium & Payment**")
            c5, c6 = st.columns(2)
            with c5:
                premium = st.text_input("Premium Amount (S$)", value=_pf("sg", "premium"))
                frequency = st.selectbox("Payment Frequency", ["Annual", "Semi-Annual", "Quarterly", "Monthly", "Single"])
                premium_term = st.text_input("Premium Term")
            with c6:
                medisave_pay = st.selectbox("Medisave Pay", ["", "Yes", "No"])
                next_due = st.text_input("Next Due Date (YYYY-MM-DD)")

            st.markdown("**Key Dates**")
            c7, c8 = st.columns(2)
            with c7:
                start_date = st.text_input("Policy Start Date", value=_pf("sg", "start_date"))
            with c8:
                maturity_date = st.text_input("Maturity Date")

            notes = st.text_area("Notes")
            submitted = st.form_submit_button("💾 Save Policy")

        if submitted:
            data = dict(
                nickname=nickname, policyholder=policyholder, life_assured=life_assured,
                insurer=insurer, product_name=product_name, policy_number=policy_number,
                policy_type=policy_type, status=status, sum_assured=sum_assured,
                ci_coverage=ci_coverage, tpd=tpd, riders=riders, ward_class=ward_class,
                deductible=deductible, co_insurance=co_insurance, panel=panel,
                premium=premium, frequency=frequency, premium_term=premium_term,
                medisave_pay=medisave_pay, next_due=next_due, start_date=start_date,
                maturity_date=maturity_date, notes=notes,
            )
            stem = nickname or product_name or policy_number or "sg-policy"
            path = rec.save_record(rec.MY_POLICIES, f"{insurer}-{stem}", rec.build_sg_markdown(data))
            st.success(f"Saved to `{path.relative_to(BASE_DIR)}`")
            st.balloons()

    with tab_view:
        render_record_browser(rec.MY_POLICIES, "No policies saved yet. Add one in the first tab.")


# =============================================================================
# Page: Parents' Policies (China) — Chinese fields
# =============================================================================
def page_parents_policies() -> None:
    st.title("🇨🇳 Parents' Policies — China")
    st.write("管理父母的中国互联网保险保单（关键字段中文）。Manage your parents' China policies.")

    tab_add, tab_view = st.tabs(["➕ 新增保单 Add", "📚 查看已保存 View"])

    with tab_add:
        st.subheader("方式 A：上传并自动解析 (Upload & Auto-Parse)")
        upload_and_parse(parsers.parse_cn_fields, key="cn")

        st.subheader("方式 B：保单表单 (Policy Form)")
        with st.form("cn_form"):
            c1, c2 = st.columns(2)
            with c1:
                nickname = st.text_input("保单昵称 Nickname", value=_pf("cn", "product_name"))
                policyholder = st.text_input("投保人 Policyholder")
                insured_person = st.text_input("被保险人 Insured", value=_pf("cn", "insured_person"))
                relationship = st.selectbox("与我关系 Relationship", ["父亲 Father", "母亲 Mother", "其他 Other"])
                insurer = st.text_input("保险公司 Insurer", value=_pf("cn", "insurer"))
                product_name = st.text_input("产品名称 Product", value=_pf("cn", "product_name"))
                policy_number = st.text_input("保单号 Policy No.", value=_pf("cn", "policy_number"))
            with c2:
                policy_type = st.selectbox(
                    "产品类型 Type",
                    ["", "百万医疗险", "重疾险", "意外险", "定期寿险", "终身寿险", "年金险", "防癌医疗险"],
                )
                status = st.selectbox("保单状态 Status", ["有效 In Force", "已失效 Lapsed", "已理赔 Claimed", "已到期 Matured"])
                sum_assured = st.text_input("保额 Sum Assured", value=_pf("cn", "sum_assured"))
                deductible = st.text_input("免赔额 Deductible", value=_pf("cn", "deductible"))

            st.markdown("**保障内容 Coverage（中国互联网保险特色字段）**")
            c3, c4 = st.columns(2)
            with c3:
                reimburse_in = st.text_input("社保内报销比例 In-Scheme %", value=_pf("cn", "reimburse_in"))
                reimburse_out = st.text_input("社保外报销比例 Out-of-Scheme %", value=_pf("cn", "reimburse_out"))
                guaranteed_renewal = st.text_input("保证续保年限 Guaranteed Renewal", value=_pf("cn", "guaranteed_renewal"))
            with c4:
                waiting_period = st.text_input("等待期 Waiting Period")

            st.markdown("**缴费信息 Premium & Payment**")
            c5, c6 = st.columns(2)
            with c5:
                premium = st.text_input("保费 Premium", value=_pf("cn", "premium"))
                frequency = st.selectbox("缴费频率 Frequency", ["年缴 Annual", "月缴 Monthly", "趸交 Single"])
                auto_renew = st.selectbox("是否自动续保 Auto-Renew", ["", "是 Yes", "否 No"])
            with c6:
                debit_account = st.text_input("自动续保扣款账户 Auto-Debit Account")
                next_due = st.text_input("下次缴费日 Next Due (YYYY-MM-DD)")

            st.markdown("**关键日期 Key Dates**")
            c7, c8 = st.columns(2)
            with c7:
                start_date = st.text_input("保险期间起 Start Date", value=_pf("cn", "start_date"))
            with c8:
                end_date = st.text_input("保险期间止 End Date")

            notes = st.text_area("备注 Notes")
            submitted = st.form_submit_button("💾 保存保单 Save")

        if submitted:
            data = dict(
                nickname=nickname, policyholder=policyholder, insured_person=insured_person,
                relationship=relationship, insurer=insurer, product_name=product_name,
                policy_number=policy_number, policy_type=policy_type, status=status,
                sum_assured=sum_assured, deductible=deductible, reimburse_in=reimburse_in,
                reimburse_out=reimburse_out, guaranteed_renewal=guaranteed_renewal,
                waiting_period=waiting_period, premium=premium, frequency=frequency,
                auto_renew=auto_renew, debit_account=debit_account, next_due=next_due,
                start_date=start_date, end_date=end_date, notes=notes,
            )
            stem = nickname or product_name or policy_number or "cn-policy"
            path = rec.save_record(rec.PARENTS_POLICIES, f"{insurer}-{stem}", rec.build_cn_markdown(data))
            st.success(f"已保存至 `{path.relative_to(BASE_DIR)}`")
            st.balloons()

    with tab_view:
        render_record_browser(rec.PARENTS_POLICIES, "暂无保单，请在第一个标签页新增。No policies yet.")


# =============================================================================
# Page: AIA Products
# =============================================================================
def page_aia_products() -> None:
    st.title("📘 AIA Products")
    st.write("Reference summaries of AIA products for advisory work.")
    render_record_browser(BASE_DIR / "aia_products", "No product summaries yet. See templates/aia_product_template.md.")


# =============================================================================
# Page: Client Profiles
# =============================================================================
def page_clients() -> None:
    st.title("👥 Client Profiles")
    st.warning("PDPA: client files hold personal data and are git-ignored. Do not commit real client data.")
    render_record_browser(BASE_DIR / "clients", "No client profiles yet. See templates/client_profile_template.md.")


# =============================================================================
# Router
# =============================================================================
PAGES = {
    "My Policies (Singapore)": page_my_policies,
    "Parents' Policies (China)": page_parents_policies,
    "AIA Products": page_aia_products,
    "Client Profiles": page_clients,
}


def main() -> None:
    st.sidebar.title("🛡️ Insurance Portal")
    choice = st.sidebar.radio("Navigation", list(PAGES.keys()))
    st.sidebar.markdown("---")
    st.sidebar.caption("Singapore policies in English · China policies with Chinese fields.")
    PAGES[choice]()


if __name__ == "__main__":
    main()
