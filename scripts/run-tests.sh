#!/usr/bin/env bash
# Run unit tests using the project venv, from any git worktree.
set -euo pipefail

# --git-common-dir resolves to the main .git dir (works from worktrees too)
GIT_COMMON_DIR="$(git rev-parse --git-common-dir)"
MAIN_REPO_ROOT="$(cd "$GIT_COMMON_DIR/.." && pwd -P)"
PYTEST="$MAIN_REPO_ROOT/.venv/bin/pytest"

if [ ! -x "$PYTEST" ]; then
    echo "ERROR: .venv not found at $REPO_ROOT. Run 'make setup' first." >&2
    exit 1
fi

# E2E tests (tests/e2e/) are excluded here because they require Playwright,
# which is not expected to be installed locally. They run in CI via validate.yml.
exec "$PYTEST" --ignore=tests/e2e -q "$@"
