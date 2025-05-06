# DooMP

A raycasting-based 3D game.

## Deployment Instructions

This repository includes a deployment script that allows you to build standalone executables for Windows, macOS, and Linux.

### Prerequisites

- Python 3.7 or later
- pip (Python package installer)

### Setup

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Building the Game

To build the game, use the `deploy.py` script with the target platform as an argument:

```bash
# Build for the current platform
python deploy.py

# Build for Windows
python deploy.py windows

# Build for macOS
python deploy.py macos

# Build for Linux
python deploy.py linux

# Try to build for all platforms (may require additional setup)
python deploy.py all
```

The script will:
1. Install PyInstaller if it's not already installed
2. Clean up any previous build files
3. Build the game for the specified platform
4. Package all necessary resources
5. Create distribution files in the `dist` directory

### Outputs

Depending on the platform, the script will create:

- **Windows**: An `.exe` file in the `dist` directory
- **macOS**: An `.app` bundle and optionally a `.dmg` file in the `dist` directory
- **Linux**: An executable file, a `.desktop` file, and a `.tar.gz` archive in the `dist` directory

### Cross-Platform Building

The script attempts to build for platforms other than the one you're running on, but this may not work without additional setup. For reliable cross-platform builds, it's best to run the script on each target platform.

### Adding Assets

If your game uses additional asset files (images, sounds, etc.), add them to the `ASSETS` list in the `deploy.py` script:

```python
ASSETS = ["shot.wav", "icon.png", "other_asset.jpg"]
```

### Adding an Icon

To add a custom icon to your game, specify the path to your icon file in the `deploy.py` script:

```python
ICON_FILE = "path/to/your/icon.ico"  # for Windows
# or
ICON_FILE = "path/to/your/icon.icns"  # for macOS
```

## Running the Game

After building, you can run the game by:

- **Windows**: Double-click the `.exe` file in the `dist` directory
- **macOS**: Double-click the `.app` bundle in the `dist` directory
- **Linux**: Run the executable file in the `dist` directory

## Troubleshooting

If you encounter any issues during the build process:

1. Make sure you have the latest version of PyInstaller installed
2. Check that all dependencies are correctly installed
3. Look for error messages in the build output
4. For platform-specific issues, consult the PyInstaller documentation