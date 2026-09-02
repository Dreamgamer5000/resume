#!/usr/bin/env bash
set -e

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "Error: Version parameter is missing."
  echo "Usage: ./upload.sh <version> (e.g., ./upload.sh 3)"
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

# 2. rename files to versioned names
echo "Versioning files with tag: ${VERSION}..."
mv -f "2col/2col.pdf" "2col/Rejit_2col_${VERSION}.pdf"
mv -f "jakes_template_prope/main.pdf" "jakes_template_prope/Rejit_resume_${VERSION}.pdf"

echo "Generated / Updated:"
echo " - 2col/Rejit_2col_${VERSION}.pdf"
echo " - jakes_template_prope/Rejit_resume_${VERSION}.pdf"

# 3. Google Drive Upload
if [ -f "./upload_gdrive.py" ]; then
  ./upload_gdrive.py "${VERSION}"
fi

# 4. Git Operations
# Stage versioned PDFs and .gitignore without deleting other files
echo "Staging updated PDF files..."
git add .gitignore "2col/Rejit_2col_${VERSION}.pdf" "jakes_template_prope/Rejit_resume_${VERSION}.pdf"

git commit -m "Upload resume PDFs (version ${VERSION})" || echo "No changes to commit."

echo "Pushing PDFs to GitHub..."
git push origin main

echo "Done! Resume PDFs (version ${VERSION}) uploaded successfully."
