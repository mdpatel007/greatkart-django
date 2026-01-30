#!/bin/bash
set -e

echo "Installing full WeasyPrint dependencies..."

dnf install -y \
  cairo \
  pango \
  pangocairo \
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

echo "WeasyPrint dependencies installed successfully ✅"
