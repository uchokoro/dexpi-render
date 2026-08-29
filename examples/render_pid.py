import os
from pathlib import Path

try:
    from dotenv import find_dotenv, load_dotenv

    _ = load_dotenv(find_dotenv())
except ImportError:
    # Fall back to standard OS environment variables if python-dotenv isn't installed
    find_dotenv = None
    load_dotenv = None

from dexpi_pid_renderer import (
    DrawingOutputFormat,
    PageOrientation,
    PageSize,
    export_dexpi_to_drawing_file,
)


def main() -> None:
    dexpi_filepath = os.getenv("DEXPI_FILEPATH")
    drawing_output_dir = os.getenv("DRAWING_OUTPUT_DIR")

    if dexpi_filepath is None:
        raise RuntimeError("DEXPI_FILEPATH is not configured")

    if drawing_output_dir is None:
        raise RuntimeError("DRAWING_OUTPUT_DIR is not configured")

    file_stem = Path(dexpi_filepath).stem
    drawing_format: DrawingOutputFormat = "pdf"
    page_size: PageSize = "A4"
    orientation: PageOrientation = "landscape"
    drawing_filepath = Path(drawing_output_dir) / f"{file_stem}.{drawing_format}"
    saved_filepath = export_dexpi_to_drawing_file(
        filepath=dexpi_filepath,
        output_filepath=drawing_filepath,
        output_format=drawing_format,
        padding=0.5,
        page_size=page_size,
        orientation=orientation,
        pretty_formatting=True,
        add_background_box=True,
    )
    print(f"P&ID from '{dexpi_filepath}' has been exported to '{saved_filepath}'.")


if __name__ == "__main__":
    main()
