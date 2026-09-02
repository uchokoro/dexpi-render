# DEXPI P&ID Renderer

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library and command-line tool for parsing DEXPI-compliant Piping and Instrumentation Diagrams (P&IDs) and rendering them into high-quality vector drawings (**SVG**, **PDF**) and high-resolution raster images (**PNG**, **JPG**, **JPEG**).

---

## Features

* **XML Model Parsing:** Load and validate DEXPI XML models seamlessly using `pydexpi`.
* **In-Memory Caching:** High-performance model provider (`DexpiModelProvider`) featuring path-keyed caching to prevent redundant parsing.
* **Multi-Format Export:** Export diagrams to **SVG**, **PDF**, **PNG**, **JPG**, and **JPEG** formats with dynamic saver argument filtering.
* **Raster Configuration:** Control image quality (`jpg_quality_factor`) and DPI scaling (`resolution_scaling_factor`).
* **Visual Customization:** Adjust diagram padding, toggle background bounding boxes, enable pretty-printed SVG formatting, and specify page dimensions/orientations.
* **CLI Tool:** Direct terminal interface (`dexpi-render`) supporting all output formats and configuration flags.

---

## Installation

### Prerequisites
* Python **3.12** or higher
* Core dependencies (installed automatically via `pip`):
  * `pydexpi` (DEXPI XML model handling)
  * `pymupdf` (PyMuPDF - raster image conversion)
  * `pydantic` (Data validation and CLI argument typing)
  * `weasyprint` (HTML/CSS to PDF rendering engine)
* [WeasyPrint system libraries](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) (cairo, pango, gdk-pixbuf) installed on your operating system.

### Install from Source
Clone the repository and install the package:

```bash
git clone [https://github.com/uchokoro/dexpi-render.git](https://github.com/uchokoro/dexpi-render.git)
cd dexpi-render

# Install core package
pip install .

# Or install in editable mode with development/example dependencies
pip install -e ".[dev,examples]"
```

---

## Usage

### High-Level Drawing Export
The primary entry point for rendering DEXPI files is `export_dexpi_to_drawing_file`. It automatically detects required parameters and dispatches to format-specific savers for **SVG**, **PDF**, **PNG**, **JPG**, and **JPEG** (JPEG uses the same export pipeline as JPG):

```python
from pathlib import Path
from dexpi_pid_renderer import export_dexpi_to_drawing_file

# 1. Export to SVG (Vector)
svg_path = export_dexpi_to_drawing_file(
    filepath="path/to/model.xml",
    output_filepath="output/model.svg",
    output_format="svg",
    padding=0.5,
    pretty_formatting=True,
    add_background_box=True,
    create_output_directory=True,
)

# 2. Export to PDF (Vector Document)
pdf_path = export_dexpi_to_drawing_file(
    filepath="path/to/model.xml",
    output_filepath="output/model.pdf",
    output_format="pdf",
    page_size="A3",
    orientation="landscape",
    create_output_directory=True,
)

# 3. Export to PNG (High-DPI Raster Image)
png_path = export_dexpi_to_drawing_file(
    filepath="path/to/model.xml",
    output_filepath="output/model.png",
    output_format="png",
    page_size="A4",
    orientation="landscape",
    resolution_scaling_factor=2,  # 2x resolution scaling
    create_output_directory=True,
)

# 4. Export to JPG / JPEG (Compressed Raster Image)
jpg_path = export_dexpi_to_drawing_file(
    filepath="path/to/model.xml",
    output_filepath="output/model.jpg",  # .jpeg extensions are also handled identically
    output_format="jpg",
    page_size="A4",
    orientation="landscape",
    resolution_scaling_factor=2,
    jpg_quality_factor=90,  # Quality (1-100)
    create_output_directory=True,
)
```

### Low-Level File Saver API
For fine-grained control, you can call the direct saver functions or convert in-memory bytes.

#### Direct Model Savers
- `save_pid_as_svg(*, dexpi_model, output_path, ...)`
- `save_pid_as_pdf(*, dexpi_model, output_path, page_size, orientation, ...)`
- `save_pid_as_png(*, dexpi_model, output_path, resolution_scaling_factor, start_page, end_page, ...)`
- `save_pid_as_jpg(*, dexpi_model, output_path, resolution_scaling_factor, jpg_quality_factor, start_page, end_page, ...)`

#### Bytes & Data Savers
- `save_svg_bytes_to_svg(svg_bytes, output_path, ...)`
- `save_svg_bytes_to_pdf(svg_bytes, output_path, page_size, orientation, ...)`
- `save_pdf_bytes_to_png(pdf_bytes, output_path, resolution_scaling_factor, start_page, end_page, ...)`
- `save_pdf_bytes_to_jpg(pdf_bytes, output_path, resolution_scaling_factor, jpg_quality_factor, start_page, end_page, ...)`

#### Example: Model Caching & Programmatic Rendering

