"""URL source handler."""

import tempfile
import shutil
from pathlib import Path
from typing import Optional

from deb2arch.sources.base import PackageSource
from deb2arch.utils.download import download_file


class UrlSource(PackageSource):
    """Handles URL sources."""

    def __init__(self):
        """Initialize"""
        self._temp_dir = tempfile.mkdtemp(prefix="deb2arch_dl_")

    def get_package(self, target: str) -> Path:
        """Download package from URL.

        Args:
            target: URL to download.

        Returns:
            Path to downloaded file.
        """
        filename = target.split("/")[-1] or "package.deb"
        dest = Path(self._temp_dir) / filename
        return download_file(target, dest)

    def cleanup(self) -> None:
        """Remove temporary directory."""
        if Path(self._temp_dir).exists():
            shutil.rmtree(self._temp_dir)
