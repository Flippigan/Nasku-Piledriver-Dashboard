#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Building executable..."
pyinstaller build.spec --clean

echo "Build complete! Executable at: dist/InverterTracker"
