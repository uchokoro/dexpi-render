from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, create_autospec, patch

import pytest

from dexpi_pid_renderer import (
    DrawingOutputFormat,
    save_pid_as_jpg,
    save_pid_as_pdf,
    save_pid_as_png,
)
from dexpi_pid_renderer.export import (
    FORMAT_TO_SAVER_MAP,
    FormatSaver,
    _filter_saver_arguments,
    export_dexpi_to_drawing_file,
)


class TestFilterSaverArguments:
    def test_filters_arguments_not_supported_by_saver(self) -> None:
        def saver(
            *,
            dexpi_model: Any,
            output_path: str | Path,
            padding: float,
        ) -> Path:
            _ = dexpi_model, padding
            return Path(output_path)

        arguments = {
            "dexpi_model": "model",
            "output_path": "output.svg",
            "padding": 0.5,
            "pretty_formatting": True,
            "add_background_box": True,
            "page_size": "A3",
            "orientation": "portrait",
            "resolution_scaling_factor": 2,
            "jpg_quality_factor": 90,
            "create_output_directory": True,
        }

        filtered_arguments = _filter_saver_arguments(
            saver,
            arguments,
        )

        assert filtered_arguments == {
            "dexpi_model": "model",
            "output_path": "output.svg",
            "padding": 0.5,
        }

    def test_preserves_all_arguments_supported_by_saver(self) -> None:
        def saver(
            *,
            dexpi_model: Any,
            output_path: str | Path,
            padding: float,
            pretty_formatting: bool,
            add_background_box: bool,
            page_size: str,
            orientation: str,
            resolution_scaling_factor: int,
            jpg_quality_factor: int,
            create_output_directory: bool,
        ) -> Path:
            _ = (
                dexpi_model,
                padding,
                pretty_formatting,
                add_background_box,
                page_size,
                orientation,
                resolution_scaling_factor,
                jpg_quality_factor,
                create_output_directory,
            )
            return Path(output_path)

        arguments = {
            "dexpi_model": "model",
            "output_path": "output.jpg",
            "padding": 0.5,
            "pretty_formatting": True,
            "add_background_box": True,
            "page_size": "A3",
            "orientation": "portrait",
            "resolution_scaling_factor": 2,
            "jpg_quality_factor": 90,
            "create_output_directory": True,
        }

        filtered_arguments = _filter_saver_arguments(
            saver,
            arguments,
        )

        assert filtered_arguments == arguments


