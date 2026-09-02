#!/usr/bin/env bash
# Wrapper to run with .venv python if available, otherwise system python3
""":"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$BASE_DIR/.venv/bin/python3" ]; then
    exec "$BASE_DIR/.venv/bin/python3" "$0" "$@"
else
    exec python3 "$0" "$@"
fi
"""

import os
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parent

# drive.file gives full read/write access to files created or opened by this app
SCOPES = ["https://www.googleapis.com/auth/drive"]

def load_env():
    """Finds and parses .env key-value pairs from the project root."""
    env_path = BASE_DIR / ".env"
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip().strip("'\"")
    return env_vars

def get_credentials(env_vars):
    """Obtains credentials via OAuth (preferred for personal Drive) or Service Account."""
    token_path = BASE_DIR / "token.json"
    oauth_secret_name = env_vars.get("GDRIVE_OAUTH_CLIENT_SECRET", "client_secret.json")
    oauth_secret_path = BASE_DIR / oauth_secret_name

    # 1. OAuth flow (supports personal Google Drive without quota issues)
    if token_path.exists() or oauth_secret_path.exists():
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not oauth_secret_path.exists():
                    print(f"❌ Error: {oauth_secret_name} not found in {BASE_DIR}.")
                    print("Please download your OAuth Desktop Client ID JSON from Google Cloud Console.")
                    sys.exit(1)
                print("\nInitiating one-time Google authentication in your browser...")
                flow = InstalledAppFlow.from_client_secrets_file(str(oauth_secret_path), SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return creds

    # 2. Fallback to Service Account (for Google Workspace Shared Drives)
    creds_file_name = env_vars.get("GDRIVE_CREDENTIALS_FILE")
    if creds_file_name:
        creds_path = BASE_DIR / creds_file_name
        if creds_path.exists():
            return service_account.Credentials.from_service_account_file(
                str(creds_path),
                scopes=SCOPES
            )

    print("❌ Error: No valid credentials found.")
    print("Please place 'client_secret.json' in the project root or configure .env.")
    sys.exit(1)

def upload_file_to_drive(service, folder_id: str, local_path: Path, remote_name: str):
    """Uploads or updates a file in Google Drive, preserving file ID and webViewLink."""
    if not local_path.exists():
        print(f"❌ Error: Local file not found: {local_path}")
        return None

    media = MediaFileUpload(str(local_path), mimetype="application/pdf", resumable=True)

    # Search if a file with this name already exists in target folder
    query = f"'{folder_id}' in parents and name = '{remote_name}' and trashed = false"
    response = service.files().list(
        q=query,
        spaces="drive",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        fields="files(id, name, webViewLink)"
    ).execute()
    files = response.get("files", [])

    if files:
        file_id = files[0]["id"]
        updated_file = service.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True,
            fields="id, name, webViewLink"
        ).execute()
        print(f"✅ Updated existing file: {remote_name}")
        print(f"   Link: {updated_file.get('webViewLink')}")
        return updated_file
    else:
        file_metadata = {
            "name": remote_name,
            "parents": [folder_id]
        }
        created_file = service.files().create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True,
            fields="id, name, webViewLink"
        ).execute()
        print(f"✅ Created new file: {remote_name}")
        print(f"   Link: {created_file.get('webViewLink')}")
        return created_file

def main():
    if len(sys.argv) < 2:
        print("Usage: ./upload_gdrive.py <version> (e.g., ./upload_gdrive.py 2)")
        sys.exit(1)

    version = sys.argv[1].strip()
    env_vars = load_env()
    folder_id = env_vars.get("GDRIVE_FOLDER_ID")

    if not folder_id:
        print("❌ Error: GDRIVE_FOLDER_ID not found in .env")
        print("Please copy .env.example to .env and set your folder ID.")
        sys.exit(1)

    try:
        credentials = get_credentials(env_vars)
        service = build("drive", "v3", credentials=credentials)

        files_to_upload = [
            (
                BASE_DIR / "jakes_template_prope" / f"Rejit_resume_{version}.pdf",
                f"Rejit_resume_{version}.pdf"
            ),
            (
                BASE_DIR / "2col" / f"Rejit_2col_{version}.pdf",
                f"Rejit_2col_{version}.pdf"
            ),
        ]

        print(f"\nUploading version {version} PDFs to Google Drive...")
        for local_file, remote_name in files_to_upload:
            upload_file_to_drive(service, folder_id, local_file, remote_name)

        print("\nAll files processed successfully.")

    except HttpError as err:
        print(f"\n❌ Google Drive API Error: {err}")
        if "storageQuotaExceeded" in str(err) or "Service Accounts do not have storage quota" in str(err):
            print("\n💡 Tip: Use an OAuth Desktop Client ID (client_secret.json) instead of a Service Account.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
