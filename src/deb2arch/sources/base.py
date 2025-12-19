"""Base class for package sources."""

from abc import ABC, abstractmethod
from pathlib import Path


class PackageSource(ABC):
    """Abstract base class for package sources."""

    @abstractmethod
    def get_package(self, target: str) -> Path:
        """Retrieve the package.

        Args:
            target: The target string (path, URL, or package name).

        Returns:
            Path to the local .deb file.

        Raises:
            DownloadError: If download fails.
            FileNotFoundError: If file not found.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup temporary files if any."""
        pass
