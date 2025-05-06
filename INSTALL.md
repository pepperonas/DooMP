# DooMP Installation Guide

This guide explains how to run DooMP on different operating systems.

## Prerequisites

- Python 3.7 or later
- pip (Python package installer)

## Windows

1. **Install Python**:
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Run the game**:
   - Extract the DooMP zip file
   - Double-click `play_game.bat`
   - The launcher will install required dependencies and start the game

## macOS

1. **Install Python**:
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - OR use Homebrew: `brew install python`

2. **Run the game**:
   - Extract the DooMP zip file
   - Open Terminal in the extracted directory
   - Make the launcher executable: `chmod +x play_game.sh`
   - Run the launcher: `./play_game.sh`

## Linux

1. **Install Python**:
   - Most Linux distributions come with Python pre-installed
   - If not, install using your package manager:
     - Ubuntu/Debian: `sudo apt install python3 python3-pip`
     - Fedora: `sudo dnf install python3 python3-pip`
     - Arch: `sudo pacman -S python python-pip`

2. **Run the game**:
   - Extract the DooMP zip file
   - Open Terminal in the extracted directory
   - Make the launcher executable: `chmod +x play_game.sh`
   - Run the launcher: `./play_game.sh`

## Troubleshooting

If you encounter any issues:

1. **Python not found**:
   - Make sure Python is installed and in your system PATH
   - Try running `python --version` or `python3 --version` to confirm

2. **Dependencies installation fails**:
   - Manually install dependencies:
     - Windows: `python -m pip install pygame numpy`
     - macOS/Linux: `python3 -m pip install pygame numpy`

3. **Graphics issues**:
   - Update your graphics drivers
   - Some systems may need additional SDL libraries:
     - Ubuntu/Debian: `sudo apt install libsdl2-2.0-0`
     - Fedora: `sudo dnf install SDL2`
     - Arch: `sudo pacman -S sdl2`