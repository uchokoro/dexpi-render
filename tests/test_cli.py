# tests/test_cli.py
from pathlib import Path
from unittest.mock import patch

import pytest

from dexpi_pid_renderer.cli import __version__, main


class TestSuccessfulExport:
    def test_main_successful_export(
        self,
        sample_xml: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        output_path = tmp_path / "output.pdf"

        with patch(
            "dexpi_pid_renderer.cli.export_dexpi_to_drawing_file"
        ) as mock_export:
            mock_export.return_value = output_path

            exit_code = main(
                [
                    str(sample_xml),
                    "-o",
                    str(output_path),
                    "-f",
                    "pdf",
                    "--padding",
                    "10.0",
                    "--page-size",
                    "A3",
                    "--orientation",
                    "portrait",
                    "--resolution-scale",
                    "1",
                    "--jpg-quality",
                    "100",
                    "--pretty",
                    "--background",
                    "--create-dir",
                ]
            )

        assert exit_code == 0

        mock_export.assert_called_once_with(
            filepath=sample_xml,
            output_filepath=output_path,
            output_format="pdf",
            padding=10.0,
            pretty_formatting=True,
            add_background_box=True,
            page_size="A3",
            orientation="portrait",
            create_output_directory=True,
            resolution_scaling_factor=1,
            jpg_quality_factor=100,
        )

        captured = capsys.readouterr()
        assert f"Successfully exported drawing to: {output_path}" in captured.out


class TestErrorHandling:
    def test_main_handles_exception(
        self,
        sample_xml: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        output_path = tmp_path / "output.pdf"

        with patch(
            "dexpi_pid_renderer.cli.export_dexpi_to_drawing_file",
            side_effect=ValueError("Invalid file format"),
        ):
            exit_code = main(
                [
                    str(sample_xml),
                    "-o",
                    str(output_path),
                ]
            )

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error: Invalid file format" in captured.err


class TestArgumentValidation:
    def test_missing_required_arguments(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main([])

        assert exc_info.value.code == 2

        captured = capsys.readouterr()
        assert "usage:" in captured.err

    @pytest.mark.parametrize(
        "output_format",
        ["pdf", "svg", "png", "jpg", "jpeg"],
    )
    def test_valid_output_formats(
        self,
        sample_xml: Path,
        tmp_path: Path,
        output_format: str,
    ) -> None:
        output_path = tmp_path / f"output.{output_format}"

        with patch(
            "dexpi_pid_renderer.cli.export_dexpi_to_drawing_file"
        ) as mock_export:
            mock_export.return_value = output_path

            exit_code = main(
                [
                    str(sample_xml),
                    "-o",
                    str(output_path),
                    "-f",
                    output_format,
                ]
            )

        assert exit_code == 0
        assert mock_export.call_args.kwargs["output_format"] == output_format

    @pytest.mark.parametrize(
        ("option", "value"),
        [
            ("--format", "doc"),
            ("--page-size", "B4"),
            ("--orientation", "sideways"),
            ("--resolution-scale", "3"),
        ],
    )
    def test_invalid_choice(
        self,
        sample_xml: Path,
        tmp_path: Path,
        option: str,
        value: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        output_path = tmp_path / "output.pdf"

        with pytest.raises(SystemExit) as exc_info:
            main(
                [
                    str(sample_xml),
                    "-o",
                    str(output_path),
                    option,
                    value,
                ]
            )

        assert exc_info.value.code == 2

        captured = capsys.readouterr()
        assert "invalid choice" in captured.err

    def test_invalid_padding(
        self,
        sample_xml: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        output_path = tmp_path / "output.pdf"

        with pytest.raises(SystemExit) as exc_info:
            main(
                [
                    str(sample_xml),
                    "-o",
                    str(output_path),
                    "--padding",
                    "not-a-number",
                ]
            )

        assert exc_info.value.code == 2

        captured = capsys.readouterr()
        assert "invalid float value" in captured.err

    def test_invalid_jpg_quality(
        self,
        sample_xml: Path,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        output_path = tmp_path / "output.jpg"

        # argparse accepts any integer here. The actual
        # 1-100 validation is performed by the downstream function.
        with patch(
            "dexpi_pid_renderer.cli.export_dexpi_to_drawing_file"
        ) as mock_export:
            mock_export.return_value = output_path

            exit_code = main(
                [
                    str(sample_xml),
                    "-o",
                    str(output_path),
                    "--jpg-quality",
                    "150",
                ]
            )

        assert exit_code == 0
        assert mock_export.call_args.kwargs["jpg_quality_factor"] == 150


class TestVersion:
    def test_cli_version(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])

        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert __version__ in captured.out
