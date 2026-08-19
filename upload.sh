#!/usr/bin/env bash
set -e

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "Error: Version parameter is missing."
  echo "Usage: ./upload.sh <version> (e.g., ./upload.sh v3)"
  exit 1
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# 1. Verify build files exist; if missing, prompt user to run build.sh
if [ ! -f "jakes_template_prope/main.pdf" ] || [ ! -f "2col/2col.pdf" ]; then
  echo "Error: Compiled PDFs not found."
  echo "Please run ./build.sh first before uploading."
  exit 1
fi

# 2. Rename in-place in respective folders (removes original main.pdf & 2col.pdf)
echo "Versioning files with tag: ${VERSION}..."
mv -f "2col/2col.pdf" "2col/Rejit_2col_${VERSION}.pdf"
mv -f "jakes_template_prope/main.pdf" "jakes_template_prope/Rejit_resume_${VERSION}.pdf"

echo "Generated / Updated:"
echo " - 2col/Rejit_2col_${VERSION}.pdf"
echo " - jakes_template_prope/Rejit_resume_${VERSION}.pdf"

# 3. Git Operations
if [ ! -d ".git" ]; then
  echo "Initializing git repository..."
  git init
  git branch -M main
fi

# Ensure remote exists
if ! git remote | grep -q "^origin$"; then
  echo "Adding remote origin dreamgamer5000/resume..."
  git remote add origin https://github.com/dreamgamer5000/resume.git
fi

echo "Staging and committing files..."
git add .
git commit -m "Update resume version ${VERSION}" || echo "No new changes to commit."

echo "Pushing to GitHub (dreamgamer5000/resume)..."
git push -u origin main

echo "Done! Version ${VERSION} uploaded successfully."
