"""Load company YAML files into validated :class:`Company` instances."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Company

DATA_DIR: Path = Path(__file__).resolve().parents[2] / "data" / "companies"


def load_company(path: Path) -> Company:
    """Load a single YAML file and return a validated Company."""
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Company.model_validate(data)


def load_all_companies(data_dir: Path = DATA_DIR) -> list[Company]:
    """Load every ``*.yaml`` file in *data_dir*, sorted by company name."""
    companies: list[Company] = [load_company(p) for p in sorted(data_dir.glob("*.yaml"))]
    return sorted(companies, key=lambda c: c.name.lower())
