from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydexpi.dexpi_classes.dexpiModel import DexpiModel

from dexpi_pid_renderer import DexpiModelProvider


@pytest.fixture
def sample_xml(tmp_path: Path) -> Path:
    """Create a temporary valid XML file for testing CLI inputs."""
    xml_file = tmp_path / "sample.xml"
    xml_file.write_text("<Equipment></Equipment>", encoding="utf-8")
    return xml_file


@pytest.fixture
def mock_dexpi_model() -> MagicMock:
    """Create a mock DEXPI model with a mock diagram."""
    model = MagicMock(spec=DexpiModel)
    model.diagram = MagicMock()
    return model


@pytest.fixture
def mock_dexpi_model_provider(
    mock_dexpi_model: MagicMock,
) -> MagicMock:
    """Create a mock DexpiModelProvider with a mock DEXPI model."""
    provider = MagicMock(spec=DexpiModelProvider)
    provider.get.return_value = mock_dexpi_model
    return provider
