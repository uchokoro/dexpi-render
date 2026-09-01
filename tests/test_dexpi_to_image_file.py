# tests/test_dexpi_to_image_file.py
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dexpi_pid_renderer.dexpi_to_image_file import (
    save_pdf_bytes_to_jpg,
    save_pdf_bytes_to_png,
    save_pid_as_jpg,
    save_pid_as_pdf,
    save_pid_as_png,
    save_pid_as_svg,
    save_svg_bytes_to_pdf,
    save_svg_bytes_to_svg,
)


class TestSaveSvgBytesToSvg:
    def test_save_svg_bytes_to_svg(
        self,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.svg"
        svg_bytes = b"<svg>test</svg>"

        result = save_svg_bytes_to_svg(
            svg_bytes=svg_bytes,
            output_path=output_path,
        )

        assert result == output_path
        assert output_path.read_bytes() == svg_bytes

    def test_save_svg_bytes_to_svg_creates_output_directory(
        self,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "nested" / "drawing.svg"
        svg_bytes = b"<svg>test</svg>"

        result = save_svg_bytes_to_svg(
            svg_bytes=svg_bytes,
            output_path=output_path,
            create_output_directory=True,
        )

        assert result == output_path
        assert output_path.read_bytes() == svg_bytes


class TestSaveSvgBytesToPdf:
    @patch("dexpi_pid_renderer.dexpi_to_image_file.HTML")
    @patch("dexpi_pid_renderer.dexpi_to_image_file.wrap_svg_bytes_into_html")
    def test_save_svg_bytes_to_pdf(
        self,
        mock_wrap_html: MagicMock,
        mock_html_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.pdf"
        svg_bytes = b"<svg>test</svg>"
        html_content = "<html>mock</html>"

        mock_wrap_html.return_value = html_content
        mock_html_document = MagicMock()
        mock_html_class.return_value = mock_html_document

        result = save_svg_bytes_to_pdf(
            svg_bytes=svg_bytes,
            output_path=output_path,
            page_size="A3",
            orientation="portrait",
        )

        assert result == output_path

        mock_wrap_html.assert_called_once_with(
            svg_bytes=svg_bytes,
            page_size="A3",
            orientation="portrait",
        )
        mock_html_class.assert_called_once_with(
            string=html_content,
        )
        mock_html_document.write_pdf.assert_called_once_with(output_path)

    @patch("dexpi_pid_renderer.dexpi_to_image_file.HTML")
    def test_save_svg_bytes_to_pdf_creates_output_directory(
        self,
        mock_html_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "nested" / "drawing.pdf"
        svg_bytes = b"<svg>test</svg>"

        mock_html_class.return_value = MagicMock()

        result = save_svg_bytes_to_pdf(
            svg_bytes=svg_bytes,
            output_path=output_path,
            create_output_directory=True,
        )

        assert result == output_path
        assert output_path.parent.is_dir()


class TestSavePdfBytesToJpg:
    def test_invalid_extension_raises_value_error(
        self,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.png"

        with pytest.raises(
            ValueError,
            match=r"'filepath' must have a '\.jpg' or '\.jpeg' extension\.",
        ):
            save_pdf_bytes_to_jpg(
                pdf_bytes=b"%PDF",
                output_path=output_path,
            )

    @patch("dexpi_pid_renderer.dexpi_to_image_file.convert_pdf_bytes_to_pixmap")
    def test_save_single_page_jpg(
        self,
        mock_convert: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.jpg"
        pdf_bytes = b"%PDF"

        mock_pixmap = MagicMock()
        mock_convert.return_value = (mock_pixmap,)

        result = save_pdf_bytes_to_jpg(
            pdf_bytes=pdf_bytes,
            output_path=output_path,
            resolution_scaling_factor=2,
            jpg_quality_factor=90,
        )

        assert result == output_path

        mock_convert.assert_called_once_with(
            pdf_bytes=pdf_bytes,
            resolution_scaling_factor=2,
        )
        mock_pixmap.save.assert_called_once_with(
            filename=output_path,
            jpg_quality=90,
        )

    @patch("dexpi_pid_renderer.dexpi_to_image_file.convert_pdf_bytes_to_pixmap")
    def test_save_multiple_pages_jpg(
        self,
        mock_convert: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.jpg"
        pdf_bytes = b"%PDF"

        mock_pixmap_1 = MagicMock()
        mock_pixmap_2 = MagicMock()
        mock_pixmap_3 = MagicMock()

        mock_convert.return_value = (
            mock_pixmap_1,
            mock_pixmap_2,
            mock_pixmap_3,
        )

        result = save_pdf_bytes_to_jpg(
            pdf_bytes=pdf_bytes,
            output_path=output_path,
            resolution_scaling_factor=1,
            jpg_quality_factor=80,
            start_page=1,
            end_page=2,
        )

        expected_paths = (
            tmp_path / "drawing_0.jpg",
            tmp_path / "drawing_1.jpg",
        )

        assert result == expected_paths

        mock_pixmap_1.save.assert_not_called()

        mock_pixmap_2.save.assert_called_once_with(
            filename=expected_paths[0],
            jpg_quality=80,
        )
        mock_pixmap_3.save.assert_called_once_with(
            filename=expected_paths[1],
            jpg_quality=80,
        )

    @patch("dexpi_pid_renderer.dexpi_to_image_file.convert_pdf_bytes_to_pixmap")
    def test_save_jpeg_uses_jpeg_extension(
        self,
        mock_convert: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.jpeg"
        mock_pixmap = MagicMock()
        mock_convert.return_value = (mock_pixmap,)

        result = save_pdf_bytes_to_jpg(
            pdf_bytes=b"%PDF",
            output_path=output_path,
        )

        assert result == output_path
        mock_pixmap.save.assert_called_once_with(
            filename=output_path,
            jpg_quality=100,
        )


class TestSavePdfBytesToPng:
    @patch("dexpi_pid_renderer.dexpi_to_image_file.convert_pdf_bytes_to_pixmap")
    def test_save_single_page_png(
        self,
        mock_convert: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.png"
        pdf_bytes = b"%PDF"

        mock_pixmap = MagicMock()
        mock_convert.return_value = (mock_pixmap,)

        result = save_pdf_bytes_to_png(
            pdf_bytes=pdf_bytes,
            output_path=output_path,
            resolution_scaling_factor=2,
        )

        assert result == output_path

        mock_convert.assert_called_once_with(
            pdf_bytes=pdf_bytes,
            resolution_scaling_factor=2,
        )
        mock_pixmap.save.assert_called_once_with(
            filename=output_path,
        )

    @patch("dexpi_pid_renderer.dexpi_to_image_file.convert_pdf_bytes_to_pixmap")
    def test_save_multiple_pages_png(
        self,
        mock_convert: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.png"
        pdf_bytes = b"%PDF"

        mock_pixmap_1 = MagicMock()
        mock_pixmap_2 = MagicMock()
        mock_pixmap_3 = MagicMock()

        mock_convert.return_value = (
            mock_pixmap_1,
            mock_pixmap_2,
            mock_pixmap_3,
        )

        result = save_pdf_bytes_to_png(
            pdf_bytes=pdf_bytes,
            output_path=output_path,
            start_page=1,
            end_page=2,
        )

        expected_paths = (
            tmp_path / "drawing_0.png",
            tmp_path / "drawing_1.png",
        )

        assert result == expected_paths

        mock_pixmap_1.save.assert_not_called()

        mock_pixmap_2.save.assert_called_once_with(
            filename=expected_paths[0],
        )
        mock_pixmap_3.save.assert_called_once_with(
            filename=expected_paths[1],
        )


class TestSavePidAsSvg:
    @patch("dexpi_pid_renderer.dexpi_to_image_file.save_svg_bytes_to_svg")
    @patch("dexpi_pid_renderer.dexpi_to_image_file.render_pid_as_svg")
    def test_save_pid_as_svg(
        self,
        mock_render: MagicMock,
        mock_save: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.svg"
        svg_bytes = b"<svg>rendered</svg>"

        mock_render.return_value = svg_bytes
        mock_save.return_value = output_path

        result = save_pid_as_svg(
            dexpi_model=mock_dexpi_model,
            output_path=output_path,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
            create_output_directory=True,
        )

        assert result == output_path

        mock_render.assert_called_once_with(
            dexpi_model=mock_dexpi_model,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
        )
        mock_save.assert_called_once_with(
            svg_bytes=svg_bytes,
            output_path=output_path,
            create_output_directory=True,
        )


class TestSavePidAsPdf:
    @patch("dexpi_pid_renderer.dexpi_to_image_file.save_svg_bytes_to_pdf")
    @patch("dexpi_pid_renderer.dexpi_to_image_file.render_pid_as_svg")
    def test_save_pid_as_pdf(
        self,
        mock_render: MagicMock,
        mock_save: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.pdf"
        svg_bytes = b"<svg>rendered</svg>"

        mock_render.return_value = svg_bytes
        mock_save.return_value = output_path

        result = save_pid_as_pdf(
            dexpi_model=mock_dexpi_model,
            output_path=output_path,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
            create_output_directory=True,
            page_size="A3",
            orientation="portrait",
        )

        assert result == output_path

        mock_render.assert_called_once_with(
            dexpi_model=mock_dexpi_model,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
        )
        mock_save.assert_called_once_with(
            svg_bytes=svg_bytes,
            output_path=output_path,
            page_size="A3",
            orientation="portrait",
            create_output_directory=True,
        )


class TestSavePidAsJpg:
    @patch("dexpi_pid_renderer.dexpi_to_image_file.save_pdf_bytes_to_jpg")
    @patch("dexpi_pid_renderer.dexpi_to_image_file.convert_svg_bytes_to_pdf")
    @patch("dexpi_pid_renderer.dexpi_to_image_file.render_pid_as_svg")
    def test_save_pid_as_jpg(
        self,
        mock_render: MagicMock,
        mock_convert_pdf: MagicMock,
        mock_save: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.jpg"
        svg_bytes = b"<svg>rendered</svg>"
        pdf_bytes = b"%PDF rendered"

        mock_render.return_value = svg_bytes
        mock_convert_pdf.return_value = pdf_bytes
        mock_save.return_value = output_path

        result = save_pid_as_jpg(
            dexpi_model=mock_dexpi_model,
            output_path=output_path,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
            create_output_directory=True,
            page_size="A3",
            orientation="portrait",
            resolution_scaling_factor=2,
            jpg_quality_factor=90,
            start_page=1,
            end_page=2,
        )

        assert result == output_path

        mock_render.assert_called_once_with(
            dexpi_model=mock_dexpi_model,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
        )
        mock_convert_pdf.assert_called_once_with(
            svg_bytes=svg_bytes,
            page_size="A3",
            orientation="portrait",
        )
        mock_save.assert_called_once_with(
            pdf_bytes=pdf_bytes,
            output_path=output_path,
            create_output_directory=True,
            resolution_scaling_factor=2,
            jpg_quality_factor=90,
            start_page=1,
            end_page=2,
        )


class TestSavePidAsPng:
    @patch("dexpi_pid_renderer.dexpi_to_image_file.save_pdf_bytes_to_png")
    @patch("dexpi_pid_renderer.dexpi_to_image_file.convert_svg_bytes_to_pdf")
    @patch("dexpi_pid_renderer.dexpi_to_image_file.render_pid_as_svg")
    def test_save_pid_as_png(
        self,
        mock_render: MagicMock,
        mock_convert_pdf: MagicMock,
        mock_save: MagicMock,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_path = tmp_path / "drawing.png"
        svg_bytes = b"<svg>rendered</svg>"
        pdf_bytes = b"%PDF rendered"

        mock_render.return_value = svg_bytes
        mock_convert_pdf.return_value = pdf_bytes
        mock_save.return_value = output_path

        result = save_pid_as_png(
            dexpi_model=mock_dexpi_model,
            output_path=output_path,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
            create_output_directory=True,
            page_size="A3",
            orientation="portrait",
            resolution_scaling_factor=2,
            start_page=1,
            end_page=2,
        )

        assert result == output_path

        mock_render.assert_called_once_with(
            dexpi_model=mock_dexpi_model,
            padding=0.5,
            pretty_formatting=True,
            add_background_box=True,
        )
        mock_convert_pdf.assert_called_once_with(
            svg_bytes=svg_bytes,
            page_size="A3",
            orientation="portrait",
        )
        mock_save.assert_called_once_with(
            pdf_bytes=pdf_bytes,
            output_path=output_path,
            create_output_directory=True,
            resolution_scaling_factor=2,
            start_page=1,
            end_page=2,
        )
