#!/usr/bin/env bash
# Uses the repository virtual environment and trusted local shell configuration.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [ ! -x .venv/bin/python ]; then
  echo "请先运行 bash install.sh。" >&2
  exit 1
fi
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi
SCRIPT="${INTERVIEW_TRANSCRIBE_SCRIPT:-$ROOT/scripts/1_transcribe.py}"
exec "$ROOT/.venv/bin/python" "$SCRIPT" "$@"
