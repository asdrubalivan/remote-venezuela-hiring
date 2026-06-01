#!/usr/bin/env bash
# Validate company YAML data using the project venv, from any git worktree.
set -euo pipefail

GIT_COMMON_DIR="$(git rev-parse --git-common-dir)"
MAIN_REPO_ROOT="$(cd "$GIT_COMMON_DIR/.." && pwd -P)"
PYTHON="$MAIN_REPO_ROOT/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: .venv not found at $MAIN_REPO_ROOT. Run 'uv sync' first." >&2
    exit 1
fi

exec "$PYTHON" -m remote_venezuela_hiring.validate_data
