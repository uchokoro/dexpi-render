from __future__ import annotations

from pathlib import Path

from .dexpi_model import DexpiModelProvider
from .dexpi_to_image_file import (
    save_pid_as_jpg,
    save_pid_as_pdf,
    save_pid_as_png,
    save_pid_as_svg,
)
from .pid_rendering import (
    DrawingOutputFormat,
    PageOrientation,
    PageSize,
)

FORMAT_TO_SAVER_MAP = {
    "jpeg": save_pid_as_jpg,
    "jpg": save_pid_as_jpg,
    "pdf": save_pid_as_pdf,
    "png": save_pid_as_png,
    "svg": save_pid_as_svg,
}


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
    resolution_scaling_factor: int = 1,
    jpg_quality_factor: int = 100,
    create_output_directory: bool = False,
    dexpi_parser_provider: DexpiModelProvider | None = None,
) -> Path | tuple[Path, ...]:
    """Export DEXPI P&ID model to the target drawing file format."""
    filepath = Path(filepath)
    output_filepath = Path(output_filepath)

    provider = dexpi_parser_provider or DexpiModelProvider()
    dexpi_model = provider.get(filepath=filepath)

    saver = FORMAT_TO_SAVER_MAP.get(output_format)
    if saver is None:
        raise ValueError(f"Unsupported drawing output format: {output_format!r}")

    call_arguments = {
        "dexpi_model": dexpi_model,
        "output_path": output_filepath,
        "padding": padding,
        "pretty_formatting": pretty_formatting,
        "add_background_box": add_background_box,
        "page_size": page_size,
        "orientation": orientation,
        "resolution_scaling_factor": resolution_scaling_factor,
        "jpg_quality_factor": jpg_quality_factor,
        "create_output_directory": create_output_directory,
    }

    return saver(**call_arguments)
