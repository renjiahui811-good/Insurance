"""Google Drive integration (service-account based).

Setup: a Google Cloud service account with the Drive API enabled. The user
shares one Drive folder ("Insurance Inbox") with the service account's email.
The app then lists and downloads files from that folder.

Configuration lives in Streamlit secrets:
  - st.secrets["gcp_service_account"]  -> the service account JSON (as a table)
  - st.secrets["gdrive_folder_id"]     -> the shared folder's ID

Everything degrades gracefully: if the libraries or secrets are missing, the
Drive option simply hides and the device upload keeps working.
"""

from __future__ import annotations

import io
from typing import Any

import streamlit as st

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload

    _HAS_GDRIVE = True
except Exception:  # pragma: no cover
    _HAS_GDRIVE = False

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# File types the parser can handle.
SUPPORTED_MIME_PREFIXES = ("application/pdf", "image/", "text/")


def is_available() -> bool:
    """True if the Google client libraries are installed."""
    return _HAS_GDRIVE


def is_configured() -> bool:
    """True if libraries are present AND secrets are set."""
    if not _HAS_GDRIVE:
        return False
    try:
        return "gcp_service_account" in st.secrets and "gdrive_folder_id" in st.secrets
    except Exception:
        return False


@st.cache_resource(show_spinner=False)
def _service():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def service_account_email() -> str:
    try:
        return st.secrets["gcp_service_account"].get("client_email", "")
    except Exception:
        return ""


def list_files(folder_id: str | None = None) -> list[dict[str, Any]]:
    """List non-trashed, parseable files in the shared folder (newest first)."""
    folder_id = folder_id or st.secrets["gdrive_folder_id"]
    service = _service()
    query = f"'{folder_id}' in parents and trashed = false"
    resp = (
        service.files()
        .list(
            q=query,
            fields="files(id, name, mimeType, modifiedTime)",
            orderBy="modifiedTime desc",
            pageSize=200,
        )
        .execute()
    )
    files = resp.get("files", [])
    return [f for f in files if f.get("mimeType", "").startswith(SUPPORTED_MIME_PREFIXES)]


def download_file(file_id: str) -> bytes:
    """Download a binary file's bytes from Drive."""
    service = _service()
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()
