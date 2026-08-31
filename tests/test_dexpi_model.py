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


class TestLoadDexpiModel:
    def test_invalid_filepath_type(self) -> None:
        invalid_path: Any = 123

        with pytest.raises(
            TypeError,
            match="'filepath' must be a `str` or `Path`",
        ):
            load_dexpi_model(invalid_path)

    def test_invalid_extension(self, tmp_path: Path) -> None:
        invalid_file = tmp_path / "model.json"
        invalid_file.write_text("{}")

        with pytest.raises(
            ValueError,
            match="'filepath' must be a .xml file",
        ):
            load_dexpi_model(invalid_file)

    def test_file_not_found(self, tmp_path: Path) -> None:
        missing_file = tmp_path / "non_existent.xml"

        with pytest.raises(
            FileNotFoundError,
            match="does not exist",
        ):
            load_dexpi_model(missing_file)

    @patch("dexpi_pid_renderer.dexpi_model.ProteusSerializer")
    def test_success(
        self,
        mock_serializer_cls: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        xml_file = tmp_path / "valid_model.xml"
        xml_file.write_text("<xml></xml>")

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.load.return_value = mock_dexpi_model
        mock_serializer_cls.return_value = mock_serializer_instance

        result = load_dexpi_model(xml_file)

        assert result is mock_dexpi_model
        mock_serializer_instance.load.assert_called_once_with(
            tmp_path,
            "valid_model.xml",
        )

    @pytest.mark.parametrize(
        "exception",
        [
            ElementTree.ParseError("syntax error"),
            ValueError("invalid value"),
            AttributeError("missing attr"),
            KeyError("missing key"),
        ],
    )
    @patch("dexpi_pid_renderer.dexpi_model.ProteusSerializer")
    def test_parse_error(
        self,
        mock_serializer_cls: MagicMock,
        exception: Exception,
        tmp_path: Path,
    ) -> None:
        xml_file = tmp_path / "corrupt_model.xml"
        xml_file.write_text("<bad_xml>")

        mock_serializer_instance = MagicMock()
        mock_serializer_instance.load.side_effect = exception
        mock_serializer_cls.return_value = mock_serializer_instance

        with pytest.raises(
            DexpiLoadError,
            match="Failed to parse or validate",
        ):
            load_dexpi_model(xml_file)


class TestDexpiModelCache:
    def test_initial_state(self, tmp_path: Path) -> None:
        cache = DexpiModelCache()
        file_path = tmp_path / "sample.xml"

        assert len(cache) == 0
        assert file_path not in cache
        assert cache.get(file_path) is None
        assert cache.paths() == ()

    def test_set_and_get(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        cache = DexpiModelCache()
        file_path = tmp_path / "sample.xml"

        cache.set(file_path, mock_dexpi_model)

        assert cache.get(file_path) is mock_dexpi_model
        assert len(cache) == 1

    def test_path_normalization(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        cache = DexpiModelCache()
        file_path = tmp_path / "sample.xml"

        cache.set(file_path, mock_dexpi_model)

        assert cache.get(str(file_path)) is mock_dexpi_model
        assert str(file_path) in cache
        assert file_path in cache

    def test_remove(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        cache = DexpiModelCache()
        file_path = tmp_path / "sample.xml"

        cache.set(file_path, mock_dexpi_model)
        cache.remove(file_path)

        assert cache.get(file_path) is None
        assert file_path not in cache
        assert len(cache) == 0

    def test_remove_nonexistent_path(self, tmp_path: Path) -> None:
        cache = DexpiModelCache()
        file_path = tmp_path / "non_existent.xml"

        cache.remove(file_path)

        assert len(cache) == 0

    def test_clear(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        cache = DexpiModelCache()
        file_1 = tmp_path / "model1.xml"
        file_2 = tmp_path / "model2.xml"

        cache.set(file_1, mock_dexpi_model)
        cache.set(file_2, mock_dexpi_model)

        cache.clear()

        assert len(cache) == 0
        assert cache.paths() == ()

    def test_contains(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        cache = DexpiModelCache()
        file_path = tmp_path / "sample.xml"

        assert file_path not in cache

        cache.set(file_path, mock_dexpi_model)

        assert file_path in cache
        assert str(file_path) in cache

    def test_paths(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        cache = DexpiModelCache()
        file_1 = tmp_path / "model1.xml"
        file_2 = tmp_path / "model2.xml"

        cache.set(file_1, mock_dexpi_model)
        cache.set(file_2, mock_dexpi_model)

        paths = cache.paths()

        assert isinstance(paths, tuple)
        assert len(paths) == 2
        assert file_1.resolve() in paths
        assert file_2.resolve() in paths

    def test_len(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        cache = DexpiModelCache()
        file_1 = tmp_path / "model1.xml"
        file_2 = tmp_path / "model2.xml"

        assert len(cache) == 0

        cache.set(file_1, mock_dexpi_model)
        assert len(cache) == 1

        cache.set(file_2, mock_dexpi_model)
        assert len(cache) == 2

        cache.remove(file_1)
        assert len(cache) == 1


class TestDexpiModelProvider:
    def test_invalid_filepath_type(self) -> None:
        provider = DexpiModelProvider()
        invalid_path: Any = 123

        with pytest.raises(
            TypeError,
            match="'filepath' must be a `str` or `Path`",
        ):
            provider.get(invalid_path)

    @patch("dexpi_pid_renderer.dexpi_model.load_dexpi_model")
    def test_get_loads_model(
        self,
        mock_load: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        xml_file = tmp_path / "model.xml"
        mock_load.return_value = mock_dexpi_model

        provider = DexpiModelProvider()

        result = provider.get(xml_file)

        assert result is mock_dexpi_model
        mock_load.assert_called_once_with(xml_file)

    @patch("dexpi_pid_renderer.dexpi_model.load_dexpi_model")
    def test_get_returns_cached_model(
        self,
        mock_load: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        xml_file = tmp_path / "model.xml"
        mock_load.return_value = mock_dexpi_model

        provider = DexpiModelProvider()

        first_result = provider.get(xml_file)
        second_result = provider.get(xml_file)

        assert first_result is mock_dexpi_model
        assert second_result is mock_dexpi_model
        mock_load.assert_called_once_with(xml_file)

    @patch("dexpi_pid_renderer.dexpi_model.load_dexpi_model")
    def test_get_reload_bypasses_cache(
        self,
        mock_load: MagicMock,
        tmp_path: Path,
    ) -> None:
        xml_file = tmp_path / "model.xml"
        mock_model_1 = MagicMock(spec=DexpiModel)
        mock_model_2 = MagicMock(spec=DexpiModel)
        mock_load.side_effect = [mock_model_1, mock_model_2]

        provider = DexpiModelProvider()

        first_result = provider.get(xml_file)
        second_result = provider.get(xml_file, reload=True)

        assert first_result is mock_model_1
        assert second_result is mock_model_2
        assert mock_load.call_count == 2

    @patch("dexpi_pid_renderer.dexpi_model.load_dexpi_model")
    def test_clear(
        self,
        mock_load: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        xml_file = tmp_path / "model.xml"
        mock_load.return_value = mock_dexpi_model

        provider = DexpiModelProvider()

        provider.get(xml_file)
        provider.clear()
        provider.get(xml_file)

        assert mock_load.call_count == 2
