#!/usr/bin/env python3
"""
DooMP Deployment Script
=======================
This script packages the DooMP game for Windows, macOS, and Linux platforms.
It automates the creation of standalone executables using PyInstaller.

Usage:
    python deploy.py [platform]

Where [platform] is one of:
    - all     (builds for all platforms if possible)
    - windows (builds for Windows)
    - macos   (builds for macOS)
    - linux   (builds for Linux)

If no platform is specified, the script detects and builds for the current platform.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Game details
GAME_NAME = "DooMP"
GAME_VERSION = "1.0"
MAIN_SCRIPT = "main.py"
REQUIREMENTS = "requirements.txt"
ASSETS = []  # Add asset files here as needed (like 'shot.wav' if present)
ICON_FILE = None  # Set this to the path of your icon file if you have one

# Directory structure
BUILD_DIR = "build"
DIST_DIR = "dist"

def get_platform():
    """Detect the current platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        print(f"Unknown platform: {system}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Install project requirements
    if os.path.exists(REQUIREMENTS):
        print(f"Installing requirements from {REQUIREMENTS}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS], check=True)

def cleanup():
    """Clean up build directories."""
    for directory in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(directory):
            print(f"Cleaning up {directory}...")
            shutil.rmtree(directory)

def prepare_assets(target_dir):
    """Copy asset files to the target directory."""
    for asset in ASSETS:
        if os.path.exists(asset):
            print(f"Copying asset: {asset}")
            shutil.copy2(asset, target_dir)
        else:
            print(f"Warning: Asset file not found: {asset}")

def build_windows():
    """Build for Windows."""
    print("\n" + "="*40)
    print(f"Building {GAME_NAME} for Windows")
    print("="*40)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", f"{GAME_NAME}-{GAME_VERSION}-win64",
        "--clean",
    ]
    
    # Add icon if available
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
    
    # Add the main script
    cmd.append(MAIN_SCRIPT)
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)
    
    # Copy assets
    prepare_assets(os.path.join(DIST_DIR))
    
    print(f"Windows build completed: {os.path.join(DIST_DIR, f'{GAME_NAME}-{GAME_VERSION}-win64.exe')}")
    return True

def build_macos():
    """Build for macOS."""
    print("\n" + "="*40)
    print(f"Building {GAME_NAME} for macOS")
    print("="*40)
    
    # Create .app bundle
    cmd = [
        "pyinstaller",
        "--windowed",
        "--name", f"{GAME_NAME}-{GAME_VERSION}-macos",
        "--clean",
    ]
    
    # Add icon if available
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
    
    # Add the main script
    cmd.append(MAIN_SCRIPT)
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)
    
    # Copy assets
    app_dir = os.path.join(DIST_DIR, f"{GAME_NAME}-{GAME_VERSION}-macos.app", "Contents", "Resources")
    prepare_assets(app_dir)
    
    # Create a DMG (if hdiutil is available - macOS only)
    if shutil.which("hdiutil") and platform.system() == "Darwin":
        dmg_name = f"{GAME_NAME}-{GAME_VERSION}-macos.dmg"
        print(f"Creating DMG: {dmg_name}")
        try:
            subprocess.run([
                "hdiutil", "create",
                "-volname", GAME_NAME,
                "-srcfolder", os.path.join(DIST_DIR, f"{GAME_NAME}-{GAME_VERSION}-macos.app"),
                "-ov", "-format", "UDZO",
                os.path.join(DIST_DIR, dmg_name)
            ], check=True)
            print(f"DMG created: {os.path.join(DIST_DIR, dmg_name)}")
        except subprocess.CalledProcessError:
            print("Warning: Failed to create DMG file")
    
    print(f"macOS build completed: {os.path.join(DIST_DIR, f'{GAME_NAME}-{GAME_VERSION}-macos.app')}")
    return True

