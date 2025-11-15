#!/bin/bash

# --- FIX ---
# Set the PYTHONPATH to include the project root
export PYTHONPATH=/app
# -----------

# Wait for the main database
echo "Waiting for main database (db:5432)..."
/app/wait-for-it.sh -h db -p 5432 --timeout=30

# Wait for the test database
echo "Waiting for test database (test_db:5432)..."
/app/wait-for-it.sh -h test_db -p 5432 --timeout=30

echo "Databases are ready."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the main application
# "$@" is used to pass arguments (like the CMD from Dockerfile)
echo "Starting application..."
exec "$@"