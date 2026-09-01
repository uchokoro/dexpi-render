from __future__ import annotations

import base64
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from dexpi_pid_renderer.pid_rendering import (
    _build_page_size,
    _create_pid_drawer,
    convert_pdf_bytes_to_pixmap,
    convert_svg_bytes_to_pdf,
    render_pid_as_svg,
    resolve_output_filepath,
    wrap_svg_bytes_into_html,
)


class TestHelperFunctions:
    def test_build_page_size(self) -> None:
        result = _build_page_size("A4", "landscape")

        assert result == "A4 landscape"

    def test_wrap_svg_bytes_into_html(self) -> None:
        raw_svg = b"<svg><rect /></svg>"

        html = wrap_svg_bytes_into_html(
            raw_svg,
            page_size="A3",
            orientation="portrait",
        )

        assert "size: A3 portrait;" in html
        assert "margin: 0;" in html
        assert "data:image/svg+xml;base64," in html

    def test_wrap_svg_bytes_into_html_embeds_svg_data(self) -> None:
        raw_svg = b"<svg><rect /></svg>"

        html = wrap_svg_bytes_into_html(raw_svg)

        encoded_svg = base64.b64encode(raw_svg).decode("utf-8")

        assert encoded_svg in html

    def test_create_pid_drawer(
        self,
        mock_dexpi_model: MagicMock,
    ) -> None:
        with patch("dexpi_pid_renderer.pid_rendering.DrawDiagram") as mock_draw_diagram:
            result = _create_pid_drawer(
                mock_dexpi_model,
                padding=1.0,
                pretty_formatting=True,
            )

        assert result is mock_draw_diagram.return_value

        mock_draw_diagram.assert_called_once_with(
            mock_dexpi_model.diagram,
            padding=1.0,
            pretty=True,
        )


class TestResolveOutputFilepath:
    def test_valid_filepath_str_and_path(
        self,
        tmp_path: Path,
    ) -> None:
        target_path = tmp_path / "output.svg"

        result_from_str = resolve_output_filepath(
            str(target_path),
            "svg",
        )
        result_from_path = resolve_output_filepath(
            target_path,
            "svg",
        )

        assert result_from_str == target_path
        assert result_from_path == target_path

    def test_invalid_filepath_type_raises_type_error(self) -> None:
        with pytest.raises(
            TypeError,
            match="'filepath' must be a `str` or a `Path`.",
        ):
            invalid_path: Any = 12345

            resolve_output_filepath(
                invalid_path,
                "svg",
            )

    def test_invalid_extension_raises_value_error(
        self,
        tmp_path: Path,
    ) -> None:
        target_path = tmp_path / "output.png"

        with pytest.raises(
            ValueError,
            match="'filepath' must have a '.svg' extension.",
        ):
            resolve_output_filepath(
                target_path,
                "svg",
            )

    def test_extension_check_is_case_insensitive(
        self,
        tmp_path: Path,
    ) -> None:
        target_path = tmp_path / "output.SVG"

        result = resolve_output_filepath(
            target_path,
            "svg",
        )

        assert result == target_path

    def test_missing_directory_without_create_flag_raises_not_a_directory_error(
        self,
        tmp_path: Path,
    ) -> None:
        target_path = tmp_path / "nested_folder" / "output.pdf"

        with pytest.raises(
            NotADirectoryError,
            match="No directory corresponding to output path's parent found.",
        ):
            resolve_output_filepath(
                target_path,
                "pdf",
                create_output_directory=False,
            )

    def test_missing_directory_with_create_flag_creates_directory(
        self,
        tmp_path: Path,
    ) -> None:
        target_path = tmp_path / "nested_folder" / "sub" / "output.pdf"

        result = resolve_output_filepath(
            target_path,
            "pdf",
            create_output_directory=True,
        )

        assert result == target_path
        assert target_path.parent.is_dir()


class TestRenderPidAsSvg:
    def test_render_pid_as_svg(
        self,
        mock_dexpi_model: MagicMock,
    ) -> None:
        mock_svg_string = "<svg>P&ID Content</svg>"

        with patch("dexpi_pid_renderer.pid_rendering.DrawDiagram") as mock_draw_diagram:
            mock_drawer = MagicMock()
            mock_drawer.draw_svg.return_value = mock_svg_string
            mock_draw_diagram.return_value = mock_drawer

            result = render_pid_as_svg(
                dexpi_model=mock_dexpi_model,
                padding=0.5,
                pretty_formatting=True,
                add_background_box=True,
            )

        assert result == mock_svg_string.encode("utf-8")

        mock_draw_diagram.assert_called_once_with(
            mock_dexpi_model.diagram,
            padding=0.5,
            pretty=True,
        )
        mock_drawer.draw_svg.assert_called_once_with(
            return_element=False,
            background=True,
        )


