#!/usr/bin/env bash
# Copy this repo's .env (or .env.example) into a target module directory.
# Usage: ./inject_env.sh <target>
#   target: mobius-chat | mobius-rag | mobius-dbt | mobius-os/backend | mobius-user
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TARGET="${1:?Usage: $0 <target> (e.g. mobius-chat, mobius-rag, mobius-dbt, mobius-os/backend)}"

# Resolve target path relative to parent of mobius-config
PARENT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEST="$PARENT/$TARGET"

if [[ ! -d "$DEST" ]]; then
  echo "Target directory does not exist: $DEST"
  exit 1
fi

if [[ -f "$SCRIPT_DIR/.env" ]]; then
  cp "$SCRIPT_DIR/.env" "$DEST/.env"
  echo "Copied .env to $DEST/.env"
else
  if [[ -f "$SCRIPT_DIR/.env.example" ]]; then
    cp "$SCRIPT_DIR/.env.example" "$DEST/.env"
    echo "Copied .env.example to $DEST/.env (fill in values)"
  else
    echo "No .env or .env.example in mobius-config. Create .env from .env.example first."
    exit 1
  fi
fi
