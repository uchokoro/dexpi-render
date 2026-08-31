from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from dexpi_pid_renderer import DrawingOutputFormat
from dexpi_pid_renderer.export import (
    FORMAT_TO_SAVER_MAP,
    export_dexpi_to_drawing_file,
)


class TestExportDexpiToDrawingFile:
    def test_export_svg(
        self,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
    ) -> None:
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / "drawing.svg"
        mock_model = mock_dexpi_model_provider.get.return_value

        mock_save_svg = MagicMock(return_value=output_filepath)

        with patch.dict(FORMAT_TO_SAVER_MAP, {"svg": mock_save_svg}):
            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
                padding=0.5,
                pretty_formatting=True,
                add_background_box=True,
                page_size="A3",
                orientation="portrait",
                resolution_scaling_factor=2,
                jpg_quality_factor=90,
                create_output_directory=True,
                dexpi_parser_provider=mock_dexpi_model_provider,
            )

        assert result == output_filepath

        mock_dexpi_model_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_save_svg.assert_called_once_with(
            dexpi_model=mock_model,
            output_path=output_filepath,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
            page_size="A3",
            orientation="portrait",
            resolution_scaling_factor=2,
            jpg_quality_factor=90,
            create_output_directory=True,
        )

    @pytest.mark.parametrize(
        "output_format",
        ["pdf", "png", "jpg", "jpeg"],
    )
    def test_export_supported_format_uses_mapped_saver(
        self,
        output_format: DrawingOutputFormat,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
    ) -> None:
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / f"drawing.{output_format}"
        mock_model = mock_dexpi_model_provider.get.return_value

        mock_saver = MagicMock(return_value=output_filepath)

        with patch.dict(
            FORMAT_TO_SAVER_MAP,
            {output_format: mock_saver},
        ):
            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format=output_format,
                padding=0.5,
                pretty_formatting=True,
                add_background_box=True,
                page_size="A3",
                orientation="portrait",
                resolution_scaling_factor=2,
                jpg_quality_factor=90,
                create_output_directory=True,
                dexpi_parser_provider=mock_dexpi_model_provider,
            )

        assert result == output_filepath

        mock_dexpi_model_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_saver.assert_called_once_with(
            dexpi_model=mock_model,
            output_path=output_filepath,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
            page_size="A3",
            orientation="portrait",
            resolution_scaling_factor=2,
            jpg_quality_factor=90,
            create_output_directory=True,
        )

    @pytest.mark.parametrize(
        "output_format",
        ["doc", "xlsx", "json", "txt", ""],
    )
    def test_unsupported_output_format_raises_value_error(
        self,
        output_format: str,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
    ) -> None:
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / f"drawing.{output_format}"

        with pytest.raises(
            ValueError,
            match=f"Unsupported drawing output format: {output_format!r}",
        ):
            drawing_file_format: Any = output_format

            export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format=drawing_file_format,
                dexpi_parser_provider=mock_dexpi_model_provider,
            )

        mock_dexpi_model_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )

    def test_default_provider_is_created(
        self,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
    ) -> None:
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / "drawing.svg"

        mock_saver = MagicMock(return_value=output_filepath)

        with (
            patch("dexpi_pid_renderer.export.DexpiModelProvider") as mock_provider_cls,
            patch.dict(
                FORMAT_TO_SAVER_MAP,
                {"svg": mock_saver},
            ),
        ):
            mock_provider_cls.return_value = mock_dexpi_model_provider

            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
            )

        assert result == output_filepath

        mock_provider_cls.assert_called_once_with()
        mock_dexpi_model_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_saver.assert_called_once()

    def test_supplied_provider_is_used(
        self,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
    ) -> None:
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / "drawing.svg"

        mock_saver = MagicMock(return_value=output_filepath)

        with (
            patch("dexpi_pid_renderer.export.DexpiModelProvider") as mock_provider_cls,
            patch.dict(
                FORMAT_TO_SAVER_MAP,
                {"svg": mock_saver},
            ),
        ):
            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
                dexpi_parser_provider=mock_dexpi_model_provider,
            )

        assert result == output_filepath

        mock_provider_cls.assert_not_called()
        mock_dexpi_model_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_saver.assert_called_once()
