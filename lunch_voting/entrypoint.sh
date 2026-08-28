#!/usr/bin/env bash
set -e

echo "Waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
python - <<'PYEOF'
import os
import socket
import sys
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))

for _ in range(30):
    try:
        socket.create_connection((host, port), timeout=1).close()
        sys.exit(0)
    except OSError:
        time.sleep(1)
print("Postgres did not become available in time.", file=sys.stderr)
sys.exit(1)
PYEOF
echo "Postgres is up."

python manage.py migrate --noinput

exec "$@"
