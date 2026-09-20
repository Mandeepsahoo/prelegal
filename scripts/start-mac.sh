#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

IMAGE_NAME="prelegal"
CONTAINER_NAME="prelegal"

docker build -t "$IMAGE_NAME" .
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER_NAME" -p 8000:8000 --env-file .env "$IMAGE_NAME"

echo "Prelegal is running at http://localhost:8000"
open "http://localhost:8000" >/dev/null 2>&1 || true
