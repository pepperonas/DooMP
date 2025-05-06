#!/bin/bash
# Script to build Windows executable for DooMP using Wine on macOS/Linux

echo "Starting Windows build using Wine..."
echo "This will create a Windows executable using Wine."

# Check if Wine is available
if ! command -v wine &> /dev/null; then
    echo "Error: Wine is not installed or not in PATH."
    echo "To install Wine on macOS:"
    echo "  brew install --cask wine-stable"
    echo "To install Wine on Ubuntu/Debian:"
    echo "  sudo apt-get install wine"
    exit 1
fi

# Create a temporary directory for the Wine environment
WINE_DIR="wine_env"
mkdir -p "$WINE_DIR"

echo "Setting up Wine Python environment..."
PYTHON_EXE="python-3.10.11-amd64.exe"
PYTHON_URL="https://www.python.org/ftp/python/3.10.11/$PYTHON_EXE"

# Download Python installer if not already present
if [ ! -f "$WINE_DIR/$PYTHON_EXE" ]; then
    echo "Downloading Windows Python installer..."
    curl -L "$PYTHON_URL" -o "$WINE_DIR/$PYTHON_EXE"
fi

# Install Python in Wine
echo "Installing Python in Wine (this will take a while)..."
cd "$WINE_DIR"
wine "$PYTHON_EXE" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
cd ..

echo "Installing required packages..."
wine python -m pip install pygame numpy pyinstaller

# Copy game files to Wine directory
echo "Copying game files..."
cp main.py "$WINE_DIR/"
cp requirements.txt "$WINE_DIR/"

# Build the executable
echo "Building Windows executable..."
cd "$WINE_DIR"
wine python -m PyInstaller --onefile --windowed --name DooMP-1.0-win64 main.py
cd ..

# Copy the executable to dist directory
echo "Copying the executable to dist directory..."
mkdir -p dist
cp "$WINE_DIR/dist/DooMP-1.0-win64.exe" dist/

echo "Clean up? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Cleaning up Wine environment..."
    rm -rf "$WINE_DIR"
fi

if [ -f "./dist/DooMP-1.0-win64.exe" ]; then
    echo "Build successful! Windows executable is available at: ./dist/DooMP-1.0-win64.exe"
else
    echo "Error: Build failed or executable not found."
    exit 1
fi