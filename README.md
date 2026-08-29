# DEXPI P&ID Renderer

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for parsing DEXPI-compliant Piping and Instrumentation Diagrams (P&IDs) and rendering them into high-quality vector drawings in **SVG** and **PDF** formats.

---

## Features

* **XML Model Parsing:** Load and validate DEXPI XML files seamlessly using `pydexpi`.
* **In-Memory Caching:** High-performance model provider (`DexpiModelProvider`) featuring path-keyed caching to avoid re-parsing models.
* **Vector Output:** Export P&ID diagrams to standalone **SVG** or formatted **PDF** files with configurable page sizes and orientations.
* **Customization:** Adjust padding, toggle background boxes, and apply visual styling options.

---

## Installation

### Prerequisites
* Python **3.12** or higher
* [WeasyPrint dependencies](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) (system libraries required for PDF rendering)

### Install from Source
Clone the repository and install the package:

```bash
git clone [https://github.com/your-username/dexpi-pid-renderer.git](https://github.com/your-username/dexpi-pid-renderer.git)
cd dexpi-pid-renderer

# Install core package
pip install .

# Or install in editable mode with development/example tools
pip install -e ".[dev,examples]"
```

---

## Usage

### Basic Drawing Export
The quickest way to render a DEXPI model to a file is using `export_dexpi_to_drawing_file`:

```python
from pathlib import Path
from dexpi_pid_renderer import export_dexpi_to_drawing_file

# Render a DEXPI XML file to SVG
svg_path = export_dexpi_to_drawing_file(
    filepath="path/to/model.xml",
    output_filepath="output/model.svg",
    output_format="svg",
    padding=0.5,
    pretty_formatting=True,
    add_background_box=True,
    create_output_directory=True,
)

print(f"Exported SVG to: {svg_path}")

# Render to a landscape A4 PDF file
pdf_path = export_dexpi_to_drawing_file(
    filepath="path/to/model.xml",
    output_filepath="output/model.pdf",
    output_format="pdf",
    page_size="A4",
    orientation="landscape",
    create_output_directory=True,
)

print(f"Exported PDF to: {pdf_path}")
```

### Advanced: Model Caching & Programmatic Rendering
If you are rendering multiple formats from the same DEXPI model, use `DexpiModelProvider` to cache the parsed XML structure:

```python
from dexpi_pid_renderer import (
    DexpiModelProvider,
    render_pid_as_svg,
    save_svg_bytes_to_pdf,
)

provider = DexpiModelProvider()

# Loads and caches the model
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
You can run the CLI tool directly from your terminal:

```bash
dexpi-render path/to/model.xml -o output/model.pdf --format pdf --page-size A4 --orientation landscape
```

---

## Running the Examples

The repository includes a ready-to-run example script under `examples/render_pid.py` that demonstrates loading a DEXPI file and exporting it to a drawing format.

### 1. Set Up Environment Variables
Copy the provided `.env.example` template to create your local `.env` configuration file:

```bash
cp .env.example .env
```

Open .env in your editor and configure the file paths to point to your DEXPI XML file and desired output directory:

```
DEXPI_FILEPATH="path/to/your/input_model.xml"
DRAWING_OUTPUT_DIR="path/to/your/output_directory"
```

### 2. Install Required Dependencies
Ensure you have installed the optional examples dependencies (python-dotenv):

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
│       ├── __init__.py         # Public API exposures
│       ├── cli.py              # Command-line interface entry point
│       ├── dexpi_model.py      # Model loader & caching provider
│       ├── export.py           # High-level file export functions
│       └── pid_rendering.py    # SVG & PDF rendering utilities
├── examples/                   # Runnable example scripts
│   └── render_pid.py
└── tests/                      # Suite of unit & integration tests
    ├── __init__.py
    ├── test_dexpi_model.py
    ├── test_export.py
    └── test_pid_rendering.py
```

---

## Development & Testing
1. **Set up virtual environment & dependencies**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -e ".[dev,examples]"
    ```
2. **Run tests**:

    ```bash
    pytest
    ```
3. **Check type annotations & linting**:

    ```bash
    mypy src/
    ruff check .
    ```

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
