# Development Guide

This guide explains how to work on `remote-venezuela-hiring` using git worktrees to keep each development wave isolated.

## What are git worktrees?

Git worktrees let you check out multiple branches simultaneously in separate directories. You can work on Wave 1 validation code while Wave 0 skeleton is still checked out in another terminal — no stashing, no branch switching.

## Recommended wave structure

Each wave is a focused unit of work. Merge waves in order. Avoid mixing schema changes with UI changes.

### Wave 0 — Repository skeleton

```bash
git worktree add ../rvh-wave-0 -b wave-0-skeleton
cd ../rvh-wave-0
```

Tasks:
- Create `pyproject.toml` and package structure
- Write `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
- Add sample YAML files in `data/companies/`
- Add `.gitignore`

### Wave 1 — Pydantic schema and validation

```bash
git worktree add ../rvh-wave-1 -b wave-1-validation
cd ../rvh-wave-1
```

Tasks:
- Implement `models.py` with Pydantic v2
- Implement `load_data.py` and `validate_data.py`
- Write tests in `tests/`

### Wave 2 — Static site generation

```bash
git worktree add ../rvh-wave-2 -b wave-2-site
cd ../rvh-wave-2
```

Tasks:
- Implement `build_site.py`
- Write Jinja2 templates in `templates/`
- Write CSS and vanilla JS in `static/`
- Add tests for build output

### Wave 3 — GitHub issue contribution flow

```bash
git worktree add ../rvh-wave-3 -b wave-3-issues
cd ../rvh-wave-3
```

Tasks:
- Add GitHub Issue Forms in `.github/ISSUE_TEMPLATE/`
- Implement `issue_to_yaml.py`
- Add `issue-to-pr.yml` GitHub Action
- Write tests

### Wave 4 — CI/CD and GitHub Pages

```bash
git worktree add ../rvh-wave-4 -b wave-4-ci-pages
cd ../rvh-wave-4
```

Tasks:
- Write `validate.yml` GitHub Action
- Write `deploy-pages.yml` GitHub Action
- Configure GitHub Pages in repository settings

### Wave 5 — Polish

```bash
git worktree add ../rvh-wave-5 -b wave-5-polish
cd ../rvh-wave-5
```

Tasks:
- Accessibility improvements
- Mobile responsiveness review
- README badges
- Sample data cleanup

## Rules for all waves

- Run `python -m remote_venezuela_hiring.validate_data` before every PR
- Run `pytest tests/` before every PR
- Keep each PR focused on one wave
- Merge waves in order (wave-1 after wave-0, etc.)
- Never mix schema changes with UI changes in the same wave

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick commands

```bash
# Validate all YAML data
python -m remote_venezuela_hiring.validate_data

# Build the static site
python -m remote_venezuela_hiring.build_site

# Run tests
pytest tests/ -v

# Lint
ruff check src tests

# Local preview
cd site && python -m http.server 8080
```
