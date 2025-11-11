#!/bin/bash
set -e

IMAGE_NAME="options_pricer"

echo "Building Docker image '${IMAGE_NAME}'..."
docker build --no-cache -t ${IMAGE_NAME} .

echo "Done! You can run it with: docker run --rm ${IMAGE_NAME}"