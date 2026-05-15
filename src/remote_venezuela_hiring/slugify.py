"""Tiny slug helper used when generating a company ``id`` from a name."""

from __future__ import annotations

import re

_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s-]")
_WHITESPACE_RE = re.compile(r"\s+")
_DASHES_RE = re.compile(r"-+")


def slugify(name: str) -> str:
    """Return a lowercase kebab-case slug derived from *name*."""
    s = name.lower()
    s = _NON_ALNUM_RE.sub("", s)
    s = _WHITESPACE_RE.sub("-", s.strip())
    s = _DASHES_RE.sub("-", s)
    return s.strip("-")
