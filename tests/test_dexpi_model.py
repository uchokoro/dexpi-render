from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree

import pytest
from pydexpi.dexpi_classes.dexpiModel import DexpiModel

from dexpi_pid_renderer.dexpi_model import (
    DexpiLoadError,
    DexpiModelCache,
    DexpiModelProvider,
    load_dexpi_model,
)

# ============================================================================
# Tests for load_dexpi_model
# ============================================================================


def test_load_dexpi_model_invalid_type() -> None:
    """Raise TypeError when filepath is not a str or Path."""
    invalid_path: Any = 123
    with pytest.raises(TypeError, match="'filepath' must be a `str` or `Path`"):
        load_dexpi_model(invalid_path)


def test_load_dexpi_model_invalid_extension(tmp_path: Path) -> None:
    """Raise ValueError when filepath does not end with .xml."""
    invalid_file = tmp_path / "model.json"
    invalid_file.write_text("{}")

    with pytest.raises(ValueError, match="'filepath' must be a .xml file"):
        load_dexpi_model(invalid_file)


def test_load_dexpi_model_file_not_found(tmp_path: Path) -> None:
    """Raise FileNotFoundError when file does not exist."""
    missing_file = tmp_path / "non_existent.xml"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_dexpi_model(missing_file)


@patch("dexpi_pid_renderer.dexpi_model.ProteusSerializer")
def test_load_dexpi_model_success(
    mock_serializer_cls: MagicMock, tmp_path: Path
) -> None:
    """Successfully load a valid DEXPI model."""
    xml_file = tmp_path / "valid_model.xml"
    xml_file.write_text("<xml></xml>")

    mock_model = MagicMock(spec=DexpiModel)
    mock_serializer_instance = MagicMock()
    mock_serializer_instance.load.return_value = mock_model
    mock_serializer_cls.return_value = mock_serializer_instance

    result = load_dexpi_model(xml_file)

    assert result is mock_model
    mock_serializer_instance.load.assert_called_once_with(tmp_path, "valid_model.xml")


@pytest.mark.parametrize(
    "exception_cls",
    [
        ElementTree.ParseError("syntax error"),
        ValueError("invalid value"),
        AttributeError("missing attr"),
        KeyError("missing key"),
    ],
)
@patch("dexpi_pid_renderer.dexpi_model.ProteusSerializer")
def test_load_dexpi_model_parse_error(
    mock_serializer_cls: MagicMock,
    exception_cls: Exception,
    tmp_path: Path,
) -> None:
    """Raise DexpiLoadError when ProteusSerializer encounters parsing issues."""
    xml_file = tmp_path / "corrupt_model.xml"
    xml_file.write_text("<bad_xml>")

    mock_serializer_instance = MagicMock()
    mock_serializer_instance.load.side_effect = exception_cls
    mock_serializer_cls.return_value = mock_serializer_instance

    with pytest.raises(DexpiLoadError, match="Failed to parse or validate"):
        load_dexpi_model(xml_file)


# ============================================================================
# Tests for DexpiModelCache
# ============================================================================


def test_dexpi_model_cache_operations(tmp_path: Path) -> None:
    """Test get, set, remove, clear, contains, and len operations on DexpiModelCache."""
    cache = DexpiModelCache()
    file_path = tmp_path / "sample.xml"
    mock_model = MagicMock(spec=DexpiModel)

    # Initially empty
    assert len(cache) == 0
    assert file_path not in cache
    assert cache.get(file_path) is None
    assert cache.paths() == ()

    # Set item
    cache.set(file_path, mock_model)
    assert len(cache) == 1
    assert file_path in cache
    assert cache.get(file_path) is mock_model
    assert cache.get(str(file_path)) is mock_model  # Tests string path normalization
    assert cache.paths() == (file_path.resolve(),)

    # Remove item
    cache.remove(file_path)
    assert len(cache) == 0
    assert file_path not in cache

    # Clear items
    cache.set(file_path, mock_model)
    assert len(cache) == 1
    cache.clear()
    assert len(cache) == 0


def test_dexpi_model_cache_contains_and_paths(tmp_path: Path) -> None:
    """Explicitly verify __contains__ and paths method behavior."""
    cache = DexpiModelCache()
    file_1 = tmp_path / "model1.xml"
    file_2 = tmp_path / "model2.xml"
    mock_model = MagicMock(spec=DexpiModel)

    # __contains__ on empty cache
    assert file_1 not in cache
    assert str(file_1) not in cache

    # Populate cache
    cache.set(file_1, mock_model)
    cache.set(file_2, mock_model)

    # __contains__ check with Path and str
    assert file_1 in cache
    assert str(file_1) in cache
    assert file_2 in cache

    # paths() method checks
    cached_paths = cache.paths()
    assert isinstance(cached_paths, tuple)
    assert len(cached_paths) == 2
    assert file_1.resolve() in cached_paths
    assert file_2.resolve() in cached_paths


# ============================================================================
# Tests for DexpiModelProvider
# ============================================================================


def test_dexpi_model_provider_invalid_filepath_type() -> None:
    """Provider raises TypeError for non-path inputs."""
    provider = DexpiModelProvider()
    invalid_path: Any = 123
    with pytest.raises(TypeError, match="'filepath' must be a `str` or `Path`"):
        provider.get(invalid_path)


@patch("dexpi_pid_renderer.dexpi_model.load_dexpi_model")
def test_dexpi_model_provider_get_and_cache(
    mock_load: MagicMock, tmp_path: Path
) -> None:
    """Provider loads model once and retrieves from cache on subsequent calls."""
    xml_file = tmp_path / "model.xml"
    mock_model = MagicMock(spec=DexpiModel)
    mock_load.return_value = mock_model

    provider = DexpiModelProvider()

    # First fetch loads from disk/loader
    res1 = provider.get(xml_file)
    assert res1 is mock_model
    mock_load.assert_called_once_with(xml_file)

    # Second fetch retrieves from cache without calling load_dexpi_model again
    res2 = provider.get(xml_file)
    assert res2 is mock_model
    assert mock_load.call_count == 1


@patch("dexpi_pid_renderer.dexpi_model.load_dexpi_model")
def test_dexpi_model_provider_get_reload(mock_load: MagicMock, tmp_path: Path) -> None:
    """Provider bypasses cache and reloads model when reload=True."""
    xml_file = tmp_path / "model.xml"
    mock_model_1 = MagicMock(spec=DexpiModel)
    mock_model_2 = MagicMock(spec=DexpiModel)
    mock_load.side_effect = [mock_model_1, mock_model_2]

    provider = DexpiModelProvider()

    # Initial load
    res1 = provider.get(xml_file)
    assert res1 is mock_model_1

    # Reload forced
    res2 = provider.get(xml_file, reload=True)
    assert res2 is mock_model_2
    assert mock_load.call_count == 2


@patch("dexpi_pid_renderer.dexpi_model.load_dexpi_model")
def test_dexpi_model_provider_clear(mock_load: MagicMock, tmp_path: Path) -> None:
    """Provider clear flushes cached models."""
    xml_file = tmp_path / "model.xml"
    mock_model = MagicMock(spec=DexpiModel)
    mock_load.return_value = mock_model

    provider = DexpiModelProvider()
    provider.get(xml_file)

    provider.clear()

    # Fetching after clear should trigger load_dexpi_model again
    provider.get(xml_file)
    assert mock_load.call_count == 2
