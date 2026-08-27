import os

from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from pydexpi.dexpi_classes.dexpiModel import DexpiModel

from dexpi_model import DexpiModelProvider
from pid_rendering import (
    DrawingOutputFormat,
    PageOrientation,
    render_pid_as_svg,
    save_pid_as_svg,
    save_svg_bytes_to_pdf,
)


_ = load_dotenv(find_dotenv())
dexpi_filepath = os.getenv("DEXPI_FILEPATH")
drawing_output_dir = os.getenv("DRAWING_OUTPUT_DIR")

if dexpi_filepath is None:
    raise RuntimeError("DEXPI_FILEPATH is not configured")

if drawing_output_dir is None:
    raise RuntimeError("DRAWING_OUTPUT_DIR is not configured")

_dexpi_model_provider = DexpiModelProvider()


def _load_dexpi_model(
    filepath: str | Path,
    provider: DexpiModelProvider | None = None,
) -> DexpiModel:
    if provider is None:
        provider = _dexpi_model_provider

    dexpi_model = provider.get(filepath)
    return dexpi_model


# Export P&ID to image file or PDF
def export_dexpi_to_drawing_file(
    filepath: str | Path,
    *,
    output_filepath: str | Path,
    output_file_format: DrawingOutputFormat = "pdf",
    image_padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
    page_size: str = "A4",
    orientation: PageOrientation = "landscape",
    create_output_directory: bool = False
) -> Path:
    if not isinstance(filepath, (Path, str)):
        raise TypeError("'filepath' must be a str or Path.")

    filepath = Path(filepath)

    if not isinstance(output_filepath, (str, Path)):
        raise TypeError("'output_dir' must be a str or Path.")

    output_filepath = Path(output_filepath)

    dexpi_model = _load_dexpi_model(filepath=filepath)
    output_file_format = output_file_format.lower()

    if output_file_format == "svg":
        return save_pid_as_svg(
            dexpi_model=dexpi_model,
            output_path=output_filepath,
            padding=image_padding,
            pretty_formatting=pretty_formatting,
            add_background_box=add_background_box,
            create_output_directory=create_output_directory,
        )


    svg_data = render_pid_as_svg(
        dexpi_model=dexpi_model,
        padding=image_padding,
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


if __name__ == "__main__":
    file_stem = Path(dexpi_filepath).stem
    output_format: DrawingOutputFormat = "pdf"
    drawing_filepath = Path(drawing_output_dir) / f"{file_stem}.{output_format}"
    saved_filepath = export_dexpi_to_drawing_file(
        filepath=dexpi_filepath,
        output_filepath=drawing_filepath,
        output_file_format=output_format,
        image_padding=0.5,
        page_size="A4",
        orientation="landscape",
        pretty_formatting=True,
        add_background_box=True,
    )
    print(
        f"P&ID from '{dexpi_filepath}' has been exported "
        f"to '{saved_filepath}'."
    )

"""
# Render a single component with node position markers
component_group = dexpi_model.diagram.groups[2]  # e.g. a pump
representation_component_group: RepresentationGroup = cast(
    RepresentationGroup, component_group
)
drawer = DrawRepresentationGroup(component_group, padding=10.0, show_node_position=True)
drawer.save_svg("pump", "output/pump.svg")
"""