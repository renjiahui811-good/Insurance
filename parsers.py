"""Text extraction and field parsing for uploaded policy documents.

Two stages:
  1. extract_text()  — pull raw text from an uploaded PDF or image.
  2. parse_sg_fields() / parse_cn_fields() — best-effort regex extraction of
     key fields for Singapore (English) and China (Chinese) policies.

All parsing is best-effort. Missing fields simply come back empty so the user
can fill them in via the manual form.
"""

from __future__ import annotations

import io
import re
from typing import Any

# --- Optional dependencies (degrade gracefully if unavailable) ---------------
try:
    from pypdf import PdfReader

    _HAS_PDF = True
except Exception:  # pragma: no cover
    _HAS_PDF = False

try:
    from PIL import Image
    import pytesseract

    _HAS_OCR = bool(pytesseract.get_languages())
except Exception:  # pragma: no cover
    _HAS_OCR = False


# =============================================================================
# Stage 1 — text extraction
# =============================================================================
def extract_text(file_bytes: bytes, filename: str, mime_type: str = "") -> tuple[str, str]:
    """Return (text, note). note explains any degradation to the user.

    Detects the file kind from the filename extension OR the MIME type — Google
    Drive files often have no extension in their title, so the MIME type is the
    reliable signal there.
    """
    name = (filename or "").lower()
    mime = (mime_type or "").lower()

    is_pdf = name.endswith(".pdf") or mime == "application/pdf"
    is_image = name.endswith((".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp")) or mime.startswith("image/")
    is_text = name.endswith((".txt", ".md")) or mime.startswith("text/")

    if is_pdf:
        if not _HAS_PDF:
            return "", "PDF support not installed (pypdf)."
        return _extract_pdf(file_bytes)

    if is_image:
        if not _HAS_OCR:
            return "", "Image OCR not available (tesseract not installed)."
        return _extract_image(file_bytes)

    if is_text:
        return file_bytes.decode("utf-8", errors="ignore"), ""

    return "", f"Unsupported file type: {filename} ({mime_type or 'unknown'})"


def _extract_pdf(file_bytes: bytes) -> tuple[str, str]:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
    except Exception as exc:  # pragma: no cover
        return "", f"Could not read PDF: {exc}"

    if not text:
        note = (
            "No embedded text found — this PDF is likely a scanned image. "
            "Try uploading it as an image (PNG/JPG) for OCR, or fill the form manually."
        )
        return "", note
    return text, ""


def _extract_image(file_bytes: bytes, lang: str = "eng+chi_sim") -> tuple[str, str]:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as exc:  # pragma: no cover
        return "", f"OCR failed: {exc}"
    if not text:
        return "", "OCR ran but found no readable text."
    return text, ""


# =============================================================================
# Stage 2 — field parsing helpers
# =============================================================================
def _first(patterns: list[str], text: str, flags: int = re.IGNORECASE) -> str:
    """Return the first capture group that matches any pattern."""
    for pat in patterns:
        m = re.search(pat, text, flags)
        if m:
            return m.group(1).strip(" :：.-")
    return ""


def _money(patterns: list[str], text: str) -> str:
    """Extract a monetary value and normalise thousands separators."""
    raw = _first(patterns, text)
    if not raw:
        return ""
    cleaned = re.sub(r"[,\s]", "", raw)
    return cleaned


# =============================================================================
# Singapore (English) parsing
# =============================================================================
def parse_sg_fields(text: str) -> dict[str, Any]:
    return {
        "insurer": _first(
            [r"\b(AIA|Prudential|Great Eastern|Income|NTUC Income|Manulife|Singlife|HSBC Life|Aviva)\b"],
            text,
        ),
        "product_name": _first([r"(?:Product Name|Plan Name|Plan)\s*[:\-]?\s*(.+)"], text),
        "policy_number": _first(
            [r"(?:Policy\s*(?:No|Number|#))\s*[:\-]?\s*([A-Z0-9\-/]+)"], text
        ),
        "policy_type": _first(
            [
                r"\b(Integrated Shield Plan|Whole Life|Term Life|Critical Illness|"
                r"Endowment|Investment-Linked|Personal Accident|Disability Income)\b"
            ],
            text,
        ),
        "life_assured": _first([r"(?:Life Assured|Insured Person|Life Insured)\s*[:\-]?\s*(.+)"], text),
        "sum_assured": _money(
            [r"(?:Sum Assured|Sum Insured|Coverage Amount)\s*[:\-]?\s*(?:S?\$)?\s*([\d,]+)"], text
        ),
        "premium": _money(
            [r"(?:Premium|Annual Premium|Premium Amount)\s*[:\-]?\s*(?:S?\$)?\s*([\d,]+(?:\.\d+)?)"], text
        ),
        "deductible": _money([r"Deductible\s*[:\-]?\s*(?:S?\$)?\s*([\d,]+)"], text),
        "co_insurance": _first([r"Co-?[Ii]nsurance\s*[:\-]?\s*([\d]+%?)"], text),
        "ward_class": _first([r"(?:Ward(?:\s*Class)?|Hospital Class)\s*[:\-]\s*(Private|B1|B2|C|A)\b"], text),
        "start_date": _first([r"(?:Policy Start|Commencement|Effective) Date\s*[:\-]?\s*([\d]{1,4}[\-/][\d]{1,2}[\-/][\d]{1,4})"], text),
    }


# =============================================================================
# China (Chinese) parsing
# =============================================================================
def parse_cn_fields(text: str) -> dict[str, Any]:
    return {
        "insurer": _first(
            [r"(众安|平安|太平洋|人保|泰康|水滴|微医|中国人寿|太平|阳光|复星联合|新华|友邦)[保险]*"],
            text,
        ),
        "product_name": _first([r"(?:产品名称|保险产品|计划名称)\s*[:：]?\s*(.+)"], text),
        "policy_number": _first([r"(?:保单号|保险单号|合同号)\s*[:：]?\s*([A-Z0-9\-]+)"], text),
        "policy_type": _first(
            [r"(百万医疗险|医疗险|重疾险|重大疾病保险|意外险|定期寿险|终身寿险|年金险|防癌医疗险)"],
            text,
        ),
        "insured_person": _first([r"(?:被保险人|被保人)\s*[:：]?\s*(.+)"], text),
        "sum_assured": _first([r"(?:保额|保险金额|基本保额)\s*[:：]?\s*([\d,]+\s*万?元?)"], text),
        "premium": _first([r"(?:保费|保险费|年缴保费|首年保费)\s*[:：]?\s*([\d,]+(?:\.\d+)?\s*元?)"], text),
        "deductible": _first([r"(?:免赔额|年免赔额)\s*[:：]?\s*([\d,]+\s*万?元?)"], text),
        "reimburse_in": _first([r"社保[内]?[报销]*(?:比例)?\s*[:：]?\s*([\d]+%)"], text),
        "reimburse_out": _first([r"社保外[报销]*(?:比例)?\s*[:：]?\s*([\d]+%)"], text),
        "guaranteed_renewal": _first([r"保证续保\s*[:：]?\s*([\d]+\s*年)"], text),
        "start_date": _first([r"(?:保险期间|生效日期|起保日期)\s*[:：]?\s*([\d]{4}[\-/年][\d]{1,2}[\-/月][\d]{1,2})"], text),
    }


CAPABILITIES = {
    "pdf": _HAS_PDF,
    "ocr": _HAS_OCR,
}
