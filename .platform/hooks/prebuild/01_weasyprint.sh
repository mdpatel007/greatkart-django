#!/bin/bash
set -e

echo "Installing WeasyPrint system dependencies..."

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

echo "System dependencies installed ✅"
