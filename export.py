from __future__ import annotations

from pathlib import Path

from dexpi_model import DexpiModelProvider
from pid_rendering import (
    DrawingOutputFormat,
    PageOrientation,
    PageSize,
    render_pid_as_svg,
    save_pid_as_svg,
    save_svg_bytes_to_pdf,
)


def export_dexpi_to_drawing_file(
    filepath: str | Path,
    *,
    output_filepath: str | Path,
    output_format: DrawingOutputFormat = "pdf",
    padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
    page_size: PageSize = "A4",
    orientation: PageOrientation = "landscape",
    create_output_directory: bool = False,
    provider: DexpiModelProvider | None = None,
) -> Path:
    """Render a DEXPI P&ID as a drawing and save it to a file."""
    filepath = Path(filepath)
    output_filepath = Path(output_filepath)

    provider = provider or DexpiModelProvider()
    dexpi_model = provider.get(filepath=filepath)

    output_format = output_format.lower()

    if output_format == "svg":
        return save_pid_as_svg(
            dexpi_model=dexpi_model,
            output_path=output_filepath,
            padding=padding,
            pretty_formatting=pretty_formatting,
            add_background_box=add_background_box,
            create_output_directory=create_output_directory,
        )

    if output_format == "pdf":
        svg_data = render_pid_as_svg(
            dexpi_model=dexpi_model,
            padding=padding,
            pretty_formatting=pretty_formatting,
            add_background_box=add_background_box,
        )

        return save_svg_bytes_to_pdf(
            svg_bytes=svg_data,
            output_path=output_filepath,
            page_size=page_size,
            orientation=orientation,
            create_output_directory=create_output_directory,
        )

    raise ValueError(
        f"Unsupported drawing output format: {output_format!r}"
    )