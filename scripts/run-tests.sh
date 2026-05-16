#!/usr/bin/env bash
# Run unit tests using the project venv, from any git worktree.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTEST="$REPO_ROOT/.venv/bin/pytest"

if [ ! -x "$PYTEST" ]; then
    echo "ERROR: .venv not found at $REPO_ROOT. Run 'make setup' first." >&2
    exit 1
fi

exec "$PYTEST" --ignore=tests/e2e -q "$@"
