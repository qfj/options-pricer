#!/usr/bin/env bash
set -e

echo "🧹 Cleaning previous containers and volumes..."

# Detect compose command
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi

# Stop and remove everything safely
$COMPOSE down --remove-orphans -v || true

echo "🧱 Building fresh images..."
# Build without cache, handle different CLI versions
if [[ "$COMPOSE" == "docker compose" ]]; then
    $COMPOSE build --no-cache
else
    $COMPOSE build --no-cache
fi

echo "🚀 Starting demo environment..."
$COMPOSE up --build