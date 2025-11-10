#!/bin/bash
# Build script for Railway - uses CPU-only PyTorch builds for faster installation

set -e

echo "Installing PyTorch CPU-only builds..."
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --no-cache-dir

echo "Installing remaining dependencies..."
pip install -r requirements.txt --no-cache-dir

echo "Build complete!"

