#!/usr/bin/env bash
set -e

# Get the directory where this script is located
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" || exit

# Run database migrations
echo "Running database migrations..."
(
    cd open_webui
    
    # Function to check if current version exists in our migration files
    check_version_exists() {
        PYTHONPATH=/app/backend python3 -c "
from sqlalchemy import create_engine, text
from open_webui.env import DATABASE_URL
import os

try:
    # Get current version from database
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        current = conn.execute(text('SELECT version_num FROM alembic_version')).scalar()
        if not current:
            exit(1)
    
    # Check if this version exists in our migrations directory
    migrations_dir = './migrations/versions'
    migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py')]
    for file in migration_files:
        with open(os.path.join(migrations_dir, file), 'r') as f:
            if current in f.read():
                exit(1)  # Version found in our files
    
    # If we get here, version exists in DB but not in our files
    print(f'Found unknown version: {current}')
    exit(0)
except Exception as e:
    print(f'Error checking version: {e}')
    exit(1)
"
    }

    # If we have an unknown version, reset the version table
    if check_version_exists; then
        echo "Found unknown version in database, resetting migration state..."
        PYTHONPATH=/app/backend python3 -c "
from sqlalchemy import create_engine, text
from open_webui.env import DATABASE_URL
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
    conn.commit()
"
    fi

    # Run migrations
    echo "Applying database migrations..."
    PYTHONPATH=/app/backend alembic upgrade head || {
        echo "Migration failed. Please check the database state and migration files."
        exit 1
    }
)

# Execute the original start script
cd "$SCRIPT_DIR"
exec ./start.sh 