from __future__ import annotations

import base64
from pathlib import Path
from typing import Literal, cast

import pymupdf
from pydantic import Field, validate_call
from pydexpi.dexpi_classes.dexpiModel import DexpiModel
from pydexpi.loaders.svg_loader import DrawDiagram
from weasyprint import HTML

DrawingOutputFormat = Literal["jpeg", "jpg", "pdf", "png", "svg"]
PageOrientation = Literal["portrait", "landscape"]

PageSize = Literal[
    "A0",
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "LETTER",
    "LEGAL",
]


def _create_pid_drawer(
    dexpi_model: DexpiModel,
    *,
    padding: float,
    pretty_formatting: bool,
) -> DrawDiagram:
    return DrawDiagram(
        dexpi_model.diagram,
        padding=padding,
        pretty=pretty_formatting,
    )


def resolve_output_filepath(
    filepath: str | Path,
    output_format: DrawingOutputFormat,
    create_output_directory: bool = False,
) -> Path:
    if not isinstance(filepath, (str, Path)):
        raise TypeError("'filepath' must be a `str` or a `Path`.")

    filepath = Path(filepath)
    expected_suffix = f".{output_format.lower()}"

    if filepath.suffix.lower() != expected_suffix:
        raise ValueError(
            f"'filepath' must have a '.{output_format.lower()}' extension."
        )

    if filepath.parent.is_dir():
        return filepath

    if not create_output_directory:
        raise NotADirectoryError(
            "No directory corresponding to output path's parent found."
        )

    filepath.parent.mkdir(parents=True, exist_ok=True)

    return filepath


def _build_page_size(
    page_size: PageSize,
    orientation: PageOrientation,
) -> str:
    return f"{page_size} {orientation}"


def wrap_svg_bytes_into_html(
    svg_bytes: bytes,
    *,
    page_size: PageSize = "A4",
    orientation: PageOrientation = "landscape",
) -> str:
    # Encode the SVG bytes to a base64 string
    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")

    css_page_size = _build_page_size(page_size, orientation)

    return f"""
        <html>
          <head>
            <style>
              @page {{
                size: {css_page_size};
                margin: 0;
              }}

              html,
              body {{
                width: 100%;
                height: 100%;
                margin: 0;
                padding: 0;
              }}

              body {{
                display: flex;
                justify-content: center;
                align-items: center;
              }}

              img {{
                display: block;
                width: 100%;
                height: 100%;
                object-fit: contain;
              }}
            </style>
          </head>
          <body>
            <img src="data:image/svg+xml;base64,{svg_base64}" />
          </body>
        </html>
        """


def render_pid_as_svg(
    *,
    dexpi_model: DexpiModel,
    padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
) -> bytes:
    """Render a DEXPI P&ID model as SVG data."""
    drawer = _create_pid_drawer(
        dexpi_model=dexpi_model,
        padding=padding,
        pretty_formatting=pretty_formatting,
    )

    svg_string = drawer.draw_svg(return_element=False, background=add_background_box)

    return cast(bytes, svg_string.encode("utf-8"))


def convert_svg_bytes_to_pdf(
    svg_bytes: bytes,
    *,
    page_size: PageSize = "A4",
    orientation: PageOrientation = "landscape",
) -> bytes:
    """Convert SVG data to PDF."""
    html_content = wrap_svg_bytes_into_html(
        svg_bytes=svg_bytes,
        page_size=page_size,
        orientation=orientation,
    )
    html_document = HTML(string=html_content)
    pdf_bytes = html_document.write_pdf()

    if pdf_bytes is None:
        raise RuntimeError("Error converting SVG data to PDF.")

    return cast(bytes, pdf_bytes)


@validate_call
def convert_pdf_bytes_to_pixmap(
    *,
    pdf_bytes: bytes,
    resolution_scaling_factor: int = Field(
        default=1,
        ge=1,
        le=2,
    ),
) -> tuple[pymupdf.Pixmap, ...]:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:  # type: ignore[no-untyped-call]
        num_pages = len(doc)
        pix_maps = []

        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            scaling_matrix = pymupdf.Matrix(  # type: ignore[no-untyped-call]
                resolution_scaling_factor, resolution_scaling_factor
            )
            pix = page.get_pixmap(matrix=scaling_matrix)
            pix_maps.append(pix)

        return tuple(pix_maps)
