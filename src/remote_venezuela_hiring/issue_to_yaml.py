"""CLI: convert a parsed GitHub issue form into a validated YAML entry.

The workflow uses ``stefanbuck/github-issue-parser`` to turn the issue body
into a JSON object keyed by the form's field ``id``s. This script reads that
JSON, validates it against the :class:`Company` model, and writes the result
to ``data/companies/<id>.yaml``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NotRequired, TypedDict

import yaml
from pydantic import ValidationError

from .load_data import DATA_DIR, load_company
from .models import (
    Company,
    CompanyStatus,
    HiringPlatform,
    VerificationMethod,
    today_utc,
)
from .slugify import slugify


class AddCompanyForm(TypedDict):
    """Fields produced by ``.github/ISSUE_TEMPLATE/add-company.yml``."""

    name: str
    website: str
    status: str
    verification_method: str
    hiring_platform: str
    tags: NotRequired[str]
    notes: NotRequired[str]


class UpdateStatusForm(TypedDict):
    """Fields produced by ``.github/ISSUE_TEMPLATE/update-status.yml``."""

    id: str
    status: str
    verification_method: str
    notes: NotRequired[str]


# Canonical YAML key order in generated files. Matches the sample entries.
_YAML_KEY_ORDER: tuple[str, ...] = (
    "id",
    "name",
    "website",
    "status",
    "last_checked",
    "verification_method",
    "hiring_platform",
    "tags",
    "notes",
    "archived",
)


def _read_json_form(path: Path) -> dict[str, str]:
    """Read the parsed issue JSON, returning a flat ``str -> str`` mapping."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"expected JSON object at {path}, got {type(raw).__name__}"
        raise TypeError(msg)
    result: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, str):
            result[key] = value.strip()
    return result


def _parse_tags(raw: str | None) -> list[str]:
    """Split a comma-separated tag string into a normalized list."""
    if not raw:
        return []
    return [t.strip().lower() for t in raw.split(",") if t.strip()]


def _company_to_yaml(company: Company) -> str:
    """Serialize a Company to YAML in the project's canonical key order."""
    data: dict[str, object] = {
        "id": company.id,
        "name": company.name,
        "website": str(company.website),
        "status": company.status.value,
        "last_checked": company.last_checked,
        "verification_method": company.verification_method.value,
        "hiring_platform": (company.hiring_platform.value if company.hiring_platform else None),
        "tags": list(company.tags),
        "notes": company.notes,
        "archived": company.archived,
    }
    # Match the sample-file shape: drop hiring_platform if None.
    if data["hiring_platform"] is None:
        del data["hiring_platform"]
    # Preserve canonical order regardless of dict iteration.
    ordered = {k: data[k] for k in _YAML_KEY_ORDER if k in data}
    return yaml.safe_dump(
        ordered,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=88,
    )


def build_add_company(form: dict[str, str]) -> Company:
    """Build a new :class:`Company` from the add-company form payload."""
    required = ("name", "website", "status", "verification_method", "hiring_platform")
    missing = [k for k in required if not form.get(k)]
    if missing:
        msg = f"missing required fields: {', '.join(missing)}"
        raise ValueError(msg)

    name = form["name"]
    payload: dict[str, object] = {
        "id": slugify(name),
        "name": name,
        "website": form["website"],
        "status": CompanyStatus(form["status"]).value,
        "last_checked": today_utc().isoformat(),
        "verification_method": VerificationMethod(form["verification_method"]).value,
        "hiring_platform": HiringPlatform(form["hiring_platform"]).value,
        "tags": _parse_tags(form.get("tags")),
        "notes": form.get("notes") or None,
        "archived": False,
    }
    return Company.model_validate(payload)


def build_update_status(form: dict[str, str], data_dir: Path = DATA_DIR) -> Company:
    """Apply an update-status form to the existing YAML, returning the merged Company."""
    required = ("id", "status", "verification_method")
    missing = [k for k in required if not form.get(k)]
    if missing:
        msg = f"missing required fields: {', '.join(missing)}"
        raise ValueError(msg)

    company_id = form["id"]
    path = data_dir / f"{company_id}.yaml"
    if not path.is_file():
        msg = f"no existing entry for id '{company_id}' at {path}"
        raise FileNotFoundError(msg)

    existing = load_company(path)
    merged_payload: dict[str, object] = {
        "id": existing.id,
        "name": existing.name,
        "website": str(existing.website),
        "status": CompanyStatus(form["status"]).value,
        "last_checked": today_utc().isoformat(),
        "verification_method": VerificationMethod(form["verification_method"]).value,
        "hiring_platform": (existing.hiring_platform.value if existing.hiring_platform else None),
        "tags": list(existing.tags),
        "notes": form.get("notes") or existing.notes,
        "archived": existing.archived,
    }
    return Company.model_validate(merged_payload)


def write_company(company: Company, data_dir: Path = DATA_DIR) -> Path:
    """Write *company* to ``<data_dir>/<id>.yaml`` and return the path."""
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / f"{company.id}.yaml"
    target.write_text(_company_to_yaml(company), encoding="utf-8")
    return target


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="rvh-issue-to-yaml",
        description="Convert a parsed GitHub issue form into a validated YAML entry.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Create a new company entry from an add-company form.")
    add.add_argument("--json", type=Path, required=True, help="Path to the parsed issue JSON.")
    add.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Where to write the YAML file (default: data/companies).",
    )

    update = sub.add_parser(
        "update", help="Update an existing company entry from an update-status form."
    )
    update.add_argument("--json", type=Path, required=True, help="Path to the parsed issue JSON.")
    update.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Where the existing YAML lives (default: data/companies).",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``rvh-issue-to-yaml``."""
    args = _parse_args(argv)
    try:
        form = _read_json_form(args.json)
        company = (
            build_add_company(form)
            if args.command == "add"
            else build_update_status(form, data_dir=args.data_dir)
        )
        path = write_company(company, data_dir=args.data_dir)
    except (ValidationError, ValueError, TypeError, FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
