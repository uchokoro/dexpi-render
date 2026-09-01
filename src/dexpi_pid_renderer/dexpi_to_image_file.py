from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field, validate_call
from pydexpi.dexpi_classes.dexpiModel import DexpiModel
from weasyprint import HTML

from .pid_rendering import (
    PageOrientation,
    PageSize,
    convert_pdf_bytes_to_pixmap,
    convert_svg_bytes_to_pdf,
    render_pid_as_svg,
    resolve_output_filepath,
    wrap_svg_bytes_into_html,
)


def save_svg_bytes_to_svg(
    svg_bytes: bytes,
    output_path: str | Path,
    *,
    create_output_directory: bool = False,
) -> Path:
    """SVG data to an SVG file."""
    output_path = resolve_output_filepath(
        filepath=output_path,
        output_format="svg",
        create_output_directory=create_output_directory,
    )

    output_path.write_bytes(svg_bytes)

    return output_path


def save_svg_bytes_to_pdf(
    svg_bytes: bytes,
    output_path: str | Path,
    *,
    page_size: PageSize = "A4",
    orientation: PageOrientation = "landscape",
    create_output_directory: bool = False,
) -> Path:
    """Convert SVG data to PDF and save it to a file."""
    output_path = resolve_output_filepath(
        filepath=output_path,
        output_format="pdf",
        create_output_directory=create_output_directory,
    )

    html_content = wrap_svg_bytes_into_html(
        svg_bytes=svg_bytes,
        page_size=page_size,
        orientation=orientation,
    )
    html_document = HTML(string=html_content)
    html_document.write_pdf(output_path)

    return output_path


@validate_call
def save_pdf_bytes_to_jpg(
    pdf_bytes: bytes,
    output_path: str | Path,
    *,
    create_output_directory: bool = False,
    resolution_scaling_factor: int = Field(
        default=1,
        ge=1,
        le=2,
    ),
    jpg_quality_factor: int = Field(
        default=100,
        ge=1,
        le=100,
    ),
    start_page: int = 0,
    end_page: int = 0,
) -> Path | tuple[Path, ...]:
    """Convert PDF data to JPG/JPEG images and save them as files."""
    path_obj = Path(output_path)
    ext = path_obj.suffix.lower()
    if ext not in (".jpg", ".jpeg"):
        raise ValueError("'filepath' must have a '.jpg' or '.jpeg' extension.")

    format_arg = "jpg" if ext == ".jpg" else "jpeg"
    output_path = resolve_output_filepath(
        filepath=path_obj,
        output_format=format_arg,  # type: ignore[arg-type]
        create_output_directory=create_output_directory,
    )

    pix_maps = convert_pdf_bytes_to_pixmap(
        pdf_bytes=pdf_bytes,
        resolution_scaling_factor=resolution_scaling_factor,
    )

    selected_pixmaps = pix_maps[start_page : end_page + 1]

    if len(selected_pixmaps) == 1:
        selected_pixmaps[0].save(  # type: ignore[no-untyped-call]
            filename=output_path, jpg_quality=jpg_quality_factor
        )
        return output_path

    file_dir = output_path.parent
    filename = output_path.stem
    extension = output_path.suffix
    output_paths: list[Path] = []

    for i, pix_map in enumerate(selected_pixmaps):
        page_filename = f"{filename}_{i + start_page}{extension}"
        filepath = file_dir / page_filename
        pix_map.save(filename=filepath, jpg_quality=jpg_quality_factor)  # type: ignore[no-untyped-call]
        output_paths.append(filepath)

    return tuple(output_paths)


@validate_call
def save_pdf_bytes_to_png(
    pdf_bytes: bytes,
    output_path: str | Path,
    *,
    create_output_directory: bool = False,
    resolution_scaling_factor: int = Field(
        default=1,
        ge=1,
        le=2,
    ),
    start_page: int = 0,
    end_page: int = 0,
) -> Path | tuple[Path, ...]:
    """Convert PDF data to PNG images and save them as files."""
    output_path = resolve_output_filepath(
        filepath=output_path,
        output_format="png",
        create_output_directory=create_output_directory,
    )

    pix_maps = convert_pdf_bytes_to_pixmap(
        pdf_bytes=pdf_bytes,
        resolution_scaling_factor=resolution_scaling_factor,
    )

    selected_pixmaps = pix_maps[start_page : end_page + 1]

    if len(selected_pixmaps) == 1:
        selected_pixmaps[0].save(filename=output_path)  # type: ignore[no-untyped-call]
        return output_path

    file_dir = output_path.parent
    filename = output_path.stem
    extension = output_path.suffix
    output_paths: list[Path] = []

    for i, pix_map in enumerate(selected_pixmaps):
        page_filename = f"{filename}_{i + start_page}{extension}"
        filepath = file_dir / page_filename
        pix_map.save(filename=filepath)  # type: ignore[no-untyped-call]
        output_paths.append(filepath)

    return tuple(output_paths)