def build_linux():
    """Build for Linux."""
    print("\n" + "="*40)
    print(f"Building {GAME_NAME} for Linux")
    print("="*40)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", f"{GAME_NAME}-{GAME_VERSION}-linux",
        "--clean",
    ]
    
    # Add icon if available
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
    
    # Add the main script
    cmd.append(MAIN_SCRIPT)
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)
    
    # Copy assets
    prepare_assets(os.path.join(DIST_DIR))
    
    # Create .desktop file
    desktop_file = os.path.join(DIST_DIR, f"{GAME_NAME}.desktop")
    with open(desktop_file, 'w') as f:
        f.write(f"""[Desktop Entry]
Type=Application
Name={GAME_NAME}
Exec={os.path.join('.', f'{GAME_NAME}-{GAME_VERSION}-linux')}
Icon={ICON_FILE if ICON_FILE else ''}
Comment=A Raycasting 3D Game
Categories=Game;
""")
    
    # Make the binary and desktop file executable
    binary_path = os.path.join(DIST_DIR, f"{GAME_NAME}-{GAME_VERSION}-linux")
    if os.path.exists(binary_path):
        os.chmod(binary_path, 0o755)
    os.chmod(desktop_file, 0o755)
    
    # Create a tar.gz archive
    archive_name = f"{GAME_NAME}-{GAME_VERSION}-linux.tar.gz"
    print(f"Creating archive: {archive_name}")
    
    orig_dir = os.getcwd()
    os.chdir(DIST_DIR)
    try:
        subprocess.run([
            "tar", "-czf", archive_name, 
            f"{GAME_NAME}-{GAME_VERSION}-linux", 
            f"{GAME_NAME}.desktop"
        ] + ASSETS, check=True)
        print(f"Archive created: {os.path.join(DIST_DIR, archive_name)}")
    except subprocess.CalledProcessError:
        print("Warning: Failed to create tar.gz archive")
    finally:
        os.chdir(orig_dir)
    
    print(f"Linux build completed: {binary_path}")
    return True

def main():
    """Main function."""
    # Get the target platform
    target_platform = None
    if len(sys.argv) > 1:
        target_platform = sys.argv[1].lower()
    
    # Validate target platform
    valid_platforms = ["all", "windows", "macos", "linux"]
    if target_platform and target_platform not in valid_platforms:
        print(f"Error: Invalid platform '{target_platform}'")
        print(f"Valid platforms are: {', '.join(valid_platforms)}")
        sys.exit(1)
    
    # If no platform specified, detect current platform
    if not target_platform:
        target_platform = get_platform()
        print(f"No platform specified, detected: {target_platform}")
    
    # Check and install dependencies
    check_dependencies()
    
    # Clean up previous builds
    cleanup()
    
    # Create necessary directories
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # Build for the specified platform(s)
    if target_platform == "all":
        current_platform = get_platform()
        print(f"Building for all platforms (native: {current_platform})")
        
        # Always build for the current platform first
        if current_platform == "windows":
            build_windows()
        elif current_platform == "macos":
            build_macos()
        elif current_platform == "linux":
            build_linux()
        
        # Try cross-platform builds
        # Note: Cross-platform builds might not work without proper setup
        if current_platform != "windows":
            try:
                print("\nAttempting cross-platform build for Windows...")
                print("Note: This might not work without proper cross-compilation setup.")
                build_windows()
            except Exception as e:
                print(f"Windows build failed: {e}")
        
        if current_platform != "macos":
            try:
                print("\nAttempting cross-platform build for macOS...")
                print("Note: This might not work without proper cross-compilation setup.")
                build_macos()
            except Exception as e:
                print(f"macOS build failed: {e}")
        
        if current_platform != "linux":
            try:
                print("\nAttempting cross-platform build for Linux...")
                print("Note: This might not work without proper cross-compilation setup.")
                build_linux()
            except Exception as e:
                print(f"Linux build failed: {e}")
    
    else:
        # Build for the specified platform
        if target_platform == "windows":
            build_windows()
        elif target_platform == "macos":
            build_macos()
        elif target_platform == "linux":
            build_linux()
    
    print("\nBuild process completed!")
    print(f"Check the '{DIST_DIR}' directory for the build outputs.")

if __name__ == "__main__":
    main()