"""Tests for data models."""

import pytest

from deb2arch.models import (
    Architecture,
    DebControl,
    DependencyMapping,
    DependencySource,
    DependencyStatus,
)


class TestArchitecture:
    """Tests for Architecture enum."""

    def test_amd64_to_x86_64(self):
        arch = Architecture.AMD64
        assert arch.to_arch() == "x86_64"

    def test_i386_to_i686(self):
        arch = Architecture.I386
        assert arch.to_arch() == "i686"

    def test_arm64_to_aarch64(self):
        arch = Architecture.ARM64
        assert arch.to_arch() == "aarch64"

    def test_all_to_any(self):
        arch = Architecture.ALL
        assert arch.to_arch() == "any"

    def test_from_string_valid(self):
        arch = Architecture.from_string("amd64")
        assert arch == Architecture.AMD64

    def test_from_string_case_insensitive(self):
        arch = Architecture.from_string("AMD64")
        assert arch == Architecture.AMD64

    def test_from_string_unknown_returns_all(self):
        arch = Architecture.from_string("unknown_arch")
        assert arch == Architecture.ALL


class TestDebControl:
    """Tests for DebControl model."""

    def test_minimal_control(self):
        control = DebControl(
            package="test",
            version="1.0",
            architecture=Architecture.AMD64,
        )
        assert control.package == "test"
        assert control.version == "1.0"
        assert control.depends == []

    def test_full_control(self):
        control = DebControl(
            package="hello",
            version="2.10-3",
            architecture=Architecture.AMD64,
            maintainer="Test <test@example.com>",
            depends=["libc6"],
            conflicts=["hello-old"],
            description="A test package",
            homepage="https://example.com",
        )
        assert control.package == "hello"
        assert control.depends == ["libc6"]
        assert control.conflicts == ["hello-old"]


class TestDependencyMapping:
    """Tests for DependencyMapping model."""

    def test_unmapped_dependency(self):
        mapping = DependencyMapping(debian_name="unknown-pkg")
        assert mapping.debian_name == "unknown-pkg"
        assert mapping.arch_name is None
        assert mapping.status == DependencyStatus.UNMAPPED
        assert mapping.source == DependencySource.NONE

    def test_mapped_dependency(self):
        mapping = DependencyMapping(
            debian_name="libc6",
            arch_name="glibc",
            status=DependencyStatus.MAPPED,
            source=DependencySource.BUILTIN,
        )
        assert mapping.arch_name == "glibc"
        assert mapping.status == DependencyStatus.MAPPED
