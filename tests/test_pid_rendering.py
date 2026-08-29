from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from dexpi_pid_renderer.pid_rendering import (
    _build_page_size,
    _create_pid_drawer,
    _resolve_output_filepath,
    _wrap_svg_bytes_into_html,
    convert_svg_bytes_to_pdf,
    render_pid_as_svg,
    save_pid_as_svg,
    save_svg_bytes_to_pdf,
    save_svg_bytes_to_svg,
)


@pytest.fixture
def mock_dexpi_model() -> MagicMock:
    model = MagicMock()
    model.diagram = MagicMock()
    return model


class TestHelperFunctions:
    def test_build_page_size(self) -> None:
        result = _build_page_size("A4", "landscape")
        assert result == "A4 landscape"

    def test_wrap_svg_bytes_into_html(self) -> None:
        raw_svg = b"<svg><rect /></svg>"
        html = _wrap_svg_bytes_into_html(
            raw_svg, page_size="A3", orientation="portrait"
        )

        assert "size: A3 portrait;" in html
        assert "data:image/svg+xml;base64," in html

    def test_create_pid_drawer(self, mock_dexpi_model: MagicMock) -> None:
        with patch("dexpi_pid_renderer.pid_rendering.DrawDiagram") as mock_draw_diagram:
            _create_pid_drawer(mock_dexpi_model, padding=1.0, pretty_formatting=True)
            mock_draw_diagram.assert_called_once_with(
                mock_dexpi_model.diagram,
                padding=1.0,
                pretty=True,
            )


class TestResolveOutputFilepath:
    def test_valid_filepath_str_and_path(self, tmp_path: Path) -> None:
        target_path = tmp_path / "output.svg"

        res_path = _resolve_output_filepath(str(target_path), "svg")
        assert res_path == target_path

        res_path_obj = _resolve_output_filepath(target_path, "svg")
        assert res_path_obj == target_path

    def test_invalid_type_raises_type_error(self) -> None:
        with pytest.raises(TypeError, match="'filepath' must be a `str` or a `Path`."):
            invalid_path: Any = 12345
            _resolve_output_filepath(invalid_path, "svg")

    def test_invalid_extension_raises_value_error(self, tmp_path: Path) -> None:
        target_path = tmp_path / "output.png"
        with pytest.raises(
            ValueError, match="'filepath' must have a '.svg' extension."
        ):
            _resolve_output_filepath(target_path, "svg")

    def test_missing_directory_without_create_flag_raises_not_a_directory_error(
        self,
        tmp_path: Path,
    ) -> None:
        non_existent_dir = tmp_path / "nested_folder" / "output.pdf"
        with pytest.raises(NotADirectoryError):
            _resolve_output_filepath(
                non_existent_dir,
                "pdf",
                create_output_directory=False,
            )

    def test_missing_directory_with_create_flag_creates_directory(
        self,
        tmp_path: Path,
    ) -> None:
        nested_file = tmp_path / "nested_folder" / "sub" / "output.pdf"
        resolved = _resolve_output_filepath(
            nested_file,
            "pdf",
            create_output_directory=True,
        )

        assert resolved == nested_file
        assert nested_file.parent.is_dir()


class TestRenderPidFunctions:
    def test_render_pid_as_svg(self, mock_dexpi_model: MagicMock) -> None:
        mock_svg_str = "<svg>P&ID Content</svg>"
        with patch("dexpi_pid_renderer.pid_rendering.DrawDiagram") as mock_draw:
            mock_drawer = MagicMock()
            mock_drawer.draw_svg.return_value = mock_svg_str
            mock_draw.return_value = mock_drawer

            result = render_pid_as_svg(
                dexpi_model=mock_dexpi_model,
                padding=0.5,
                pretty_formatting=True,
                add_background_box=True,
            )

            assert result == mock_svg_str.encode("utf-8")
            mock_drawer.draw_svg.assert_called_once_with(
                return_element=False,
                background=True,
            )

    @patch("dexpi_pid_renderer.pid_rendering.HTML")
    def test_convert_svg_bytes_to_pdf(self, mock_html_class: MagicMock) -> None:
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b"%PDF-1.4 Mock Bytes"
        mock_html_class.return_value = mock_html_instance

        raw_svg = b"<svg></svg>"
        pdf_bytes = convert_svg_bytes_to_pdf(
            raw_svg,
            page_size="A4",
            orientation="landscape",
        )

        assert pdf_bytes == b"%PDF-1.4 Mock Bytes"
        mock_html_class.assert_called_once()
        mock_html_instance.write_pdf.assert_called_once()


class TestSaveFunctions:
    def test_save_pid_as_svg(
        self,
        mock_dexpi_model: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_file = tmp_path / "drawing.svg"

        with patch("dexpi_pid_renderer.pid_rendering.DrawDiagram") as mock_draw:
            mock_drawer = MagicMock()
            mock_drawer.save_svg.return_value = str(output_file)
            mock_draw.return_value = mock_drawer

            saved_path = save_pid_as_svg(
                dexpi_model=mock_dexpi_model,
                output_path=output_file,
                padding=0.2,
                pretty_formatting=False,
                add_background_box=True,
            )

            assert saved_path == output_file
            mock_drawer.save_svg.assert_called_once_with(
                object_name="drawing",
                filepath=str(output_file),
                background=True,
            )

    def test_save_svg_bytes_to_svg(self, tmp_path: Path) -> None:
        output_file = tmp_path / "test.svg"
        raw_svg = b"<svg>test bytes</svg>"

        saved_path = save_svg_bytes_to_svg(raw_svg, output_file)

        assert saved_path == output_file
        assert output_file.read_bytes() == raw_svg

    @patch("dexpi_pid_renderer.pid_rendering.HTML")
    def test_save_svg_bytes_to_pdf(
        self,
        mock_html_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        output_file = tmp_path / "test.pdf"
        mock_html_instance = MagicMock()
        mock_html_class.return_value = mock_html_instance

        raw_svg = b"<svg>test bytes</svg>"
        saved_path = save_svg_bytes_to_pdf(
            raw_svg,
            output_file,
            page_size="A4",
            orientation="portrait",
        )

        assert saved_path == output_file
        mock_html_instance.write_pdf.assert_called_once_with(output_file)
