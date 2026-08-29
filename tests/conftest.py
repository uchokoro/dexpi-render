from pathlib import Path

import pytest


@pytest.fixture
def sample_xml(tmp_path: Path) -> Path:
    """Creates a temporary valid XML file for testing CLI inputs."""
    xml_file = tmp_path / "sample.xml"
    xml_file.write_text("<Equipment></Equipment>", encoding="utf-8")
    return xml_file
