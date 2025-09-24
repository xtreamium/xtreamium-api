#!/bin/bash

# Build Docker image for xtreamium-backend
# Usage: ./build_docker.sh [tag] [run_mode]
# 
# Arguments:
#   tag      - Docker image tag (default: xtreamium-backend:latest)
#   run_mode - Build mode: production or development (default: production)

set -e

# Default values
DEFAULT_TAG="xtreamium-backend:latest"
DEFAULT_RUN_MODE="production"

# Parse arguments
TAG=${1:-$DEFAULT_TAG}
RUN_MODE=${2:-$DEFAULT_RUN_MODE}

# Get the script directory and set context directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKERFILE_PATH="$CONTEXT_DIR/docker/Dockerfile"

echo "Building Docker image..."
echo "  Context directory: $CONTEXT_DIR"
echo "  Dockerfile: $DOCKERFILE_PATH"
echo "  Image tag: $TAG"
echo "  Run mode: $RUN_MODE"
echo ""

# Verify Dockerfile exists
if [ ! -f "$DOCKERFILE_PATH" ]; then
    echo "Error: Dockerfile not found at $DOCKERFILE_PATH"
    exit 1
fi

# Build the Docker image
docker build \
    --file "$DOCKERFILE_PATH" \
    --build-arg RUN_MODE="$RUN_MODE" \
    --tag "$TAG" \
    "$CONTEXT_DIR"

echo ""
echo "✅ Docker image built successfully!"
echo "   Image: $TAG"
echo "   Run mode: $RUN_MODE"
echo ""
echo "To run the container:"
echo "   docker run -p 8080:80 $TAG"