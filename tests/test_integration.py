"""Integration tests for deb2arch."""

import pytest
import shutil
import subprocess
from pathlib import Path

from deb2arch.core.converter import Converter
from deb2arch.models import ConversionResult

class TestIntegration:
    """Integration tests."""

    @pytest.fixture
    def hello_deb(self, fixtures_dir):
        """Path to hello.deb fixture."""
        return fixtures_dir / "hello.deb"

    def test_convert_hello_deb(self, hello_deb, tmp_path):
        """Test converting hello.deb end-to-end."""
        output_dir = tmp_path / "output"
        converter = Converter(output_dir=output_dir, quiet=True)
        
        result = converter.convert(str(hello_deb))
        
        assert result.success
        assert result.package_path
        assert result.package_path.exists()
        assert result.package_path.name.startswith("hello-2.10_3-1-x86_64.pkg.tar.zst")
        
        # Verify package content roughly using tar
        # bsdtar -tf package
        cmd = ["bsdtar", "-tf", str(result.package_path)]
        output = subprocess.check_output(cmd, text=True)
        
        assert ".PKGINFO" in output
        assert ".MTREE" in output
        assert "usr/bin/hello" in output
        assert "usr/share/man/man1/hello.1.gz" in output
        
        # Verify .PKGINFO content
        cmd_info = ["bsdtar", "-xOf", str(result.package_path), ".PKGINFO"]
        pkginfo = subprocess.check_output(cmd_info, text=True)
        
        assert "pkgname = hello" in pkginfo
        assert "pkgver = 2.10_3-1" in pkginfo
        assert "depend = glibc" in pkginfo  # libc6 -> glibc mapping
