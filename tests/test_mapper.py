"""Tests for dependency mapper."""

import pytest
from unittest.mock import MagicMock

from deb2arch.deps.mapper import DependencyMapper
from deb2arch.deps.pkgfile import PkgFile
from deb2arch.models import DependencySource, DependencyStatus


class TestDependencyMapper:
    """Tests for DependencyMapper."""

    def test_clean_package_name(self):
        """Test cleaning of package names."""
        mapper = DependencyMapper()
        
        assert mapper._clean_package_name("python3 (>= 3.9)") == "python3"
        assert mapper._clean_package_name("libc6:amd64") == "libc6"
        assert mapper._clean_package_name("pkg (>> 1.0) | pkg-alt") == "pkg"  # Simple split handles first
        
    def test_builtin_mapping(self):
        """Test built-in mappings."""
        mapper = DependencyMapper()
        
        mapping = mapper.map_dependency("libc6")
        assert mapping.status == DependencyStatus.MAPPED
        assert mapping.source == DependencySource.BUILTIN
        assert mapping.arch_name == "glibc"
        
    def test_user_mapping_priority(self):
        """Test that user mappings override built-ins."""
        user_mappings = {"libc6": "my-glibc"}
        mapper = DependencyMapper(user_mappings=user_mappings)
        
        mapping = mapper.map_dependency("libc6")
        assert mapping.status == DependencyStatus.MAPPED
        assert mapping.source == DependencySource.USER
        assert mapping.arch_name == "my-glibc"
        
    def test_fuzzy_matching_python(self):
        """Test fuzzy matching for python packages."""
        mapper = DependencyMapper()
        
        mapping = mapper.map_dependency("python3-requests")
        assert mapping.status == DependencyStatus.MAPPED
        assert mapping.source == DependencySource.FUZZY
        assert mapping.arch_name == "python-requests"

    def test_fuzzy_matching_lib(self):
        """Test fuzzy matching for libraries."""
        mapper = DependencyMapper()
        
        # libfoo1 -> libfoo
        mapping = mapper.map_dependency("libfoo1")
        assert mapping.status == DependencyStatus.MAPPED
        assert mapping.source == DependencySource.FUZZY
        assert mapping.arch_name == "libfoo"
        
    def test_virtual_mapping(self):
        """Test virtual package mapping."""
        mapper = DependencyMapper()
        
        mapping = mapper.map_dependency("www-browser")
        assert mapping.status == DependencyStatus.VIRTUAL
        assert mapping.source == DependencySource.BUILTIN
        # Should pick first alternative
        assert mapping.arch_name in ["firefox", "chromium", "lynx"]
        
    def test_unmapped(self):
        """Test unmapped dependency."""
        mapper = DependencyMapper()
        
        mapping = mapper.map_dependency("unknown-package-123")
        assert mapping.status == DependencyStatus.UNMAPPED
        assert mapping.arch_name is None
