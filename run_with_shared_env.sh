#!/usr/bin/env bash
# Source this repo's .env and run a command from a module directory.
# Usage: ./run_with_shared_env.sh <module_dir> <command> [args...]
# Example: ./run_with_shared_env.sh ../mobius-chat ./mchatc
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODULE_DIR="${1:?Usage: $0 <module_dir> <command> [args...]}"
shift || true

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 <module_dir> <command> [args...]"
  echo "Example: $0 ../mobius-chat ./mchatc"
  exit 1
fi

# Resolve module dir (relative to mobius-config)
if [[ "$MODULE_DIR" != /* ]]; then
  MODULE_DIR="$(cd "$SCRIPT_DIR/$MODULE_DIR" && pwd)"
else
  MODULE_DIR="$(cd "$MODULE_DIR" && pwd)"
fi

if [[ ! -d "$MODULE_DIR" ]]; then
  echo "Module directory does not exist: $MODULE_DIR"
  exit 1
fi

if [[ -f "$SCRIPT_DIR/.env" ]]; then
  # Safe .env loader (no shell expansion).
  # Avoids corrupting values that contain '$@' (e.g. passwords ending with '$').
  while IFS= read -r _line || [[ -n "$_line" ]]; do
    [[ -z "$_line" || "$_line" =~ ^[[:space:]]*# ]] && continue
    if [[ "$_line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
      export "${BASH_REMATCH[1]}=${BASH_REMATCH[2]}"
    fi
  done < "$SCRIPT_DIR/.env"
fi

cd "$MODULE_DIR"
exec "$@"
