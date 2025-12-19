"""Tests for source handlers."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from deb2arch.sources.local import LocalSource
from deb2arch.sources.url import UrlSource
from deb2arch.exceptions import ExtractionError, DownloadError


class TestLocalSource:
    """Tests for LocalSource."""

    def test_get_existing_file(self, tmp_path):
        """Test getting an existing file."""
        f = tmp_path / "test.deb"
        f.touch()
        source = LocalSource()
        path = source.get_package(str(f))
        assert path == f
        assert path.exists()

    def test_get_nonexistent_file(self):
        """Test getting a nonexistent file raises."""
        source = LocalSource()
        with pytest.raises(FileNotFoundError):
            source.get_package("/nonexistent/file.deb")

    def test_get_directory_raises(self, tmp_path):
        """Test getting a directory raises."""
        source = LocalSource()
        with pytest.raises(ExtractionError, match="Not a file"):
            source.get_package(str(tmp_path))

class TestUrlSource:
    """Tests for UrlSource."""

    @patch("deb2arch.sources.url.download_file")
    def test_get_package(self, mock_download):
        """Test downloading a package."""
        source = UrlSource()
        url = "http://example.com/package.deb"
        expected_path = Path(source._temp_dir) / "package.deb"
        mock_download.return_value = expected_path
        
        path = source.get_package(url)
        
        assert path == expected_path
        mock_download.assert_called_once_with(url, expected_path)
        source.cleanup()

    def test_cleanup_removes_dir(self):
        """Test cleanup removes temporary directory."""
        source = UrlSource()
        temp_dir = Path(source._temp_dir)
        assert temp_dir.exists()
        
        source.cleanup()
        assert not temp_dir.exists()
