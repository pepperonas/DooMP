#!/usr/bin/env python3
"""
DooMP Cross-Platform Packaging Script
====================================
This script creates a distributable package that can be run on any platform
with Python installed. It includes all necessary files and a launcher script.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
import zipfile

# Game details
GAME_NAME = "DooMP"
GAME_VERSION = "1.0"
MAIN_SCRIPT = "main.py"
REQUIREMENTS = "requirements.txt"
ASSETS = []  # Add asset files like shot.wav if needed

# Output directory
DIST_DIR = "dist"
PACKAGE_DIR = os.path.join(DIST_DIR, f"{GAME_NAME}-{GAME_VERSION}")

def clean_directory():
    """Clean the output directory."""
    if os.path.exists(PACKAGE_DIR):
        print(f"Cleaning up {PACKAGE_DIR}...")
        shutil.rmtree(PACKAGE_DIR)
    os.makedirs(PACKAGE_DIR, exist_ok=True)

def copy_game_files():
    """Copy the game files to the package directory."""
    # Copy main script
    print(f"Copying {MAIN_SCRIPT}...")
    shutil.copy2(MAIN_SCRIPT, PACKAGE_DIR)
    
    # Copy requirements
    if os.path.exists(REQUIREMENTS):
        print(f"Copying {REQUIREMENTS}...")
        shutil.copy2(REQUIREMENTS, PACKAGE_DIR)
    
    # Copy assets
    for asset in ASSETS:
        if os.path.exists(asset):
            print(f"Copying asset: {asset}")
            shutil.copy2(asset, PACKAGE_DIR)
    
    # Copy README if exists
    if os.path.exists("README.md"):
        print("Copying README.md...")
        shutil.copy2("README.md", PACKAGE_DIR)

def create_launcher_scripts():
    """Create launcher scripts for different platforms."""
    # Windows batch file
    print("Creating Windows launcher...")
    with open(os.path.join(PACKAGE_DIR, "play_game.bat"), 'w') as f:
        f.write('@echo off\n')
        f.write('echo Starting DooMP...\n')
        f.write('echo If Python is not installed, please install it from python.org\n')
        f.write('python -m pip install -r requirements.txt\n')
        f.write('python main.py\n')
        f.write('pause\n')
    
    # macOS/Linux shell script
    print("Creating macOS/Linux launcher...")
    with open(os.path.join(PACKAGE_DIR, "play_game.sh"), 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('echo "Starting DooMP..."\n')
        f.write('echo "If Python is not installed, please install it from python.org"\n')
        f.write('python3 -m pip install -r requirements.txt\n')
        f.write('python3 main.py\n')
    
    # Make the shell script executable
    os.chmod(os.path.join(PACKAGE_DIR, "play_game.sh"), 0o755)
    
    # Create a simple README for the package
    with open(os.path.join(PACKAGE_DIR, "HOW_TO_PLAY.txt"), 'w') as f:
        f.write(f"{GAME_NAME} v{GAME_VERSION}\n")
        f.write("=" * 30 + "\n\n")
        f.write("HOW TO PLAY:\n\n")
        f.write("Windows:\n")
        f.write("1. Double-click play_game.bat\n\n")
        f.write("macOS/Linux:\n")
        f.write("1. Open Terminal in this directory\n")
        f.write("2. Run: chmod +x play_game.sh\n")
        f.write("3. Run: ./play_game.sh\n\n")
        f.write("Requirements:\n")
        f.write("- Python 3.7 or later must be installed\n")
        f.write("- The script will install pygame and numpy automatically\n")

def create_zip_archive():
    """Create a ZIP archive of the package."""
    zip_filename = os.path.join(DIST_DIR, f"{GAME_NAME}-{GAME_VERSION}.zip")
    print(f"Creating ZIP archive: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(PACKAGE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, DIST_DIR))
    
    print(f"ZIP archive created: {zip_filename}")
    return zip_filename

def main():
    """Main function."""
    print(f"Packaging {GAME_NAME} v{GAME_VERSION} for distribution...")
    
    # Ensure dist directory exists
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # Clean package directory
    clean_directory()
    
    # Copy game files
    copy_game_files()
    
    # Create launcher scripts
    create_launcher_scripts()
    
    # Create ZIP archive
    zip_file = create_zip_archive()
    
    print("\nPackaging complete!")
    print(f"The package has been created at: {zip_file}")
    print("This ZIP file can be distributed and run on any platform with Python installed.")

if __name__ == "__main__":
    main()