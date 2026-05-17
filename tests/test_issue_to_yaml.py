import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from remote_venezuela_hiring.issue_to_yaml import (
    build_add_company,
    build_update_status,
    main,
    write_company,
)


@pytest.fixture
def isolated_data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "companies"
    d.mkdir()
    return d


def _add_form() -> dict[str, str]:
    return {
        "name": "Acme Inc",
        "website": "https://acme.example.com",
        "status": "accepts",
        "verification_method": "application_form",
        "hiring_platform": "greenhouse",
        "tags": "backend, remote, saas",
        "notes": "Verified via application flow.",
    }


def _update_form() -> dict[str, str]:
    return {
        "id": "proxify",
        "status": "rejects",
        "verification_method": "community_report",
        "notes": "Reported by community as no longer accepting Venezuela.",
    }


def test_build_add_company_slugifies_id() -> None:
    company = build_add_company(_add_form())
    assert company.id == "acme-inc"
    assert company.name == "Acme Inc"
    assert company.status.value == "accepts"


def test_build_add_company_parses_tags() -> None:
    company = build_add_company(_add_form())
    assert company.tags == ["backend", "remote", "saas"]


def test_build_add_company_rejects_missing_required() -> None:
    form = _add_form()
    del form["website"]
    with pytest.raises(ValueError, match="missing required fields"):
        build_add_company(form)


def test_build_add_company_validates_status_value() -> None:
    form = _add_form()
    form["status"] = "maybe"
    with pytest.raises(ValueError, match="'maybe' is not a valid"):
        build_add_company(form)


def test_build_add_company_runs_pydantic_validation() -> None:
    form = _add_form()
    form["status"] = "accepts"
    form["verification_method"] = "unknown"
    with pytest.raises(ValidationError):
        build_add_company(form)


def test_write_company_produces_canonical_yaml(isolated_data_dir: Path) -> None:
    company = build_add_company(_add_form())
    path = write_company(company, data_dir=isolated_data_dir)

    assert path == isolated_data_dir / "acme-inc.yaml"
    text = path.read_text(encoding="utf-8")
    keys = [
        line.split(":", 1)[0] for line in text.splitlines() if line and not line.startswith(" ")
    ]
    # First few keys should follow the canonical order.
    assert keys[:5] == ["id", "name", "website", "status", "last_checked"]

    # Round-trip should validate cleanly.
    reloaded = yaml.safe_load(text)
    assert reloaded["id"] == "acme-inc"
    assert reloaded["tags"] == ["backend", "remote", "saas"]


def test_build_update_status_merges_existing(isolated_data_dir: Path) -> None:
    seed_path = isolated_data_dir / "proxify.yaml"
    seed_path.write_text(
        (
            "id: proxify\n"
            "name: Proxify\n"
            "website: https://proxify.io\n"
            "status: accepts\n"
            "last_checked: 2026-01-01\n"
            "verification_method: application_form\n"
            "hiring_platform: linkedin\n"
            "tags:\n  - backend\n  - python\n"
            "notes: Originally accepted.\n"
            "archived: false\n"
        ),
        encoding="utf-8",
    )

    company = build_update_status(_update_form(), data_dir=isolated_data_dir)
    assert company.id == "proxify"
    assert company.status.value == "rejects"
    assert company.verification_method.value == "community_report"
    # Existing fields preserved.
    assert company.hiring_platform is not None
    assert company.hiring_platform.value == "linkedin"
    assert company.tags == ["backend", "python"]


def test_build_update_status_errors_if_id_missing(isolated_data_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_update_status(
            {"id": "nope", "status": "accepts", "verification_method": "recruiter"},
            data_dir=isolated_data_dir,
        )


def test_main_add_subcommand_writes_file(isolated_data_dir: Path, tmp_path: Path) -> None:
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(_add_form()), encoding="utf-8")

    rc = main(["add", "--json", str(payload_path), "--data-dir", str(isolated_data_dir)])
    assert rc == 0
    assert (isolated_data_dir / "acme-inc.yaml").is_file()


def test_build_update_status_normalizes_id_case(isolated_data_dir: Path) -> None:
    seed_path = isolated_data_dir / "hostinger.yaml"
    seed_path.write_text(
        (
            "id: hostinger\n"
            "name: Hostinger\n"
            "website: https://hostinger.com\n"
            "status: accepts\n"
            "last_checked: 2026-01-01\n"
            "verification_method: application_form\n"
            "tags: []\n"
            "archived: false\n"
        ),
        encoding="utf-8",
    )

    form = {
        "id": "Hostinger",
        "status": "rejects",
        "verification_method": "community_report",
    }

    company = build_update_status(form, data_dir=isolated_data_dir)
    assert company.id == "hostinger"
    assert company.status.value == "rejects"


def test_main_returns_nonzero_on_validation_error(isolated_data_dir: Path, tmp_path: Path) -> None:
    form = _add_form()
    form["website"] = "not a url"
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps(form), encoding="utf-8")

    rc = main(["add", "--json", str(payload_path), "--data-dir", str(isolated_data_dir)])
    assert rc == 1
