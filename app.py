"""Personal Insurance Portal — Streamlit app.

Browse and read the Markdown records under this repository:
  - My Policies
  - Parents' Policies
  - AIA Products
  - Clients
  - Knowledge

The UI is in English. Records are plain Markdown files, so they can be
edited in any text editor and read directly on GitHub.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

SECTIONS = {
    "My Policies": BASE_DIR / "my_policies",
    "Parents' Policies": BASE_DIR / "parents_policies",
    "AIA Products": BASE_DIR / "aia_products",
    "Clients": BASE_DIR / "clients",
    "Knowledge": BASE_DIR / "knowledge",
}


def list_records(folder: Path) -> list[Path]:
    """Return Markdown files in a folder, README/templates last."""
    if not folder.exists():
        return []
    files = sorted(folder.glob("*.md"))
    records = [f for f in files if not f.name.startswith(("_", "README"))]
    others = [f for f in files if f.name.startswith(("_", "README"))]
    return records + others


def pretty_name(path: Path) -> str:
    if path.name.startswith("_"):
        return f"📄 {path.stem.lstrip('_')} (template)"
    if path.name == "README.md":
        return "ℹ️ README"
    return f"📝 {path.stem}"


def main() -> None:
    st.set_page_config(page_title="Personal Insurance Portal", page_icon="🛡️", layout="wide")

    st.sidebar.title("🛡️ Insurance Portal")
    section = st.sidebar.radio("Section", list(SECTIONS.keys()))

    folder = SECTIONS[section]
    records = list_records(folder)

    st.sidebar.markdown("---")
    if not records:
        st.sidebar.info("No records yet. Copy a template to get started.")
        selected = None
    else:
        selected = st.sidebar.selectbox(
            "Record",
            records,
            format_func=pretty_name,
        )

    st.title(section)

    if selected is None:
        st.info(
            f"No Markdown records found in `{folder.name}/`.\n\n"
            "Copy the template file in that folder to create your first record."
        )
        return

    st.caption(f"Source: `{selected.relative_to(BASE_DIR)}`")
    st.markdown(selected.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
