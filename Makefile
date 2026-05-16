.PHONY: setup install install-hooks test lint validate build serve

setup: install install-hooks

install:
	python3.12 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	pnpm install

install-hooks:
	git config --worktree --unset-all core.hooksPath || git config --local --unset-all core.hooksPath || true
	.venv/bin/pre-commit install
	.venv/bin/pre-commit install --hook-type pre-push

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/ruff check src tests
	.venv/bin/ruff format --check src tests
	.venv/bin/mypy

validate:
	.venv/bin/python -m remote_venezuela_hiring.validate_data

build:
	node scripts/build-js.mjs
	.venv/bin/python -m remote_venezuela_hiring.build_site

update-readme:  ## Actualiza la tabla de empresas en README.md
	.venv/bin/python -m remote_venezuela_hiring.update_readme

serve: build
	cd site && python -m http.server 8080
