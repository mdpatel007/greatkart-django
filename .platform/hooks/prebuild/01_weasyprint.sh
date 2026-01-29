#!/bin/bash
echo "Installing WeasyPrint system dependencies..."

sudo dnf install -y \
  cairo \
  pango \
  gdk-pixbuf2 \
  libffi \
  freetype \
  harfbuzz \
  fontconfig \
  libjpeg-turbo \
  zlib
