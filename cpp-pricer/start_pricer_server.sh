#!/bin/bash
set -e

CONTAINER_NAME="pricer"
IMAGE_NAME="options_pricer"

# Stop and remove any existing container with the same name
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping and removing existing container '${CONTAINER_NAME}'..."
    docker rm -f "${CONTAINER_NAME}"
fi

echo "Starting pricer server..."
docker run -d -p 8080:8080 --name "${CONTAINER_NAME}" "${IMAGE_NAME}"
echo "Server started. Use './stop_pricer_server.sh' to stop it."
