"""CLI: validate every YAML entry in ``data/companies/``.

Exits with status 1 on any error so the GitHub Action and the git pre-commit
hook can rely on the return code.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import yaml
from pydantic import ValidationError

from .load_data import DATA_DIR
from .models import Company

if TYPE_CHECKING:
    from pathlib import Path


def validate_all(data_dir: Path = DATA_DIR) -> tuple[list[str], list[str]]:
    """Validate every ``*.yaml`` in *data_dir*.

    Returns:
        Tuple ``(errors, warnings)`` of human-readable messages.
    """
    errors: list[str] = []
    warnings: list[str] = []

    yaml_files = sorted(data_dir.glob("*.yaml"))
    if not yaml_files:
        warnings.append(f"{data_dir}: no YAML files found")
        return errors, warnings

    for path in yaml_files:
        _validate_one(path, errors, warnings)

    return errors, warnings


def _validate_one(path: Path, errors: list[str], warnings: list[str]) -> None:
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{path}: could not parse YAML: {exc}")
        return

    if not isinstance(data, dict):
        errors.append(f"{path}: file does not contain a YAML mapping")
        return

    try:
        company = Company.model_validate(data)
    except ValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(x) for x in err["loc"])
            errors.append(f"{path}: field '{loc}': {err['msg']}")
        return

    if path.stem != company.id:
        errors.append(f"{path}: filename '{path.stem}' does not match id '{company.id}'")

    if company.is_stale():
        warnings.append(
            f"{path}: '{company.id}' last_checked is older than 180 days "
            f"(last checked: {company.last_checked})"
        )


def main() -> int:
    """Entry point for ``rvh-validate``. Returns the process exit code."""
    errors, warnings = validate_all()

    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\n{len(errors)} error(s) found. Fix them before continuing.")
        return 1

    if warnings:
        print(f"\n{len(warnings)} warning(s). Data is valid.")
    else:
        print("All data is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