def save_pid_as_svg(
    *,
    dexpi_model: DexpiModel,
    output_path: str | Path,
    padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
    create_output_directory: bool = False,
    **_kwargs: Any,
) -> Path:
    """Render a DEXPI P&ID model as SVG data, and save it to an SVG file."""
    svg_bytes = render_pid_as_svg(
        dexpi_model=dexpi_model,
        padding=padding,
        pretty_formatting=pretty_formatting,
        add_background_box=add_background_box,
    )

    return save_svg_bytes_to_svg(
        svg_bytes=svg_bytes,
        output_path=output_path,
        create_output_directory=create_output_directory,
    )


def save_pid_as_pdf(
    *,
    dexpi_model: DexpiModel,
    output_path: str | Path,
    padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
    create_output_directory: bool = False,
    page_size: PageSize = "A4",
    orientation: PageOrientation = "landscape",
    **_kwargs: Any,
) -> Path:
    """Render a DEXPI P&ID model as SVG data, and save it to a PDF file."""
    svg_bytes = render_pid_as_svg(
        dexpi_model=dexpi_model,
        padding=padding,
        pretty_formatting=pretty_formatting,
        add_background_box=add_background_box,
    )

    return save_svg_bytes_to_pdf(
        svg_bytes=svg_bytes,
        output_path=output_path,
        page_size=page_size,
        orientation=orientation,
        create_output_directory=create_output_directory,
    )


def save_pid_as_jpg(
    *,
    dexpi_model: DexpiModel,
    output_path: str | Path,
    padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
    create_output_directory: bool = False,
    page_size: PageSize = "A4",
    orientation: PageOrientation = "landscape",
    resolution_scaling_factor: int = Field(
        default=1,
        ge=1,
        le=2,
    ),
    jpg_quality_factor: int = Field(
        default=100,
        ge=1,
        le=100,
    ),
    start_page: int = 0,
    end_page: int = 0,
    **_kwargs: Any,
) -> Path | tuple[Path, ...]:
    """Render a DEXPI P&ID model as SVG data, and save it to a JPG/JPEG file."""
    svg_bytes = render_pid_as_svg(
        dexpi_model=dexpi_model,
        padding=padding,
        pretty_formatting=pretty_formatting,
        add_background_box=add_background_box,
    )
    pdf_bytes = convert_svg_bytes_to_pdf(
        svg_bytes=svg_bytes,
        page_size=page_size,
        orientation=orientation,
    )

    return save_pdf_bytes_to_jpg(
        pdf_bytes=pdf_bytes,
        output_path=output_path,
        create_output_directory=create_output_directory,
        resolution_scaling_factor=resolution_scaling_factor,
        jpg_quality_factor=jpg_quality_factor,
        start_page=start_page,
        end_page=end_page,
    )


def save_pid_as_png(
    *,
    dexpi_model: DexpiModel,
    output_path: str | Path,
    padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
    create_output_directory: bool = False,
    page_size: PageSize = "A4",
    orientation: PageOrientation = "landscape",
    resolution_scaling_factor: int = Field(
        default=1,
        ge=1,
        le=2,
    ),
    start_page: int = 0,
    end_page: int = 0,
    **_kwargs: Any,
) -> Path | tuple[Path, ...]:
    """Render a DEXPI P&ID model as SVG data, and save it to a PNG file."""
    svg_bytes = render_pid_as_svg(
        dexpi_model=dexpi_model,
        padding=padding,
        pretty_formatting=pretty_formatting,
        add_background_box=add_background_box,
    )
    pdf_bytes = convert_svg_bytes_to_pdf(
        svg_bytes=svg_bytes,
        page_size=page_size,
        orientation=orientation,
    )

    return save_pdf_bytes_to_png(
        pdf_bytes=pdf_bytes,
        output_path=output_path,
        create_output_directory=create_output_directory,
        resolution_scaling_factor=resolution_scaling_factor,
        start_page=start_page,
        end_page=end_page,
    )
