from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from pydexpi.dexpi_classes.dexpiModel import DexpiModel
from pydexpi.loaders import ProteusSerializer


class DexpiLoadError(Exception):
    """Raised when a DEXPI model cannot be loaded or parsed."""


def load_dexpi_model(filepath: str | Path) -> DexpiModel:
    """Load and parse a DEXPI P&ID model."""
    if not isinstance(filepath, (str, Path)):
        raise TypeError("'filepath' must be a `str` or `Path`")

    filepath = (
        Path(filepath)
        .expanduser()
        .resolve()
    )

    if filepath.suffix.lower() != ".xml":
        raise ValueError("'filepath' must be a .xml file")

    if not filepath.is_file():
        raise FileNotFoundError(
            f"The file, '{filepath}', does not exist"
        )

    model_serializer = ProteusSerializer()

    try:
        model: DexpiModel = model_serializer.load(
            filepath.parent,
            filepath.name
        )
    except (
            ElementTree.ParseError,
            ValueError,
            AttributeError,
            KeyError
    ) as exc:
        raise DexpiLoadError(
            f"Failed to parse or validate DEXPI file structure: {exc}"
        ) from exc

    return model


class DexpiModelCache:
    """In-memory cache of DEXPI models keyed by source file path."""

    def __init__(self) -> None:
        self._models: dict[Path, DexpiModel] = {}

    @staticmethod
    def _normalize_path(path: str | Path) -> Path:
        return Path(path).expanduser().resolve()

    def get(self, path: str | Path) -> DexpiModel | None:
        return self._models.get(
            self._normalize_path(path)
        )

    def set(self, path: str | Path, model: DexpiModel) -> None:
        self._models[
            self._normalize_path(path)
        ] = model

    def remove(self, path: str | Path) -> None:
        self._models.pop(
            self._normalize_path(path),
            None
        )

    def clear(self) -> None:
        self._models.clear()

    def paths(self) -> tuple[Path, ...]:
        """Return the source paths of all cached models."""
        return tuple(self._models)

    def __contains__(self, path: str | Path) -> bool:
        return self._normalize_path(path) in self._models

    def __len__(self) -> int:
        return len(self._models)


class DexpiModelProvider:
    """Provides DEXPI models using an in-memory path-keyed cache."""

    def __init__(self, cache: DexpiModelCache | None = None) -> None:
        self._cache = (
            cache
            if cache is not None
            else DexpiModelCache()
        )

    def get(
        self,
        filepath: str | Path,
        *,
        reload: bool = False,
    ) -> DexpiModel:
        if not isinstance(filepath, (str, Path)):
            raise TypeError("'filepath' must be a `str` or `Path`")

        if not reload:
            cached_model = self._cache.get(filepath)

            if cached_model is not None:
                return cached_model

        model = load_dexpi_model(filepath)
        self._cache.set(filepath, model)

        return model

    def clear(self) -> None:
        self._cache.clear()