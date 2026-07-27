#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for command_name in git docker; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Missing required command: $command_name" >&2
    exit 1
  }
done

docker compose version >/dev/null

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

printf 'git:     %s\n' "$(git --version)"
printf 'docker:  %s\n' "$(docker --version)"
printf 'compose: %s\n' "$(docker compose version)"
echo "Starter prerequisites are ready. Run: docker compose up --build"
