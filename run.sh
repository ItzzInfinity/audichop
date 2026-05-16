#!/bin/bash
# Quick start script for Audio File Splitter

echo "=========================================="
echo "  Audio File Splitter - Setup"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ Warning: ffmpeg is not installed."
    echo "  Install with: sudo apt-get install ffmpeg (Ubuntu/Debian)"
    echo "               brew install ffmpeg (macOS)"
    echo ""
fi

# Install dependencies
echo "Installing Python dependencies..."
python3 -m pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"
echo ""

# Use intelligent launcher that tries multiple strategies
echo "=========================================="
echo "  Starting Audio File Splitter..."
echo "=========================================="
echo ""

python3 launch.py "$@"
exit_code=$?

exit $exit_code
