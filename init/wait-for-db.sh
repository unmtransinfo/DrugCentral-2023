#!/bin/bash
set -e

DB_NAME="${POSTGRES_DB:-drugcen}"
DB_USER="${POSTGRES_USER:-root}"
DUMP_FILE="/docker-entrypoint-initdb.d/drugcen.dump"

# Wait until PostgreSQL is ready
until pg_isready -U "$DB_USER" -d postgres; do
  echo "Waiting for postgres..."
  sleep 2
done

# Create database if not exists
psql -U "$DB_USER" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -U "$DB_USER" -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"

# Enable RDKit extension
psql -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS rdkit;"

# Restore from dump
pg_restore --no-owner -U "$DB_USER" -d "$DB_NAME" "$DUMP_FILE"
