#!/usr/bin/env bash
set -e

CONTAINER_NAME=pricer
PORT=8080

if docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Stopping pricer server..."
    docker stop $CONTAINER_NAME >/dev/null
    docker rm $CONTAINER_NAME >/dev/null
    echo "Server stopped and container removed."
else
    echo "No running pricer container found."
fi

# Free up any stray process if necessary
sudo fuser -k $PORT/tcp 2>/dev/null || true
