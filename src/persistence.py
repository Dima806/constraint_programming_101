"""Persist notebook artefacts to disk.

The notebooks save every figure as a PNG under ``outputs/figures/`` and every
textual/numerical input (problem instances, boards, sweep tables) as JSON under
``outputs/data/``, so every result in the repo is reproducible and inspectable
outside a running kernel.
"""

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from matplotlib.figure import Figure

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
DATA_DIR = PROJECT_ROOT / "outputs" / "data"


def to_jsonable(obj: Any) -> Any:
    """Convert dataclasses, tuples, and non-string dict keys into JSON-safe values."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return to_jsonable(asdict(obj))
    if isinstance(obj, dict):
        return {str(key): to_jsonable(value) for key, value in obj.items()}
    if isinstance(obj, list | tuple):
        return [to_jsonable(value) for value in obj]
    return obj


def save_json(name: str, data: Any, *, directory: Path = DATA_DIR) -> Path:
    """Write ``data`` as pretty JSON to ``<directory>/<name>.json`` and return the path."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(to_jsonable(data), indent=2) + "\n")
    return path


def save_figure(name: str, fig: Figure, *, directory: Path = FIGURES_DIR, dpi: int = 150) -> Path:
    """Save a Matplotlib figure as ``<directory>/<name>.png`` and return the path."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