class TestExportDexpiToDrawingFile:
    def test_export_svg(
        self,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
    ) -> None:
        input_filepath = tmp_path / "input.xml"
        output_filepath = tmp_path / "output.svg"

        mock_model = mock_dexpi_model_provider.get.return_value
        mock_save_svg = MagicMock(return_value=output_filepath)

        def save_svg(
            *,
            dexpi_model: Any,
            output_path: str | Path,
            padding: float,
            pretty_formatting: bool,
            add_background_box: bool,
            create_output_directory: bool,
        ) -> Path:
            saved_filepath: Path = mock_save_svg(
                dexpi_model=dexpi_model,
                output_path=output_path,
                padding=padding,
                pretty_formatting=pretty_formatting,
                add_background_box=add_background_box,
                create_output_directory=create_output_directory,
            )
            return saved_filepath

        with patch.dict(FORMAT_TO_SAVER_MAP, {"svg": save_svg}):
            result = export_dexpi_to_drawing_file(
                input_filepath,
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
            create_output_directory=True,
        )

    @pytest.mark.parametrize(
        ("output_format", "saver", "format_arguments"),
        [
            (
                "pdf",
                save_pid_as_pdf,
                {
                    "page_size": "A3",
                    "orientation": "portrait",
                },
            ),
            (
                "png",
                save_pid_as_png,
                {
                    "page_size": "A3",
                    "orientation": "portrait",
                    "resolution_scaling_factor": 2,
                },
            ),
            (
                "jpg",
                save_pid_as_jpg,
                {
                    "page_size": "A3",
                    "orientation": "portrait",
                    "resolution_scaling_factor": 2,
                    "jpg_quality_factor": 90,
                },
            ),
            (
                "jpeg",
                save_pid_as_jpg,
                {
                    "page_size": "A3",
                    "orientation": "portrait",
                    "resolution_scaling_factor": 2,
                    "jpg_quality_factor": 90,
                },
            ),
        ],
    )
    def test_export_supported_format_uses_mapped_saver(
        self,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
        output_format: DrawingOutputFormat,
        saver: FormatSaver,
        format_arguments: dict[str, Any],
    ) -> None:
        input_filepath = tmp_path / "input.xml"
        output_filepath = tmp_path / f"output.{output_format}"

        mock_model = mock_dexpi_model_provider.get.return_value
        mock_saver = create_autospec(saver, return_value=output_filepath)

        with patch.dict(FORMAT_TO_SAVER_MAP, {output_format: mock_saver}):
            result = export_dexpi_to_drawing_file(
                input_filepath,
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
            create_output_directory=True,
            **format_arguments,
        )

    @pytest.mark.parametrize(
        "output_format",
        ["doc", "xlsx", "json", "txt", ""],
    )
    def test_unsupported_output_format_raises_value_error(
        self,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
        output_format: str,
    ) -> None:
        input_filepath = tmp_path / "input.xml"
        output_filepath = tmp_path / "output"

        with pytest.raises(
            ValueError,
            match=f"Unsupported drawing output format: {output_format!r}",
        ):
            drawing_file_format: Any = output_format
            export_dexpi_to_drawing_file(
                input_filepath,
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
        input_filepath = tmp_path / "input.xml"
        output_filepath = tmp_path / "output.svg"

        mock_model = mock_dexpi_model_provider.get.return_value
        mock_saver = MagicMock(return_value=output_filepath)

        def save_svg(
            *,
            dexpi_model: Any,
            output_path: str | Path,
            padding: float,
            pretty_formatting: bool,
            add_background_box: bool,
            create_output_directory: bool,
        ) -> Path:
            saved_filepath: Path = mock_saver(
                dexpi_model=dexpi_model,
                output_path=output_path,
                padding=padding,
                pretty_formatting=pretty_formatting,
                add_background_box=add_background_box,
                create_output_directory=create_output_directory,
            )
            return saved_filepath

        with (
            patch(
                "dexpi_pid_renderer.export.DexpiModelProvider",
                return_value=mock_dexpi_model_provider,
            ) as mock_provider_class,
            patch.dict(FORMAT_TO_SAVER_MAP, {"svg": save_svg}),
        ):
            result = export_dexpi_to_drawing_file(
                input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
            )

        assert result == output_filepath

        mock_provider_class.assert_called_once_with()
        mock_dexpi_model_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_saver.assert_called_once_with(
            dexpi_model=mock_model,
            output_path=output_filepath,
            padding=0.0,
            pretty_formatting=False,
            add_background_box=False,
            create_output_directory=False,
        )

    def test_supplied_provider_is_used(
        self,
        tmp_path: Path,
        mock_dexpi_model_provider: MagicMock,
    ) -> None:
        input_filepath = tmp_path / "input.xml"
        output_filepath = tmp_path / "output.svg"

        mock_model = mock_dexpi_model_provider.get.return_value
        mock_saver = MagicMock(return_value=output_filepath)

        def save_svg(
            *,
            dexpi_model: Any,
            output_path: str | Path,
            padding: float,
            pretty_formatting: bool,
            add_background_box: bool,
            create_output_directory: bool,
        ) -> Path:
            saved_filepath: Path = mock_saver(
                dexpi_model=dexpi_model,
                output_path=output_path,
                padding=padding,
                pretty_formatting=pretty_formatting,
                add_background_box=add_background_box,
                create_output_directory=create_output_directory,
            )
            return saved_filepath

        with (
            patch(
                "dexpi_pid_renderer.export.DexpiModelProvider",
            ) as mock_provider_class,
            patch.dict(FORMAT_TO_SAVER_MAP, {"svg": save_svg}),
        ):
            result = export_dexpi_to_drawing_file(
                input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
                dexpi_parser_provider=mock_dexpi_model_provider,
            )

        assert result == output_filepath

        mock_provider_class.assert_not_called()
        mock_dexpi_model_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_saver.assert_called_once_with(
            dexpi_model=mock_model,
            output_path=output_filepath,
            padding=0.0,
            pretty_formatting=False,
            add_background_box=False,
            create_output_directory=False,
        )
