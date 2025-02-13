#!/usr/bin/env bash
set -e

# Get the directory where this script is located
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

# Run database migrations
echo "Running database migrations..."
(
    cd open_webui
    PYTHONPATH=/app/backend alembic stamp head  # Mark the current version as head
    PYTHONPATH=/app/backend alembic upgrade head # Then try to upgrade
)

# Execute the original start script
exec "$SCRIPT_DIR/start.sh" 