#!/usr/bin/env bash
set -e

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Execute the original start script
exec ./start.sh 