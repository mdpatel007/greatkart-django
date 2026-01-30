#!/bin/bash
set -e

echo "Installing WeasyPrint dependencies..."

sudo dnf install -y \
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

echo "System libraries installed successfully ✅"

echo "Installing WeasyPrint Python package..."

source /var/app/venv/*/bin/activate
pip install --upgrade pip
pip install weasyprint

echo "WeasyPrint installed successfully ✅"
