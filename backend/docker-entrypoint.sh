#!/usr/bin/env bash
set -e

# Get the directory where this script is located
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

# Run database migrations
echo "Running database migrations..."
cd open_webui && PYTHONPATH=/app/backend alembic upgrade head && cd ..

# Execute the original start script
exec ./start.sh 