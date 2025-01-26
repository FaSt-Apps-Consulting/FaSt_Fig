"""Tests for the presets of FaSt_Fig."""

# %%
import json
from pathlib import Path
import numpy as np
import fast_fig


# %%
def test_presets_default() -> None:
    """Test loading presets from default fast_fig_presets.json."""
    json_path = Path("fast_fig_presets.json")
    test_dict = {
        "test": {
            "width": 10,
            "height": 10,
            "fontfamily": "sans-serif",
            "fontsize": 20,
            "linewidth": 5,
        },
    }
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(test_dict, file)

    fig = fast_fig.FFig(template="test")
    assert (
        "test" in fig.presets
    ), "fast_fig_presets.json should generate template test automatically"
    fig.close()


def test_presets_json(tmpdir: str) -> None:
    """Test loading presets from specified filepath."""
    json_path = Path(tmpdir) / "test_presets.json"
    with json_path.open("w", encoding="utf-8") as file:
        file.write('{ "json": { "height": 5, "linewidth": 5} }')
    fig = fast_fig.FFig(template="json", presets=json_path)
    assert "json" in fig.presets, "JSON file should generate a template json"
    fig.plot()
    fig.plot()
    fig.close()


def test_presets_dict() -> None:
    """Test preset with dictionary and undefined color name."""
    fig = fast_fig.FFig(
        presets={
            "colors": {
                "orange": [255, 89, 27],
                "yellow": [200, 187, 8],
                "grey": [64, 64, 64],
            },
            "color_seq": ["yellow", "orange", "crazy"],
        },
    )
    fig.plot()
    fig.plot()
    assert fig.colors["orange"][0] == 1, "Orange color should have first RGB value of 1"
    assert np.isclose(fig.handle_plot[0].get_color()[0],200/255), "First plot should be yellow"
    assert np.isclose(fig.handle_plot[1].get_color()[0],1), "Second plot should be orange"
    fig.close()


def test_presets_example(tmpdir: str) -> None:
    """Test generation of presets example."""
    json_path = Path(tmpdir) / "test_presets_example.json"
    fast_fig.presets.generate_example(filepath=json_path)
    assert json_path.is_file(), f"Generate preset example should generate {json_path}"


def test_presets_nofile() -> None:
    """Test correct error handling for missing file."""
    fig = fast_fig.FFig(presets="fast_fig_nofile.json")
    fig.plot()
    fig.close()
