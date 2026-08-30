from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import ANY, MagicMock, patch

import pytest

from dexpi_pid_renderer.export import (
    FORMAT_TO_SAVER_MAP,
    export_dexpi_to_drawing_file,
)


class TestExportDexpiToDrawingFile:
    def test_export_svg(self, tmp_path: Path) -> None:
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / "drawing.svg"

        mock_provider = MagicMock()
        mock_model = MagicMock()
        mock_provider.get.return_value = mock_model
        mock_save_svg = MagicMock(return_value=output_filepath)

        with patch.dict(FORMAT_TO_SAVER_MAP, {"svg": mock_save_svg}):
            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
                padding=0.5,
                pretty_formatting=True,
                add_background_box=True,
                create_output_directory=True,
                dexpi_parser_provider=mock_provider,
            )

        assert result == output_filepath
        mock_provider.get.assert_called_once_with(filepath=input_filepath)
        mock_save_svg.assert_called_once_with(
            dexpi_model=mock_model,
            output_path=output_filepath,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
            create_output_directory=True,
            page_size=ANY,
            orientation=ANY,
            resolution_scaling_factor=ANY,
            jpg_quality_factor=ANY,
        )

    def test_export_pdf(
        self,
        tmp_path: Path,
    ) -> None:
        """Exporting as PDF renders the P&ID as SVG before saving it as PDF."""
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / "drawing.pdf"
        svg_data = b"<svg>rendered P&ID</svg>"

        mock_provider = MagicMock()
        mock_model = MagicMock()
        mock_provider.get.return_value = mock_model

        with (
            patch(
                "dexpi_pid_renderer.dexpi_to_image_file.render_pid_as_svg"
            ) as mock_render_svg,
            patch(
                "dexpi_pid_renderer.dexpi_to_image_file.save_svg_bytes_to_pdf"
            ) as mock_save_pdf,
        ):
            mock_render_svg.return_value = svg_data
            mock_save_pdf.return_value = output_filepath

            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format="pdf",
                padding=0.5,
                pretty_formatting=True,
                add_background_box=True,
                page_size="A3",
                orientation="portrait",
                create_output_directory=True,
                dexpi_parser_provider=mock_provider,
            )

        assert result == output_filepath

        mock_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_render_svg.assert_called_once_with(
            dexpi_model=mock_model,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
        )
        mock_save_pdf.assert_called_once_with(
            svg_bytes=svg_data,
            output_path=output_filepath,
            page_size="A3",
            orientation="portrait",
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
    ) -> None:
        """Raise ValueError when an unsupported output format is requested."""
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / f"drawing.{output_format}"

        mock_provider = MagicMock()
        mock_provider.get.return_value = MagicMock()

        with pytest.raises(
            ValueError,
            match=f"Unsupported drawing output format: {output_format!r}",
        ):
            drawing_file_format: Any = output_format
            export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format=drawing_file_format,
                dexpi_parser_provider=mock_provider,
            )

    def test_default_provider_is_created(
        self,
        tmp_path: Path,
    ) -> None:
        """Create a default DexpiModelProvider when none is supplied."""
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / "drawing.svg"

        mock_model = MagicMock()
        mock_save_svg = MagicMock(return_value=output_filepath)

        with (
            patch("dexpi_pid_renderer.export.DexpiModelProvider") as mock_provider_cls,
            patch.dict(
                "dexpi_pid_renderer.export.FORMAT_TO_SAVER_MAP", {"svg": mock_save_svg}
            ),
        ):
            mock_provider = MagicMock()
            mock_provider.get.return_value = mock_model
            mock_provider_cls.return_value = mock_provider

            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
            )

        assert result == output_filepath

        mock_provider_cls.assert_called_once_with()
        mock_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
        mock_save_svg.assert_called_once()

    def test_supplied_provider_is_used(
        self,
        tmp_path: Path,
    ) -> None:
        """Use the supplied provider instead of creating a default provider."""
        input_filepath = tmp_path / "model.xml"
        output_filepath = tmp_path / "drawing.svg"

        mock_provider = MagicMock()
        mock_model = MagicMock()
        mock_provider.get.return_value = mock_model

        with (
            patch("dexpi_pid_renderer.export.DexpiModelProvider") as mock_provider_cls,
            patch("dexpi_pid_renderer.export.save_pid_as_svg") as mock_save_svg,
        ):
            mock_save_svg.return_value = output_filepath

            result = export_dexpi_to_drawing_file(
                filepath=input_filepath,
                output_filepath=output_filepath,
                output_format="svg",
                dexpi_parser_provider=mock_provider,
            )

        assert result == output_filepath

        mock_provider_cls.assert_not_called()
        mock_provider.get.assert_called_once_with(
            filepath=input_filepath,
        )