```python
from dexpi_pid_renderer import (
    DexpiModelProvider,
    render_pid_as_svg,
    save_svg_bytes_to_pdf,
)

provider = DexpiModelProvider()

# Load and cache model
model = provider.get("path/to/model.xml")

# Render directly to SVG bytes
svg_bytes = render_pid_as_svg(
    dexpi_model=model,
    padding=0.5,
    pretty_formatting=True,
)

# Convert SVG bytes to PDF
save_svg_bytes_to_pdf(
    svg_bytes=svg_bytes,
    output_path="output/cached_model.pdf",
    page_size="A3",
    orientation="landscape",
    create_output_directory=True,
)
```

### Command Line Interface (CLI)
The package includes a terminal executable (`dexpi-render`).

```bash
# Export to PDF (default format)
dexpi-render path/to/model.xml -o output/model.pdf --page-size A3 --orientation landscape

# Export to high-resolution PNG with extra padding and background box
dexpi-render path/to/model.xml -o output/model.png -f png --resolution-scale 2 --padding 1.0 --background

# Export to JPG with custom quality compression
dexpi-render path/to/model.xml -o output/model.jpg -f jpg --resolution-scale 2 --jpg-quality 85 --create-dir
```

#### CLI Flag Options:
- `-o, --output`: (**Required**) Path to destination file.
- `-f, --format`: Target extension (`pdf`, `svg`, `png`, `jpg`, `jpeg`). Default: `pdf`.
- `--padding`: Floating-point diagram padding. Default: `0.0`.
- `--page-size`: Dimensions (`A0` through `A5`, `LETTER`, `LEGAL`). Default: `A4`.
- `--orientation`: Page layout (`landscape`, `portrait`). Default: `landscape`.
- `--resolution-scale`: Raster multiplier (`1` or `2`). Default: `1`.
- `--jpg-quality`: JPG compression score (`1` to `100`). Default: `100`.
- `--pretty`: Format SVG XML with indentation.
- `--background`: Add a bounding background box behind components.
- `--create-dir`: Automatically create parent output directory if missing.

---

## Running the Examples

Run `examples/render_pid.py` to test loading and saving a DEXPI file

### 1. Set Up Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open .env in your editor and configure the file paths to point to your DEXPI XML file and desired output directory:

```
DEXPI_FILEPATH="path/to/your/input_model.xml"
DRAWING_OUTPUT_DIR="path/to/your/output_directory"
```

### 2. Install Required Dependencies
Ensure you have installed the optional examples dependencies (`python-dotenv`):

```bash
pip install -e ".[examples]"
```

### 3. Execute the Example Script
Run the script from the project root:

```bash
python examples/render_pid.py
```

---

## Project Structure

```
dexpi-pid-renderer/
├── .env.example                # Template for example script environment variables
├── .gitignore                  # Git ignore patterns
├── .pre-commit-config.yaml     # Git hooks configuration (ruff, mypy, etc.)
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── pyproject.toml              # Build, metadata & dependency configuration
├── src/
│   └── dexpi_pid_renderer/     # Core package source code
│       ├── __init__.py         # Public API exports
│       ├── cli.py              # Command-line interface parser and entry point
│       ├── dexpi_model.py      # Model loader & caching provider
│       ├── dexpi_to_image_file.py # File saving logic for SVG, PDF, PNG, JPG/JPEG
│       ├── export.py           # High-level dispatcher with dynamic argument filtering
│       └── pid_rendering.py    # SVG rendering & PyMuPDF/WeasyPrint byte converters
├── examples/                   # Runnable example scripts
│   └── render_pid.py
└── tests/                      # Suite of unit & integration tests
    ├── __init__.py
    ├── conftest.py
    ├── test_dexpi_model.py
    ├── test_dexpi_to_image_file.py
    ├── test_export.py
    └── test_pid_rendering.py
```

---

## Development & Testing
1. #### Environment setup
- Create and activate a virtual environment based on your platform:
  - **Linux / macOS**:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
  - **Windows (CMD)**:
    ```dos
    python -m venv .venv
    .venv\Scripts\activate.bat
    ```
  - **Windows (PowerShell)**:
    ```ps
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```
- Install all development and example dependencies:
    ```bash
    pip install -e ".[dev,examples]"
    ```

2. #### Running Tests:
- Run the pytest suite:

    ```bash
    pytest
    ```
- The test suite covers:
  - `test_dexpi_model.py`: XML validation, path normalization, and DexpiModelProvider caching.
- `test_pid_rendering.p`y: Raw SVG rendering, HTML wrapping, and byte conversion helpers.
- `test_dexpi_to_image_file.p`y: Direct file persistence, page slicing offsets (`start_page`/`end_page`), and file extension verification for SVG, PDF, PNG, and JPG/JPEG.
- `test_export.py`: High-level `export_dexpi_to_drawing_file` dispatch, error handling for unsupported formats, and signature-based dynamic argument filtering (`_filter_saver_arguments`).

3. #### Linting and Type Checking:

    ```bash
    mypy src/
    ruff check .
    ```

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
