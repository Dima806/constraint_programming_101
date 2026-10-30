"""Typed settings loaded from ``config/settings.yaml``.

Keeping the knobs (time limits, seeds, default problem sizes) in one typed object
makes every notebook and the Streamlit app reproducible and bounded.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


class Settings(BaseModel):
    """Project-wide solver and problem settings."""

    time_limit_seconds: float = Field(default=10.0, gt=0)
    num_workers: int = Field(default=2, ge=1)
    random_seed: int = 42

    sudoku_box: int = Field(default=3, ge=2)

    roster_num_nurses: int = Field(default=6, ge=1)
    roster_num_days: int = Field(default=7, ge=1)
    roster_min_days_off: int = Field(default=2, ge=0)

    scaling_time_limit_seconds: float = Field(default=5.0, gt=0)


def load_settings(path: Path | None = None) -> Settings:
    """Load settings from YAML, falling back to defaults when the file is absent."""
    path = path or DEFAULT_CONFIG_PATH
    if not path.exists():
        return Settings()
    data = yaml.safe_load(path.read_text()) or {}
    return Settings.model_validate(data)
