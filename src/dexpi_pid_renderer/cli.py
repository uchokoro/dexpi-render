from __future__ import annotations

import argparse
import sys

from pathlib import Path
from typing import Sequence

from .export import export_dexpi_to_drawing_file


__version__ = "0.1.0"


def _build_parser() -> argparse.ArgumentParser:
    """Construct and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="dexpi-render",
        description="Render DEXPI P&ID models to SVG or PDF drawings.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "filepath",
        type=Path,
        help="Path to the input DEXPI XML file.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        dest="output_filepath",
        help="Path where the output drawing will be saved.",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["pdf", "svg"],
        default="pdf",
        dest="output_format",
        help="Target drawing format.",
    )

    parser.add_argument(
        "--padding",
        type=float,
        default=0.0,
        help="Padding added around the diagram elements.",
    )

    parser.add_argument(
        "--page-size",
        choices=["A0", "A1", "A2", "A3", "A4", "A5", "LETTER", "LEGAL"],
        default="A4",
        help="Page size for PDF rendering.",
    )

    parser.add_argument(
        "--orientation",
        choices=["landscape", "portrait"],
        default="landscape",
        help="Page orientation for PDF rendering.",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        default=False,
        dest="pretty_formatting",
        help="Enable pretty-formatted SVG output.",
    )

    parser.add_argument(
        "--background",
        action="store_true",
        default=False,
        dest="add_background_box",
        help="Add a background bounding box behind the diagram.",
    )

    parser.add_argument(
        "--create-dir",
        action="store_true",
        default=False,
        dest="create_output_directory",
        help="Automatically create parent directories for the output path if missing.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line interface entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        saved_path = export_dexpi_to_drawing_file(
            filepath=args.filepath,
            output_filepath=args.output_filepath,
            output_format=args.output_format,
            padding=args.padding,
            pretty_formatting=args.pretty_formatting,
            add_background_box=args.add_background_box,
            page_size=args.page_size,
            orientation=args.orientation,
            create_output_directory=args.create_output_directory,
        )
        print(f"Successfully exported drawing to: {saved_path}")
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())