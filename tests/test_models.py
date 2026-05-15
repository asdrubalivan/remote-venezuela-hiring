from datetime import UTC, date, datetime, timedelta
from typing import NotRequired, TypedDict, Unpack

import pytest
from pydantic import ValidationError

from remote_venezuela_hiring.models import (
    Company,
    CompanyStatus,
    HiringPlatform,
    VerificationMethod,
)


class CompanyPayload(TypedDict):
    """Shape of the raw payload passed to ``Company.model_validate`` in tests.

    Every field is ``NotRequired`` so tests can override only the keys they
    care about. Values are stored as the JSON/YAML-shaped primitives Pydantic
    will coerce — strings for enums, ISO date strings for dates, etc.
    """

    id: NotRequired[str]
    name: NotRequired[str]
    website: NotRequired[str]
    status: NotRequired[str]
    last_checked: NotRequired[str]
    verification_method: NotRequired[str]
    hiring_platform: NotRequired[str]
    tags: NotRequired[list[str]]
    notes: NotRequired[str | None]
    archived: NotRequired[bool]


def _today() -> date:
    return datetime.now(UTC).date()


def make_payload(**overrides: Unpack[CompanyPayload]) -> CompanyPayload:
    """Build a valid CompanyPayload, with optional per-test overrides."""
    base: CompanyPayload = {
        "id": "my-company",
        "name": "My Company",
        "website": "https://example.com",
        "status": "accepts",
        "last_checked": _today().isoformat(),
        "verification_method": "application_form",
        "hiring_platform": "greenhouse",
        "tags": ["backend", "remote"],
        "notes": "Verified via application form.",
        "archived": False,
    }
    base.update(overrides)
    return base


def test_valid_company_loads() -> None:
    company = Company.model_validate(make_payload())
    assert company.id == "my-company"
    assert company.status == CompanyStatus.accepts
    assert company.verification_method == VerificationMethod.application_form
    assert company.hiring_platform == HiringPlatform.greenhouse


def test_id_must_be_kebab_case() -> None:
    with pytest.raises(ValidationError) as exc:
        Company.model_validate(make_payload(id="My_Company"))
    assert "kebab-case" in str(exc.value)


def test_name_cannot_be_empty() -> None:
    with pytest.raises(ValidationError):
        Company.model_validate(make_payload(name="   "))


def test_last_checked_cannot_be_in_future() -> None:
    future = (_today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError) as exc:
        Company.model_validate(make_payload(last_checked=future))
    assert "future" in str(exc.value)


def test_tags_must_be_kebab_case() -> None:
    with pytest.raises(ValidationError):
        Company.model_validate(make_payload(tags=["Backend"]))


def test_tags_are_sorted() -> None:
    company = Company.model_validate(make_payload(tags=["zebra", "alpha", "middle"]))
    assert company.tags == ["alpha", "middle", "zebra"]


def test_notes_max_length() -> None:
    with pytest.raises(ValidationError) as exc:
        Company.model_validate(make_payload(notes="x" * 501))
    assert "500" in str(exc.value)


def test_notes_disallowed_term() -> None:
    with pytest.raises(ValidationError) as exc:
        Company.model_validate(make_payload(notes="This place is a scam."))
    assert "disallowed" in str(exc.value).lower()


def test_definitive_status_requires_known_verification_method() -> None:
    with pytest.raises(ValidationError) as exc:
        Company.model_validate(make_payload(status="accepts", verification_method="unknown"))
    assert "verification_method" in str(exc.value)


def test_unknown_status_allows_unknown_verification_method() -> None:
    company = Company.model_validate(make_payload(status="unknown", verification_method="unknown"))
    assert company.status == CompanyStatus.unknown


def test_invalid_website_url() -> None:
    with pytest.raises(ValidationError):
        Company.model_validate(make_payload(website="not-a-url"))


def test_is_stale_returns_true_for_old_entries() -> None:
    old = (_today() - timedelta(days=200)).isoformat()
    company = Company.model_validate(make_payload(last_checked=old))
    assert company.is_stale() is True


def test_is_stale_returns_false_for_recent_entries() -> None:
    recent = (_today() - timedelta(days=10)).isoformat()
    company = Company.model_validate(make_payload(last_checked=recent))
    assert company.is_stale() is False
