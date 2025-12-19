"""Tests for the deb extractor."""

import pytest
from pathlib import Path

from deb2arch.core.extractor import DebExtractor
from deb2arch.exceptions import ExtractionError
from deb2arch.models import Architecture


class TestDebExtractor:
    """Tests for DebExtractor class."""

    def test_extract_hello_deb(self, hello_deb: Path):
        """Test extracting the hello.deb test fixture."""
        with DebExtractor() as extractor:
            package = extractor.extract(hello_deb)

            # Check control metadata
            assert package.control.package == "hello"
            assert package.control.version == "2.10-3"
            assert package.control.architecture == Architecture.AMD64
            assert package.control.maintainer == "Santiago Vila <sanvila@debian.org>"
            assert package.control.installed_size == 277
            assert package.control.depends == ["libc6"]
            assert package.control.conflicts == ["hello-traditional"]
            assert package.control.homepage == "https://www.gnu.org/software/hello/"

            # Check data extraction
            assert package.data_dir.exists()
            hello_binary = package.data_dir / "usr" / "bin" / "hello"
            assert hello_binary.exists()

            # Check man page exists
            man_page = package.data_dir / "usr" / "share" / "man" / "man1" / "hello.1.gz"
            assert man_page.exists()

    def test_extract_returns_correct_dirs(self, hello_deb: Path):
        """Test that extraction returns valid directories."""
        with DebExtractor() as extractor:
            package = extractor.extract(hello_deb)

            assert package.control_dir.exists()
            assert package.data_dir.exists()
            assert (package.control_dir / "control").exists()

    def test_extract_nonexistent_file_raises(self):
        """Test that extracting nonexistent file raises error."""
        with DebExtractor() as extractor:
            with pytest.raises(ExtractionError, match="not found"):
                extractor.extract(Path("/nonexistent/path.deb"))

    def test_cleanup_removes_temp_dir(self, hello_deb: Path):
        """Test that cleanup removes temporary directory."""
        extractor = DebExtractor()
        package = extractor.extract(hello_deb)

        work_dir = extractor.work_dir
        assert work_dir.exists()

        extractor.cleanup()
        assert not work_dir.exists()

    def test_context_manager_cleanup(self, hello_deb: Path):
        """Test that context manager properly cleans up."""
        with DebExtractor() as extractor:
            package = extractor.extract(hello_deb)
            work_dir = extractor.work_dir
            assert work_dir.exists()

        # After context exit, temp dir should be gone
        assert not work_dir.exists()

    def test_custom_work_dir(self, hello_deb: Path, tmp_path: Path):
        """Test using a custom work directory."""
        custom_dir = tmp_path / "custom_work"
        extractor = DebExtractor(work_dir=custom_dir)

        try:
            package = extractor.extract(hello_deb)
            assert extractor.work_dir == custom_dir
            assert (custom_dir / "control" / "control").exists()
            assert (custom_dir / "data" / "usr" / "bin" / "hello").exists()
        finally:
            # Manual cleanup since custom dir won't be auto-deleted
            pass

    def test_no_scripts_in_hello(self, hello_deb: Path):
        """Test that hello.deb has no maintainer scripts."""
        with DebExtractor() as extractor:
            package = extractor.extract(hello_deb)

            # hello package typically has no scripts
            assert package.preinst is None
            assert package.postinst is None
            assert package.prerm is None
            assert package.postrm is None

    def test_no_conffiles_in_hello(self, hello_deb: Path):
        """Test that hello.deb has no conffiles."""
        with DebExtractor() as extractor:
            package = extractor.extract(hello_deb)

            assert package.conffiles == []


class TestDebExtractorIntegration:
    """Integration tests for DebExtractor with real package inspection."""

    def test_extracted_binary_is_executable(self, hello_deb: Path):
        """Test that extracted binary has executable permissions."""
        with DebExtractor() as extractor:
            package = extractor.extract(hello_deb)

            hello_binary = package.data_dir / "usr" / "bin" / "hello"
            # Check if file has any execute permission
            assert hello_binary.stat().st_mode & 0o111

    def test_locale_files_extracted(self, hello_deb: Path):
        """Test that locale files are properly extracted."""
        with DebExtractor() as extractor:
            package = extractor.extract(hello_deb)

            locale_dir = package.data_dir / "usr" / "share" / "locale"
            assert locale_dir.exists()

            # Check for at least some locales
            locales = list(locale_dir.iterdir())
            assert len(locales) > 0

            # Check German locale as example
            de_locale = locale_dir / "de" / "LC_MESSAGES" / "hello.mo"
            assert de_locale.exists()
