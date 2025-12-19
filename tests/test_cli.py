"""Tests for CLI."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

from deb2arch.cli import main
from deb2arch.models import ConversionResult

class TestCli:
    """Tests for the CLI."""

    @pytest.fixture
    def runner(self):
        """Click test runner."""
        return CliRunner()

    @patch("deb2arch.cli.Converter")
    def test_convert_success(self, mock_converter_cls, runner):
        """Test successful conversion."""
        # Setup mock
        mock_instance = mock_converter_cls.return_value
        result = ConversionResult(
            success=True, 
            package_path=Path("/tmp/out/pkg.tar.zst")
        )
        mock_instance.convert.return_value = result
        
        # Run command
        result = runner.invoke(main, ["convert", "package.deb"])
        
        # Assertions
        assert result.exit_code == 0
        assert "Success" in result.output
        assert "/tmp/out/pkg.tar.zst" in result.output
        mock_converter_cls.assert_called()
        mock_instance.convert.assert_called_with("package.deb")

    @patch("deb2arch.cli.Converter")
    def test_convert_failure(self, mock_converter_cls, runner):
        """Test failed conversion."""
        # Setup mock
        mock_instance = mock_converter_cls.return_value
        result = ConversionResult(
            success=False, 
            errors=["Something went wrong"]
        )
        mock_instance.convert.return_value = result
        
        # Run command
        result = runner.invoke(main, ["convert", "package.deb"])
        
        # Assertions
        assert result.exit_code == 1
        assert "Conversion Failed" in result.output
        assert "Something went wrong" in result.output

    @patch("deb2arch.cli.Converter")
    def test_convert_with_opts(self, mock_converter_cls, runner):
        """Test conversion with options."""
        mock_instance = mock_converter_cls.return_value
        mock_instance.convert.return_value = ConversionResult(success=True)
        
        runner.invoke(main, ["convert", "package.deb", "--quiet", "--install", "-o", "/out"])
        
        mock_converter_cls.assert_called_with(
            output_dir=Path("/out"),
            install=True,
            quiet=True
        )