class TestConvertSvgBytesToPdf:
    @patch("dexpi_pid_renderer.pid_rendering.HTML")
    def test_convert_svg_bytes_to_pdf(
        self,
        mock_html_class: MagicMock,
    ) -> None:
        svg_bytes = b"<svg></svg>"
        pdf_bytes = b"%PDF-1.4 Mock Bytes"

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = pdf_bytes
        mock_html_class.return_value = mock_html_instance

        result = convert_svg_bytes_to_pdf(
            svg_bytes,
            page_size="A4",
            orientation="landscape",
        )

        assert result == pdf_bytes

        mock_html_class.assert_called_once()
        mock_html_instance.write_pdf.assert_called_once()

    @patch("dexpi_pid_renderer.pid_rendering.HTML")
    def test_convert_svg_bytes_to_pdf_uses_page_configuration(
        self,
        mock_html_class: MagicMock,
    ) -> None:
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF"
        mock_html_class.return_value = mock_html_instance

        svg_bytes = b"<svg></svg>"

        convert_svg_bytes_to_pdf(
            svg_bytes,
            page_size="A3",
            orientation="portrait",
        )

        html_content = mock_html_class.call_args.kwargs["string"]

        assert "size: A3 portrait;" in html_content

    @patch("dexpi_pid_renderer.pid_rendering.HTML")
    def test_convert_svg_bytes_to_pdf_raises_when_conversion_returns_none(
        self,
        mock_html_class: MagicMock,
    ) -> None:
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None
        mock_html_class.return_value = mock_html_instance

        with pytest.raises(
            RuntimeError,
            match="Error converting SVG data to PDF.",
        ):
            convert_svg_bytes_to_pdf(b"<svg></svg>")


class TestConvertPdfBytesToPixmap:
    def test_convert_pdf_bytes_to_pixmap(
        self,
    ) -> None:
        pdf_bytes = b"%PDF-1.4 Mock Bytes"

        mock_page_1 = MagicMock()
        mock_page_2 = MagicMock()

        mock_pixmap_1 = MagicMock()
        mock_pixmap_2 = MagicMock()

        mock_page_1.get_pixmap.return_value = mock_pixmap_1
        mock_page_2.get_pixmap.return_value = mock_pixmap_2

        mock_document = MagicMock()
        mock_document.__enter__.return_value = mock_document
        mock_document.__len__.return_value = 2
        mock_document.load_page.side_effect = [
            mock_page_1,
            mock_page_2,
        ]

        with (
            patch(
                "dexpi_pid_renderer.pid_rendering.pymupdf.open",
                return_value=mock_document,
            ),
            patch("dexpi_pid_renderer.pid_rendering.pymupdf.Matrix") as mock_matrix,
        ):
            result = convert_pdf_bytes_to_pixmap(
                pdf_bytes=pdf_bytes,
                resolution_scaling_factor=2,
            )

        assert result == (
            mock_pixmap_1,
            mock_pixmap_2,
        )

        mock_document.load_page.assert_any_call(0)
        mock_document.load_page.assert_any_call(1)

        mock_matrix.assert_called_with(2, 2)

        mock_page_1.get_pixmap.assert_called_once_with(
            matrix=mock_matrix.return_value,
        )
        mock_page_2.get_pixmap.assert_called_once_with(
            matrix=mock_matrix.return_value,
        )

    @pytest.mark.parametrize(
        "resolution_scaling_factor",
        [1, 2],
    )
    def test_convert_pdf_bytes_to_pixmap_accepts_valid_scaling_factors(
        self,
        resolution_scaling_factor: int,
    ) -> None:
        pdf_bytes = b"%PDF-1.4 Mock Bytes"

        mock_document = MagicMock()
        mock_document.__len__.return_value = 0

        with patch(
            "dexpi_pid_renderer.pid_rendering.pymupdf.open",
            return_value=mock_document,
        ):
            result = convert_pdf_bytes_to_pixmap(
                pdf_bytes=pdf_bytes,
                resolution_scaling_factor=resolution_scaling_factor,
            )

        assert result == ()

    @pytest.mark.parametrize(
        "resolution_scaling_factor",
        [0, 3, -1],
    )
    def test_convert_pdf_bytes_to_pixmap_rejects_invalid_scaling_factor(
        self,
        resolution_scaling_factor: int,
    ) -> None:
        with pytest.raises(ValueError):
            convert_pdf_bytes_to_pixmap(
                pdf_bytes=b"%PDF-1.4 Mock Bytes",
                resolution_scaling_factor=resolution_scaling_factor,
            )
