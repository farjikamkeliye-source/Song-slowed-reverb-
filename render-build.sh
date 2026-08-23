#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Download ffmpeg static build for Linux
if [ ! -f "ffmpeg" ]; then
  echo "Downloading ffmpeg..."
  curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -o ffmpeg.tar.xz
  tar -xf ffmpeg.tar.xz
  # Move binaries to a folder in PATH or local directory
  cp ffmpeg-master-latest-linux64-gpl/bin/ffmpeg .
  cp ffmpeg-master-latest-linux64-gpl/bin/ffprobe .
  rm -rf ffmpeg.tar.xz ffmpeg-master-latest-linux64-gpl
  echo "FFmpeg installed successfully!"
fi

