from __future__ import annotations

import base64

from pathlib import Path
from typing import cast, Literal
from typing_extensions import Buffer

from pydexpi.loaders.svg_loader import DrawDiagram
from pydexpi.dexpi_classes.dexpiModel import DexpiModel
from weasyprint import HTML

#from dexpi_model import DexpiModelProvider


DrawingOutputFormat = Literal[
    "JPG", "jpg", "JPEG", "jpeg", "PDF", "pdf", "SVG", "svg"
]
PageOrientation = Literal["portrait", "landscape"]


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


def _resolve_output_filepath(
    filepath: str | Path,
    output_format: DrawingOutputFormat,
    create_output_directory: bool = False,
) -> Path:
    if not isinstance(filepath, (str, Path)):
        raise TypeError("'output_path' must be a `str` or a `Path`.")

    filepath = Path(filepath)

    if not filepath.suffix.lower() == f".{output_format.lower()}":
        raise ValueError(
            f"Output path must be a valid {output_format.lower()} filepath."
        )

    if not create_output_directory and not filepath.parent.is_dir():
        raise NotADirectoryError(
            "No directory corresponding to output path's parent found."
        )


    filepath.parent.mkdir(parents=True, exist_ok=True)

    return filepath


def _wrap_svg_bytes_into_html(
    svg_bytes: bytes,
    *,
    page_size: str = "A4",
    orientation: PageOrientation = "landscape",
) -> str:
    # Encode the SVG bytes to a base64 string
    svg_base64 = base64.b64encode(
        cast(Buffer, svg_bytes)
    ).decode('utf-8')

    css_page_size = f"{page_size} {orientation}"

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
    drawer = _create_pid_drawer(
        dexpi_model=dexpi_model,
        padding=padding,
        pretty_formatting=pretty_formatting,
    )

    svg_string = drawer.draw_svg(
        return_element=False,
        background=add_background_box
    )

    return svg_string.encode("utf-8")


def convert_svg_bytes_to_pdf(
    svg_bytes: bytes,
    *,
    page_size: str = "A4",
    orientation: PageOrientation = "landscape",
) -> bytes:
    html_content = _wrap_svg_bytes_into_html(
        svg_bytes=svg_bytes,
        page_size=page_size,
        orientation=orientation,
    )
    html_document = HTML(string=html_content)

    return html_document.write_pdf()


def save_pid_as_svg(
    *,
    dexpi_model: DexpiModel,
    output_path: str | Path,
    padding: float = 0.0,
    pretty_formatting: bool = False,
    add_background_box: bool = False,
    create_output_directory: bool = False,
) -> Path:
    output_path: Path = _resolve_output_filepath(
        filepath=output_path,
        output_format="svg",
        create_output_directory=create_output_directory,
    )
    drawer = _create_pid_drawer(
        dexpi_model=dexpi_model,
        padding=padding,
        pretty_formatting=pretty_formatting,
    )

    saved_path = drawer.save_svg(
        object_name=output_path.stem,
        filepath=str(output_path),
        background=add_background_box,
    )

    return Path(saved_path)


def save_svg_bytes_to_svg(
    svg_bytes: bytes,
    output_path: str | Path,
    *,
    create_output_directory: bool = False,
) -> Path:
    output_path = _resolve_output_filepath(
        filepath=output_path,
        output_format="svg",
        create_output_directory=create_output_directory,
    )

    output_path.write_bytes(
        cast(Buffer, svg_bytes)
    )

    return output_path


def save_svg_bytes_to_pdf(
    svg_bytes: bytes,
    output_path: str | Path,
    *,
    page_size: str = "A4",
    orientation: PageOrientation = "landscape",
    create_output_directory: bool = False,
) -> Path:
    output_path = _resolve_output_filepath(
        filepath=output_path,
        output_format="pdf",
        create_output_directory=create_output_directory,
    )

    html_content = _wrap_svg_bytes_into_html(
        svg_bytes=svg_bytes,
        page_size=page_size,
        orientation=orientation,
    )
    html_document = HTML(string=html_content)
    html_document.write_pdf(output_path)

    return output_path