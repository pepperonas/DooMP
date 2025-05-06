#!/bin/bash
# Script to build Windows executable for DooMP using Docker

echo "Starting Windows build using Docker..."
echo "This will create a Windows executable using a Windows Docker container."
echo "Make sure Docker Desktop is installed and running."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH. Please install Docker Desktop first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running. Please start Docker Desktop first."
    exit 1
fi

echo "Building Windows Docker image (this may take a while)..."
docker build -t doomp-windows-builder -f Dockerfile.windows .

echo "Creating dist directory if it doesn't exist..."
mkdir -p dist

echo "Copying the Windows executable from the container..."
docker create --name doomp-windows-temp doomp-windows-builder
docker cp doomp-windows-temp:/app/dist/DooMP-1.0-win64.exe ./dist/
docker rm doomp-windows-temp

if [ -f "./dist/DooMP-1.0-win64.exe" ]; then
    echo "Build successful! Windows executable is available at: ./dist/DooMP-1.0-win64.exe"
else
    echo "Error: Build failed or executable not found."
    exit 1
fi