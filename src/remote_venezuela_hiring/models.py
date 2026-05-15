"""Pydantic models that describe a single company entry in the dataset."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

KEBAB_CASE_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

NOTES_MAX_LENGTH: Final[int] = 500

DISALLOWED_NOTES_TERMS: Final[tuple[str, ...]] = (
    "scam",
    "toxic",
    "illegal",
    "sanctions violation",
    "996",
    "burnout",
    "bad work-life balance",
    "screenshot",
    "recruiter name",
    "email thread",
)


def today_utc() -> date:
    """Return today's date in UTC.

    Using UTC keeps validation consistent across contributors and CI runners
    regardless of their local timezone.
    """
    return datetime.now(UTC).date()


class CompanyStatus(StrEnum):
    """How a company currently treats applications from Venezuela-based candidates."""

    accepts = "accepts"
    rejects = "rejects"
    unknown = "unknown"


class VerificationMethod(StrEnum):
    """How the contributor verified the company's stance."""

    application_form = "application_form"
    recruiter = "recruiter"
    public_job_post = "public_job_post"
    community_report = "community_report"
    unknown = "unknown"


class HiringPlatform(StrEnum):
    """The applicant tracking system or hiring surface the company uses."""

    greenhouse = "greenhouse"
    ashby = "ashby"
    lever = "lever"
    workable = "workable"
    teamtailor = "teamtailor"
    linkedin = "linkedin"
    company_site = "company_site"
    other = "other"
    unknown = "unknown"


class Company(BaseModel):
    """A single company entry, validated against the project's rules."""

    model_config = ConfigDict(extra="forbid", frozen=False, str_strip_whitespace=False)

    id: str
    name: str
    website: HttpUrl
    status: CompanyStatus
    last_checked: date
    verification_method: VerificationMethod
    hiring_platform: HiringPlatform | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    archived: bool = False

    @field_validator("id")
    @classmethod
    def _id_must_be_kebab_case(cls, v: str) -> str:
        if not KEBAB_CASE_RE.match(v):
            msg = "must be lowercase kebab-case (e.g. 'my-company')"
            raise ValueError(msg)
        return v

    @field_validator("name")
    @classmethod
    def _name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            msg = "cannot be empty"
            raise ValueError(msg)
        return v

    @field_validator("last_checked")
    @classmethod
    def _last_checked_not_in_future(cls, v: date) -> date:
        if v > today_utc():
            msg = "cannot be in the future"
            raise ValueError(msg)
        return v

    @field_validator("tags")
    @classmethod
    def _tags_must_be_kebab_case(cls, v: list[str]) -> list[str]:
        for tag in v:
            if not KEBAB_CASE_RE.match(tag):
                msg = f"tag '{tag}' must be lowercase kebab-case"
                raise ValueError(msg)
        return sorted(v)

    @field_validator("notes")
    @classmethod
    def _notes_must_be_safe(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) > NOTES_MAX_LENGTH:
            msg = f"must be {NOTES_MAX_LENGTH} characters or fewer (got {len(v)})"
            raise ValueError(msg)
        lower = v.lower()
        for term in DISALLOWED_NOTES_TERMS:
            if term in lower:
                msg = f"contains disallowed term: '{term}'"
                raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def _definitive_status_requires_known_method(self) -> Company:
        if (
            self.status in (CompanyStatus.accepts, CompanyStatus.rejects)
            and self.verification_method == VerificationMethod.unknown
        ):
            msg = "verification_method cannot be 'unknown' when status is 'accepts' or 'rejects'"
            raise ValueError(msg)
        return self

    def is_stale(self, *, max_age_days: int = 180) -> bool:
        """Return ``True`` when the entry has not been re-checked recently."""
        return (today_utc() - self.last_checked).days > max_age_days

    def website_str(self) -> str:
        """Return the website as a plain string (Pydantic stores it as ``HttpUrl``)."""
        return str(self.website)
