"""Tests for the presets of FaSt_Fig."""

# %%
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import yaml

import fast_fig
from fast_fig.presets import define_presets


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
    assert "test" in fig.presets, (
        "fast_fig_presets.json should generate template test automatically"
    )
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
    assert np.isclose(fig.handle_plot[0].get_color()[0], 200 / 255), "First plot should be yellow"
    assert np.isclose(fig.handle_plot[1].get_color()[0], 1), "Second plot should be orange"
    fig.close()


def test_presets_generate_yaml(tmpdir: str) -> None:
    """Test generation of presets example."""
    yaml_path = Path(tmpdir) / "test_presets_example.yaml"

    if fast_fig.presets.YAML_AVAILABLE:
        fast_fig.presets.generate_file(filepath=yaml_path)
        assert yaml_path.is_file(), f"Generate preset example should generate {yaml_path}"

        # Verify YAML content
        with yaml_path.with_suffix(".yaml").open("r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        assert "color_seq" in yaml_data, "YAML should contain color_seq"
        assert "colors" in yaml_data, "YAML should contain colors"


def test_presets_generate_json(tmpdir: str) -> None:
    """Test generation of presets example."""
    json_path = Path(tmpdir) / "test_presets_example.json"
    fast_fig.presets.generate_file(filepath=json_path)
    assert json_path.is_file(), f"Generate preset example should generate {json_path}"


def test_presets_nofile() -> None:
    """Test correct error handling for missing file."""
    fig = fast_fig.FFig(presets="fast_fig_nofile.json")
    fig.plot()
    fig.close()


def test_presets_yaml(tmpdir: str) -> None:
    """Test loading presets from YAML file."""
    yaml_path = Path(tmpdir) / "test_presets.yaml"
    test_config = {"yaml": {"height": 5, "linewidth": 5}}

    with yaml_path.open("w", encoding="utf-8") as file:
        yaml.dump(test_config, file)

    fig = fast_fig.FFig(template="yaml", presets=yaml_path)
    assert "yaml" in fig.presets, "YAML file should generate a template yaml"
    assert fig.presets["yaml"]["height"] == 5, "Height should be 5"
    assert fig.presets["yaml"]["linewidth"] == 5, "Linewidth should be 5"
    fig.close()


def test_presets_yaml_yml_extension(tmpdir: str) -> None:
    """Test loading presets from file with .yml extension."""
    yml_path = Path(tmpdir) / "test_presets.yml"
    test_config = {"yml": {"height": 6, "linewidth": 3}}

    with yml_path.open("w", encoding="utf-8") as file:
        yaml.dump(test_config, file)

    fig = fast_fig.FFig(template="yml", presets=yml_path)
    assert "yml" in fig.presets, "YML file should generate a template yml"
    fig.close()


def test_invalid_yaml(tmpdir: str) -> None:
    """Test handling of invalid YAML file."""
    yaml_path = Path(tmpdir) / "invalid.yaml"

    # Create invalid YAML file
    with yaml_path.open("w", encoding="utf-8") as file:
        file.write("invalid: yaml: : :")

    with pytest.raises(ValueError, match="Invalid file format"):
        fast_fig.presets.load_config(yaml_path)


def test_unsupported_format(tmpdir: str) -> None:
    """Test handling of unsupported file format."""
    bad_path = Path(tmpdir) / "config.txt"
    bad_path.touch()

    with pytest.raises(ValueError, match="Unsupported file format"):
        fast_fig.presets.load_config(bad_path)


def test_yaml_not_available(tmpdir: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test behavior when PyYAML is not available."""
    # Simulate PyYAML not being installed
    monkeypatch.setattr(fast_fig.presets, "YAML_AVAILABLE", False)

    yaml_path = Path(tmpdir) / "test.yaml"
    with yaml_path.open("w", encoding="utf-8") as file:
        file.write("test: value")

    with pytest.raises(ValueError, match="YAML support requires PyYAML"):
        fast_fig.presets.load_config(yaml_path)


def test_define_presets_file_loading(tmp_path: Path) -> None:
    """Test loading presets from files."""
    # Test JSON file
    json_file = tmp_path / "test_presets.json"
    json_data = {"test_preset": {"width": 5, "height": 5}}
    import json  # noqa: PLC0415

    with json_file.open("w") as f:
        json.dump(json_data, f)

    presets = define_presets(json_file)
    assert "test_preset" in presets
    assert presets["test_preset"]["width"] == 5

    # Test YAML file if available
    try:
        import yaml  # noqa: PLC0415

        yaml_file = tmp_path / "test_presets.yaml"
        yaml_data = {"yaml_preset": {"width": 7, "height": 7}}
        with yaml_file.open("w") as f:
            yaml.dump(yaml_data, f)

        presets = define_presets(yaml_file)
        assert "yaml_preset" in presets
        assert presets["yaml_preset"]["width"] == 7
    except ImportError:
        pass


def test_presets_generate_file_boost(tmp_path: Path) -> None:
    """Test generation of preset files."""
    base_path = tmp_path / "test_presets"
    fast_fig.presets.generate_file(str(base_path))

    assert (tmp_path / "test_presets.json").exists()
    # YAML might not be available in all test envs, but let's check if it tried
    if fast_fig.presets.YAML_AVAILABLE:
        assert (tmp_path / "test_presets.yaml").exists()


def test_load_config_os_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test load_config with OS error."""
    test_file = tmp_path / "test.json"
    test_file.write_text("{}")

    # Patch Path.open just for this test
    original_open = Path.open

    def mock_open(self: Path, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if str(self).endswith("test.json"):
            msg = "Mock OS Error"
            raise OSError(msg)
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr("pathlib.Path.open", mock_open)

    with pytest.raises(OSError, match="Error reading file"):
        fast_fig.presets.load_config(test_file)


def test_define_presets_yaml_discovery() -> None:
    """Test define_presets discovering yaml file in CWD."""
    yaml_file = Path("fast_fig_presets.yaml")
    yaml_file.write_text("m: {width: 999}")
    try:
        p = define_presets()
        assert p["m"]["width"] == 999
    finally:
        if yaml_file.exists():
            yaml_file.unlink()


def test_presets_generate_yaml_no_pyyaml(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generate_file raises error when YAML not available."""
    monkeypatch.setattr(fast_fig.presets, "YAML_AVAILABLE", False)
    with pytest.raises(ValueError, match="YAML support requires PyYAML"):
        fast_fig.presets.generate_file("test.yaml")


def test_load_config_file_not_found() -> None:
    """Test load_config with missing file."""
    with pytest.raises(FileNotFoundError):
        fast_fig.presets.load_config("non_existent_file.json")
