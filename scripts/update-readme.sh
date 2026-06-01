#!/usr/bin/env bash
# Regenerate the README companies table and stage the result, from any git worktree.
set -euo pipefail

GIT_COMMON_DIR="$(git rev-parse --git-common-dir)"
MAIN_REPO_ROOT="$(cd "$GIT_COMMON_DIR/.." && pwd -P)"
PYTHON="$MAIN_REPO_ROOT/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: .venv not found at $MAIN_REPO_ROOT. Run 'uv sync' first." >&2
    exit 1
fi

"$PYTHON" -m remote_venezuela_hiring.update_readme

# Stage README so the update is included in the current commit.
git add "$MAIN_REPO_ROOT/README.md"
