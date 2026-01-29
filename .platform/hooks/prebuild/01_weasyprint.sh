#!/bin/bash
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
  redhat-rpm-config \
  gcc \
  python3-devel
