#!/bin/bash
set -e

echo "Installing WeasyPrint dependencies (Amazon Linux 2023)..."

dnf install -y \
  cairo \
  pango \
  gdk-pixbuf2 \
  libffi \
  freetype \
  harfbuzz \
  fribidi \
  fontconfig \
  libjpeg-turbo \
  zlib \
  libxml2 \
  libxslt

echo "Installing WeasyPrint Python package..."
source /var/app/venv/*/bin/activate
pip install --upgrade weasyprint

echo "WeasyPrint install complete ✅"
