"""Tests for the control file parser."""

import pytest
from pathlib import Path

from deb2arch.core.parser import (
    clean_version,
    parse_control_string,
    parse_dependency_list,
)
from deb2arch.exceptions import ParseError
from deb2arch.models import Architecture


class TestParseDependencyList:
    """Tests for parse_dependency_list function."""

    def test_empty_string(self):
        assert parse_dependency_list("") == []

    def test_whitespace_only(self):
        assert parse_dependency_list("   ") == []

    def test_single_dependency(self):
        assert parse_dependency_list("libc6") == ["libc6"]

    def test_multiple_dependencies(self):
        result = parse_dependency_list("libc6, libssl3, zlib1g")
        assert result == ["libc6", "libssl3", "zlib1g"]

    def test_dependency_with_version(self):
        result = parse_dependency_list("libc6 (>= 2.34)")
        assert result == ["libc6"]

    def test_dependency_with_complex_version(self):
        result = parse_dependency_list("libc6 (>= 2.34), libssl3 (>= 3.0.0~alpha)")
        assert result == ["libc6", "libssl3"]

    def test_alternatives_takes_first(self):
        result = parse_dependency_list("python3 | python, vim | emacs")
        assert result == ["python3", "vim"]

    def test_alternatives_with_versions(self):
        result = parse_dependency_list("libssl3 (>= 3.0) | libssl1.1 (>= 1.1)")
        assert result == ["libssl3"]

    def test_arch_suffix_removed(self):
        result = parse_dependency_list("libc6:amd64, libssl3:i386")
        assert result == ["libc6", "libssl3"]

    def test_mixed_complex_deps(self):
        result = parse_dependency_list(
            "libc6 (>= 2.34), python3 (>= 3.10) | python3.9, libfoo:amd64"
        )
        assert result == ["libc6", "python3", "libfoo"]


class TestCleanVersion:
    """Tests for clean_version function."""

    def test_simple_version(self):
        assert clean_version("1.2.3") == "1.2.3"

    def test_version_with_debian_revision(self):
        assert clean_version("2.10-3") == "2.10_3"

    def test_version_with_epoch(self):
        assert clean_version("1:2.3.4-5") == "2.3.4_5"

    def test_version_with_tilde(self):
        assert clean_version("2.0.0~beta1-1") == "2.0.0_beta1_1"

    def test_version_with_plus(self):
        assert clean_version("1.0+git20231225-1") == "1.0_git20231225_1"

    def test_complex_version(self):
        assert clean_version("1:2.0.0~rc1+dfsg-1ubuntu2") == "2.0.0_rc1_dfsg_1ubuntu2"


class TestParseControlString:
    """Tests for parse_control_string function."""

    def test_minimal_control(self):
        content = """Package: test
Version: 1.0
Architecture: amd64
"""
        control = parse_control_string(content)
        assert control.package == "test"
        assert control.version == "1.0"
        assert control.architecture == Architecture.AMD64

    def test_missing_package_raises(self):
        content = """Version: 1.0
Architecture: amd64
"""
        with pytest.raises(ParseError, match="Package"):
            parse_control_string(content)

    def test_missing_version_raises(self):
        content = """Package: test
Architecture: amd64
"""
        with pytest.raises(ParseError, match="Version"):
            parse_control_string(content)

    def test_full_control(self, sample_control_content):
        control = parse_control_string(sample_control_content)

        assert control.package == "hello"
        assert control.version == "2.10-3"
        assert control.architecture == Architecture.AMD64
        assert control.maintainer == "Santiago Vila <sanvila@debian.org>"
        assert control.installed_size == 277
        assert control.depends == ["libc6"]
        assert control.conflicts == ["hello-traditional"]
        assert control.breaks == ["hello-debhelper"]
        assert control.replaces == ["hello-debhelper", "hello-traditional"]
        assert control.section == "devel"
        assert control.priority == "optional"
        assert control.homepage == "https://www.gnu.org/software/hello/"
        assert "example package" in control.description

    def test_complex_dependencies(self, complex_depends_content):
        control = parse_control_string(complex_depends_content)

        assert control.package == "test-complex"
        assert control.version == "1:2.0.0~beta1-1ubuntu2"
        assert control.depends == ["libc6", "libssl3", "python3"]
        assert control.pre_depends == ["dpkg"]
        assert control.recommends == ["vim", "git"]
        assert control.suggests == ["docker-ce"]
        assert control.conflicts == ["test-old"]
        assert control.provides == ["test-provider"]

    def test_unknown_architecture_defaults_to_all(self):
        content = """Package: test
Version: 1.0
Architecture: sparc64
"""
        control = parse_control_string(content)
        assert control.architecture == Architecture.ALL
