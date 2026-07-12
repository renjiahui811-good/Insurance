# Personal Insurance Portal

A lightweight portal to manage and understand insurance policies — built with
Python + Streamlit. Designed for the Singapore market (Integrated Shield Plans,
Critical Illness, Life, Endowment, ILP, etc.).

## Purpose

1. Manage and understand **my own** policies.
2. Manage and understand **my parents'** policies.
3. Support **AIA advisory** work — insurance knowledge, AIA product summaries,
   and (future) client profiles and plan management.

## Sections

The portal has four sections in the sidebar:

| Section | Language | Notes |
|---------|----------|-------|
| **My Policies (Singapore)** | English | Integrated Shield Plan, Medisave Pay, Co-insurance, Deductible, TPD, CI… |
| **Parents' Policies (China)** | Chinese fields | 百万医疗险、免赔额、社保内/外报销比例、保证续保年限、自动续保扣款账户… |
| **AIA Products** | English | Advisory product summaries |
| **Client Profiles** | English | Advisory client records (PDPA — git-ignored) |

## Data entry (two ways)

On both policy pages you can add a record two ways:

- **A. Upload & Auto-Parse** — upload a policy **PDF** (embedded text) or an
  **image** (PNG/JPG, read via OCR). The app extracts the text and best-effort
  parses key fields, which pre-fill the form. Singapore uses English patterns;
  China uses Chinese patterns (`eng+chi_sim` OCR).
- **B. Policy Form** — review/adjust anything parsing missed, then save. The
  record is written as a Markdown file (English for SG, Chinese fields for CN).

## Structure

```
Insurance/
├── app.py                  # Streamlit portal (4 sections, upload + forms)
├── parsers.py              # PDF/image text extraction + field parsing
├── records.py              # Markdown builders + save/list
├── requirements.txt
├── my_policies/            # Singapore policies (English, one .md per policy)
├── parents_policies/       # China policies (Chinese fields)
├── aia_products/           # AIA product summaries (advisory)
├── clients/                # Client profiles (PDPA — git-ignored)
├── knowledge/              # Glossary & insurance notes
├── templates/              # Master Markdown templates
└── data/                   # Local working data (git-ignored)
```

Each record is a plain Markdown file — editable in any editor and readable on
GitHub.

## Templates

| Template | Use |
|----------|-----|
| `templates/personal_policy_template.md` | Your own & parents' policies |
| `templates/aia_product_template.md` | AIA product summaries |
| `templates/client_profile_template.md` | Client profiles |

Each working folder also contains a copy of its template (prefixed with `_`).
To add a record, copy the template to a new file and fill it in.

## Run the portal

```bash
pip install -r requirements.txt

# For image OCR (optional, needed only to read scanned/photo policies):
sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim

streamlit run app.py
```

The app opens in your browser. Use the sidebar to pick a section. PDF parsing
works with `pypdf` alone; image OCR additionally needs the `tesseract` binary.
The app degrades gracefully and tells you which parsers are available.

## Deploy online (Streamlit Community Cloud)

The repo is ready to deploy at [share.streamlit.io](https://share.streamlit.io):

1. Sign in with GitHub and pick this repo + branch, main file `app.py`.
2. `requirements.txt` (Python deps) and `packages.txt` (`tesseract-ocr`,
   `tesseract-ocr-chi-sim` for OCR) are installed automatically.
3. Set the app to **private** so only you can view it.

> ⚠️ **Persistence note:** the Community Cloud filesystem is ephemeral, so
> policies saved through the deployed app are **temporary** and lost on
> restart/redeploy. For permanent records, run the app locally (data stays on
> your machine) or commit records to the repo.

## Privacy (PDPA)

The `clients/` folder holds personal data and is git-ignored (except the
template and README). Do not commit real client information. Record PDPA consent
before storing any personal data.
