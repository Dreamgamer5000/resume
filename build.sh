#!/usr/bin/env bash
set -e

echo "Compiling resumes..."
(cd jakes_template_prope && pdflatex -interaction=nonstopmode main.tex > /dev/null)
(cd 2col && pdflatex -interaction=nonstopmode 2col.tex > /dev/null)
echo "Done."
