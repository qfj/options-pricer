#!/usr/bin/env bash
set -euo pipefail

echo "🛑 Stopping and cleaning demo environment..."

# Detect whether 'docker compose' (v2+) or 'docker-compose' (v1) is available
if command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ No Docker Compose found. Please install docker-compose or Docker v2+."
    exit 1
fi

# Attempt to stop and remove containers, volumes, and orphaned services
# Suppress errors if some items do not exist
$COMPOSE_CMD down --volumes --remove-orphans || true

echo "✅ Demo environment cleaned."