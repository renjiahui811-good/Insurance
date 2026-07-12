# Personal Insurance Portal

A lightweight portal to manage and understand insurance policies — built with
Python + Streamlit. Designed for the Singapore market (Integrated Shield Plans,
Critical Illness, Life, Endowment, ILP, etc.).

## Purpose

1. Manage and understand **my own** policies.
2. Manage and understand **my parents'** policies.
3. Support **AIA advisory** work — insurance knowledge, AIA product summaries,
   and (future) client profiles and plan management.

## Structure

```
Insurance/
├── app.py                  # Streamlit portal (English UI)
├── requirements.txt
├── my_policies/            # My own policies (one .md per policy)
├── parents_policies/       # Parents' policies
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
streamlit run app.py
```

The app opens in your browser. Use the sidebar to pick a section and a record.

## Privacy (PDPA)

The `clients/` folder holds personal data and is git-ignored (except the
template and README). Do not commit real client information. Record PDPA consent
before storing any personal data.
