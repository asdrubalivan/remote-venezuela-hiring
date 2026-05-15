#!/usr/bin/env bash
# Install the project's git hooks.
#
# Tries the `pre-commit` framework first (recommended). Falls back to a
# symlink-based native git hook if pre-commit is not installed.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if command -v pre-commit >/dev/null 2>&1; then
    echo "▶ Installing hooks via pre-commit framework..."
    pre-commit install
    pre-commit install --hook-type pre-push
    echo "✔ pre-commit hooks installed."
    exit 0
fi

echo "▶ pre-commit not found. Installing native git hook..."
mkdir -p .git/hooks
ln -sf "../../scripts/git-hooks/pre-commit" .git/hooks/pre-commit
chmod +x scripts/git-hooks/pre-commit
echo "✔ Native pre-commit hook symlinked into .git/hooks/."
echo "  (Tip: install the 'pre-commit' framework for richer config: pip install pre-commit)"
