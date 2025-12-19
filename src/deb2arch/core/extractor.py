"""Extractor for .deb package files."""

import shutil
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import arpy

from deb2arch.core.parser import parse_control_file
from deb2arch.exceptions import ExtractionError
from deb2arch.models import DebPackage


class DebExtractor:
    """Extract and parse .deb package files."""

    # Possible names for control and data archives
    CONTROL_TAR_NAMES = [
        b"control.tar.gz",
        b"control.tar.xz",
        b"control.tar.zst",
        b"control.tar.bz2",
        b"control.tar",
    ]
    DATA_TAR_NAMES = [
        b"data.tar.gz",
        b"data.tar.xz",
        b"data.tar.zst",
        b"data.tar.bz2",
        b"data.tar.lzma",
        b"data.tar",
    ]

    def __init__(self, work_dir: Optional[Path] = None):
        """Initialize the extractor.

        Args:
            work_dir: Working directory for extraction. If None, creates a temp dir.
        """
        if work_dir is None:
            self._temp_dir = tempfile.mkdtemp(prefix="deb2arch_")
            self.work_dir = Path(self._temp_dir)
        else:
            self._temp_dir = None
            self.work_dir = work_dir
            self.work_dir.mkdir(parents=True, exist_ok=True)

    def extract(self, deb_path: Path) -> DebPackage:
        """Extract a .deb file and return parsed package info.

        Args:
            deb_path: Path to the .deb file.

        Returns:
            DebPackage with extracted data and parsed control info.

        Raises:
            ExtractionError: If extraction fails.
        """
        if not deb_path.exists():
            raise ExtractionError(f"File not found: {deb_path}")

        control_dir = self.work_dir / "control"
        data_dir = self.work_dir / "data"
        control_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Open and read the AR archive
            with open(deb_path, "rb") as f:
                ar = arpy.Archive(fileobj=f)
                ar.read_all_headers()

                # Find and extract control archive
                control_member = self._find_member(ar, self.CONTROL_TAR_NAMES)
                if control_member is None:
                    raise ExtractionError("Invalid .deb: missing control archive")
                self._extract_tar_member(control_member, control_dir)

                # Find and extract data archive
                data_member = self._find_member(ar, self.DATA_TAR_NAMES)
                if data_member is None:
                    raise ExtractionError("Invalid .deb: missing data archive")
                self._extract_tar_member(data_member, data_dir)

        except ExtractionError:
            raise
        except Exception as e:
            raise ExtractionError(f"Failed to extract .deb file: {e}") from e

        # Parse control file
        control_file = control_dir / "control"
        if not control_file.exists():
            raise ExtractionError("No control file found in package")

        control = parse_control_file(control_file)

        # Read maintainer scripts
        scripts = {}
        for script_name in ["preinst", "postinst", "prerm", "postrm"]:
            script_path = control_dir / script_name
            if script_path.exists():
                scripts[script_name] = script_path.read_text()

        # Read conffiles
        conffiles: list[str] = []
        conffiles_path = control_dir / "conffiles"
        if conffiles_path.exists():
            conffiles = [
                line.strip()
                for line in conffiles_path.read_text().splitlines()
                if line.strip()
            ]

        return DebPackage(
            control=control,
            data_dir=data_dir,
            control_dir=control_dir,
            preinst=scripts.get("preinst"),
            postinst=scripts.get("postinst"),
            prerm=scripts.get("prerm"),
            postrm=scripts.get("postrm"),
            conffiles=conffiles,
        )

    def _find_member(
        self, ar: arpy.Archive, names: list[bytes]
    ) -> Optional[arpy.ArchiveFileData]:
        """Find a member in the AR archive by possible names.

        Args:
            ar: The AR archive.
            names: List of possible member names to look for.

        Returns:
            The archive member if found, None otherwise.
        """

        for name in names:
            if name in ar.archived_files:
                return ar.archived_files[name]
        return None

    def _extract_tar_member(
        self, ar_member: arpy.ArchiveFileData, dest: Path
    ) -> None:
        """Extract a tar archive member to destination directory.

        Args:
            ar_member: The AR archive member containing a tar archive.
            dest: Destination directory for extraction.

        Raises:
            ExtractionError: If extraction fails.
        """
        try:
            # Read the tar data into memory
            ar_member.seek(0)
            tar_data = ar_member.read()

            # Open as tar with automatic compression detection
            with tarfile.open(fileobj=BytesIO(tar_data), mode="r:*") as tar:
                # Use data filter for security (Python 3.12+) or extractall
                try:
                    tar.extractall(path=dest, filter="data")
                except TypeError:
                    # Python < 3.12 doesn't have filter parameter
                    tar.extractall(path=dest)

        except Exception as e:
            raise ExtractionError(f"Failed to extract tar archive: {e}") from e

    def cleanup(self) -> None:
        """Remove temporary working directory."""
        if self._temp_dir and Path(self._temp_dir).exists():
            shutil.rmtree(self._temp_dir)

    def __enter__(self) -> "DebExtractor":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - cleanup temp files."""
        self.cleanup()
