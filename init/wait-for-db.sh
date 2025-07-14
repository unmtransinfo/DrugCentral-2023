#!/bin/bash
set -e

# Wait until PostgreSQL is ready
until pg_isready -U root -d postgres; do
  echo "Waiting for postgres..."
  sleep 2
done

# Create database if not exists
psql -U root -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'drugcen'" | grep -q 1 || \
psql -U root -d postgres -c "CREATE DATABASE drugcen OWNER root;"

# Enable RDKit extension
psql -U root -d drugcen -c "CREATE EXTENSION IF NOT EXISTS rdkit;"

# Restore from dump
pg_restore -U root -d drugcen /docker-entrypoint-initdb.d/drugcen.dump
