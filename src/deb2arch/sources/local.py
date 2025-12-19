"""Local file source handler."""

from pathlib import Path
from typing import Optional

from deb2arch.sources.base import PackageSource
from deb2arch.exceptions import ExtractionError


class LocalSource(PackageSource):
    """Handles local .deb files."""

    def get_package(self, target: str) -> Path:
        """Return the path to the local file.

        Args:
            target: Path to local .deb file.

        Returns:
            Path object.
        """
        path = Path(target)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ExtractionError(f"Not a file: {path}")
            
        return path

    def cleanup(self) -> None:
        """Nothing to cleanup for local files."""
        pass
