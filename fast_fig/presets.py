"""Functions to define, validate and generate presets."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_PRESETS = pdict = {
    "color_seq": ["blue", "red", "green", "orange"],
    "linestyle_seq": ["-", "--", ":", "-."],
    "m": {
        "width": 15,
        "height": 10,
        "fontfamily": "sans-serif",
        "fontsize": 12,
        "linewidth": 2,
    },
    "s": {
        "width": 10,
        "height": 8,
        "fontfamily": "sans-serif",
        "fontsize": 12,
        "linewidth": 2,
    },
    "l": {
        "width": 20,
        "height": 15,
        "fontfamily": "sans-serif",
        "fontsize": 12,
        "linewidth": 3,
    },
    "ol": {
        "width": 8,
        "height": 6,
        "fontfamily": "serif",
        "fontsize": 9,
        "linewidth": 1,
    },
    "oe": {
        "width": 12,
        "height": 8,
        "fontfamily": "serif",
        "fontsize": 10,
        "linewidth": 1,
    },
    "square": {
        "width": 10,
        "height": 10,
        "fontfamily": "serif",
        "fontsize": 10,
        "linewidth": 1,
    },
    "colors": {
        "blue": [33, 101, 146],
        "red": [218, 4, 19],
        "green": [70, 173, 52],
        "orange": [235, 149, 0],
        "yellow": [255, 242, 0],
        "grey": [64, 64, 64],
    },
}


def define_presets(presets: dict | str | Path | None = None) -> dict:
    """Define default presets for fast_fig."""
    # define defaults in preset dictionary
    pdict = DEFAULT_PRESETS.copy()

    # Overwrite defaults with presets from fast_fig_presets.json
    if Path("fast_fig_presets.json").is_file():
        pdict.update(load_json("fast_fig_presets.json"))

    # Overwrite defaults with presets from given JSON file
    if isinstance(presets, (str, Path)) and Path(presets).is_file():
        pdict.update(load_json(presets))

    # Overwrite defaults with specific values
    if isinstance(presets, dict):
        pdict.update(presets)

    for key in pdict:
        if key not in ["colors", "color_seq", "linestyle_seq", "linewidth_seq"]:
            pdict[key] = fill_preset(pdict[key])

    return pdict


def fill_preset(preset: dict) -> dict:
    """Fill incomplete preset with defaults."""
    preset.setdefault("width", 15)
    preset.setdefault("height", 10)
    preset.setdefault("fontfamily", "sans-serif")
    preset.setdefault("fontsize", 12)
    preset.setdefault("linewidth", 2)
    return preset


def load_json(filepath: str | Path) -> dict:
    """Load a preset from a JSON file.

    Args:
    ----
        filepath (Union[str, Path]): JSON file path.

    Returns:
    -------
        dict: Loaded JSON data.

    Raises:
    ------
        FileNotFoundError: If the file is not found.
        IOError: If there's an error reading the file.
        json.JSONDecodeError: If the JSON structure is invalid.

    """
    filepath = Path(filepath)
    try:
        with filepath.open(mode="r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        msg = f"File not found: '{filepath}'"
        raise FileNotFoundError(msg) from e
    except OSError as e:
        msg = f"Error reading file: '{filepath}'"
        raise OSError(msg) from e
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON structure in file: '{filepath}'"
        raise json.JSONDecodeError(msg, e.doc, e.pos) from e
    return data


def generate_example(filepath: str = "fast_fig_presets_example.json") -> None:
    """Generate a preset example that can be modified for custom presets.

    Args:
    ----
        filepath (str, optional): Path to generated JSON file.

    """
    example_dict = define_presets()
    # write example_dict to JSON file
    with Path(filepath).open("w", encoding="utf-8") as file:
        json.dump(example_dict, file)
