"""Tests for the Arch package builder."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from deb2arch.core.builder import ArchBuilder
from deb2arch.exceptions import BuildError
from deb2arch.models import ArchPackageInfo

class TestArchBuilder:
    """Tests for ArchBuilder."""

    @pytest.fixture
    def mock_tools(self):
        """Mock external tools."""
        with patch("deb2arch.core.builder.shutil.which") as mock_which, \
             patch("deb2arch.core.builder.subprocess.run") as mock_run:
            mock_which.side_effect = lambda x: f"/usr/bin/{x}"
            
            def side_effect(cmd, **kwargs):
                if ".MTREE" in cmd:
                    # Create dummy .MTREE if we are in content_dir
                    cwd = kwargs.get("cwd")
                    if cwd:
                        (cwd / ".MTREE").touch()
                elif cmd[0] == "gzip":
                    # Simulate gzip: create .gz file and remove original
                    original = Path(cmd[-1])
                    if original.exists():
                        (original.parent / (original.name + ".gz")).touch()
                        original.unlink()
                return MagicMock(returncode=0)
                
            mock_run.side_effect = side_effect
            yield mock_which, mock_run

    def test_init_raises_if_tools_missing(self):
        """Test that init raises if tools are missing."""
        with patch("deb2arch.core.builder.shutil.which") as mock_which:
            mock_which.return_value = None
            with pytest.raises(BuildError, match="required but not found"):
                ArchBuilder()

    def test_fix_directory_structure(self, tmp_path, mock_tools):
        """Test directory structure fixing (usr move)."""
        builder = ArchBuilder()
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        
        # Create legacy structure
        (content_dir / "bin").mkdir()
        (content_dir / "bin" / "hello").touch()
        (content_dir / "lib").mkdir()
        (content_dir / "lib" / "libfoo.so").touch()
        (content_dir / "usr" / "bin").mkdir(parents=True)
        (content_dir / "usr" / "bin" / "other").touch()
        
        builder._fix_directory_structure(content_dir)
        
        assert not (content_dir / "bin").exists()
        assert not (content_dir / "lib").exists()
        assert (content_dir / "usr" / "bin" / "hello").exists()
        assert (content_dir / "usr" / "bin" / "other").exists()
        assert (content_dir / "usr" / "lib" / "libfoo.so").exists()

    def test_overwrite_on_move(self, tmp_path, mock_tools):
        """Test that existing files are overwritten during move."""
        builder = ArchBuilder()
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        
        (content_dir / "bin").mkdir()
        (content_dir / "bin" / "conflict").write_text("new")
        (content_dir / "usr" / "bin").mkdir(parents=True)
        (content_dir / "usr" / "bin" / "conflict").write_text("old")
        
        builder._fix_directory_structure(content_dir)
        
        assert (content_dir / "usr" / "bin" / "conflict").read_text() == "new"

    def test_build_package_flow(self, tmp_path, mock_tools):
        """Test the full build flow."""
        mock_which, mock_run = mock_tools
        builder = ArchBuilder()
        content_dir = tmp_path / "content"
        output_dir = tmp_path / "output"
        content_dir.mkdir()
        output_dir.mkdir()
        
        info = ArchPackageInfo(
            pkgname="testpkg",
            pkgver="1.0",
            pkgdesc="Test Package",
        )
        
        pkg = builder.build_package(info, content_dir, output_dir)
        
        assert pkg.name == "testpkg-1.0-1-x86_64.pkg.tar.zst"
        assert (content_dir / ".PKGINFO").exists()
        assert (content_dir / ".MTREE").exists() # Mocked subprocess success but file not created by verified mock run?
        # Actually our mock_run doesn't create file.
        # But `_generate_mtree` checks if .MTREE exists to gzip it.
        # So we should create .MTREE in side effect if we want that path to cover.
        # But verifying subprocess calls is enough.
        
        # Verify subprocess calls
        assert mock_run.call_count >= 2 # mtree and create_archive
        
        # Verify .PKGINFO content
        pkginfo = (content_dir / ".PKGINFO").read_text()
        assert "pkgname = testpkg" in pkginfo
        assert "packager = deb2arch" in pkginfo
