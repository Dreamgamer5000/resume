# Automated Resume Pipeline: LaTeX Build, Git Versioning & Google Drive Sync

An automated resume compilation and distribution pipeline designed for LaTeX resumes. It compiles ATS-friendly and modern two-column templates, manages versioned snapshots in Git, and syncs updates to **Google Drive while preserving the exact same shareable link across every revision**.

---

## 📁 Architecture & File Layout

```text
├── 2col/                       # Modern 2-Column LaTeX resume template
├── jakes_template_prope/       # ATS-friendly Single Column LaTeX template
├── template/                   # Sanitized starter templates (Single Column & 2-Column)
│   ├── 2col/                   # Clean 2-column template ready to customize
│   └── jakes_template/         # Clean single-column template ready to customize
├── build.sh                    # Compiles both LaTeX resumes locally
├── upload.sh                   # Versions PDFs, syncs with Google Drive & pushes to Git
├── upload_gdrive.py            # Link-preserving Google Drive upload logic
├── requirements.txt            # Python dependencies for Google Drive API
├── .env.example                # Environment variables template
├── .env                        # Local credentials config (NEVER COMMITTED)
├── client_secret.json          # Google OAuth Desktop client secret (NEVER COMMITTED)
└── token.json                  # Auto-generated OAuth refresh token (NEVER COMMITTED)
```

---

## 🚀 Quick Start Guide

### Step 1: Install Prerequisites

Make sure you have a TeX distribution and Python 3.10+ installed:

```bash
# Arch Linux
sudo pacman -S texlive-meta python

# Ubuntu / Debian
sudo apt install texlive-latex-extra texlive-fonts-recommended python3 python3-venv
```

---

### Step 2: Choose Your Template

You can build on the existing templates or start fresh using the sanitized templates in `template/`:

* **Single Column (ATS-friendly):** Located in `jakes_template_prope/main.tex` (or `template/jakes_template/main.tex`)
* **2-Column (Modern Visual Layout):** Located in `2col/2col.tex` (or `template/2col/2col.tex`)

---

### Step 3: Set Up Python Virtual Environment

From the root directory:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate and install dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Step 4: Configure Google Cloud & OAuth (One-Time Setup)

To allow the upload script to save files directly into your personal Google Drive (without hitting service account storage quota errors), set up an **OAuth 2.0 Desktop Client**:

1. Open [Google Cloud Console](https://console.cloud.google.com/) and create a project (e.g. `Resume-Pipeline`).
2. **Enable the Google Drive API**:
   * Go to **APIs & Services** > **Library**.
   * Search for **Google Drive API** and click **ENABLE**.
3. **Configure OAuth Consent Screen**:
   * Go to **APIs & Services** > **OAuth consent screen**.
   * Select **External** and click **Create**.
   * Fill in **App Name** (e.g. `Resume Uploader`), your **Support Email**, and your **Developer Email**.
   * On the **Test users** page, click **+ ADD USERS**, enter your Google email, and save.
   * *(Recommended)* Under Publishing status on the OAuth Consent Screen dashboard, click **PUBLISH APP** so your login session remains permanent.
4. **Create Desktop Client ID**:
   * Go to **APIs & Services** > **Credentials**.
   * Click **+ CREATE CREDENTIALS** > **OAuth client ID**.
   * Choose **Desktop app** as the Application type.
   * Click **Create**, then click **DOWNLOAD JSON**.
5. Save the downloaded JSON file in the project root as `client_secret.json`:
   ```bash
   cp ~/Downloads/client_secret_*.json ./client_secret.json
   ```

---

### Step 5: Configure `.env`

1. Create a dedicated folder in your Google Drive (e.g. `Resumes`).
2. Copy the folder ID from your browser's address bar:
   ```text
   https://drive.google.com/drive/folders/<YOUR_FOLDER_ID>
   ```
3. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
4. Add your folder ID:
   ```env
   GDRIVE_FOLDER_ID="your_google_drive_folder_id_here"
   GDRIVE_OAUTH_CLIENT_SECRET="client_secret.json"
   ```

---

## 🛠️ Everyday Workflow

Whenever you edit your resume `.tex` files:

### 1. Compile Resumes Locally
```bash
./build.sh
```
This compiles both templates into:
* `jakes_template_prope/main.pdf`
* `2col/2col.pdf`

Review the PDFs locally to ensure formatting and single-page alignment look perfect.

### 2. Version, Sync to Google Drive & Push to Git
```bash
./upload.sh <version_number>
```
*Example:*
```bash
./upload.sh 2
```

**What `./upload.sh` does automatically:**
1. Verifies that fresh PDFs were built by `build.sh`.
2. Creates versioned copies of your resumes locally.
3. Invokes `./upload_gdrive.py <version>`:
   * Searches your Google Drive folder for an existing file matching that name.
   * If found, **updates the file in place** using Google Drive's revision API. **The shareable URL never changes!**
   * If not found, creates the file and outputs the permanent shareable link.
4. Stages the versioned PDFs in Git and pushes to your remote repository.

---

## 🔒 Security & Privacy

The following files contain private tokens and credentials and are **strictly excluded** from Git via `.gitignore`:

* `.env` — Contains your private Google Drive Folder ID.
* `client_secret.json` — Google OAuth client secrets.
* `token.json` — Auto-generated OAuth refresh and access tokens.
* `.venv/` — Local virtual environment.

