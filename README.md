# DooMP

DooMP is a raycasting-based 3D shooter game written in Python using Pygame.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Building from Source](#building-from-source)
  - [Cross-Platform Package](#cross-platform-package)
  - [Building Windows Executable on macOS](#building-windows-executable-on-macos)
  - [Building with GitHub Actions](#building-with-github-actions)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- Raycasting-based 3D rendering
- First-person shooter gameplay
- Enemy AI with various behaviors
- Weapons and projectile system
- Health and scoring system
- Minimap for navigation

## Installation

### Windows
Download and run the latest `DooMP-x.x-win64.exe` from the releases page.

### macOS
Download and mount the `DooMP-x.x-macos.dmg` file, then drag the application to your Applications folder.

### Linux
Download the `DooMP-x.x-linux.tar.gz` file, extract it, and run the executable:

```bash
tar -xzf DooMP-x.x-linux.tar.gz
chmod +x DooMP-x.x-linux
./DooMP-x.x-linux
```

### From Source
If you have Python installed, you can run the game directly from source:

```bash
# Clone or download the repository
git clone https://github.com/your-username/DooMP.git
cd DooMP

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## How to Play

### Controls
- **WASD / Arrow Keys**: Move
- **Mouse**: Look around
- **Left Click**: Shoot
- **R**: Reload when out of ammo
- **ESC**: Exit game
- **H / F1**: Show help overlay

### Gameplay
- Defeat enemies to score points
- Avoid taking damage from enemies
- Navigate the maze to find and eliminate all enemies

## Building from Source

### Cross-Platform Package

To create a distributable package that works on any system with Python installed:

```bash
python build_package.py
```

This creates a ZIP file in the `dist` directory containing everything needed to run the game on any platform.

### Building Windows Executable on macOS

#### Using Docker

1. Install Docker Desktop for macOS
2. Run the build script:

```bash
./build_windows.sh
```

This will create a Windows executable (`DooMP-1.0-win64.exe`) in the `dist` directory.

#### Using Wine

1. Install Wine on macOS:

```bash
brew install --cask wine-stable
```

2. Run the Wine-based build script:

```bash
./build_windows_wine.sh
```

### Building macOS App

To build a native macOS application:

```bash
python deploy.py macos
```

This creates a `.app` bundle and `.dmg` file in the `dist` directory.

### Building Linux Executable

To build a Linux executable:

```bash
python deploy.py linux
```

This creates an executable and a `.tar.gz` archive in the `dist` directory.

### Building with GitHub Actions

This repository includes GitHub Actions workflows that automatically build game packages for all platforms.

To use it:
1. Push your code to GitHub
2. Go to the Actions tab in your repository
3. Run the "Build Game Packages" workflow manually or push to the main branch

## Development

### Requirements
- Python 3.7+
- Pygame 2.0+
- NumPy

### Project Structure
- `main.py`: Main game code
- `deploy.py`: Deployment script for creating standalone executables
- `build_package.py`: Script for creating cross-platform packages
- `build_windows.sh` and `build_windows_wine.sh`: Scripts for building Windows executables on macOS
- `.github/workflows/build.yml`: GitHub Actions workflow for automated builds

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Copyright © 2025 Martin Pfeffer. All rights reserved.