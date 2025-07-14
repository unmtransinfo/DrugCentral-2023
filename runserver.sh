#!/bin/sh

set -e

cd "$(dirname "$0")"
exec python3 manage.py runserver 0.0.0.0:8000
