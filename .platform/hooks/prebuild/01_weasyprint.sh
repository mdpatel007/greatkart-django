#!/bin/bash
set -e

echo "Installing missing WeasyPrint system libraries..."

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
  pangocairo \
  libxml2 \
  libxslt

echo "WeasyPrint full dependencies installed successfully."