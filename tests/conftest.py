"""Pytest configuration and fixtures for deb2arch tests."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def hello_deb(fixtures_dir: Path) -> Path:
    """Return the path to the hello.deb test fixture."""
    deb_path = fixtures_dir / "hello.deb"
    if not deb_path.exists():
        pytest.skip("hello.deb fixture not found")
    return deb_path


@pytest.fixture
def sample_control_content() -> str:
    """Return sample control file content for testing."""
    return """Package: hello
Version: 2.10-3
Architecture: amd64
Maintainer: Santiago Vila <sanvila@debian.org>
Installed-Size: 277
Depends: libc6 (>= 2.34)
Conflicts: hello-traditional
Breaks: hello-debhelper (<< 2.9)
Replaces: hello-debhelper (<< 2.9), hello-traditional
Section: devel
Priority: optional
Homepage: https://www.gnu.org/software/hello/
Description: example package based on GNU hello
 The GNU hello program produces a familiar, friendly greeting.  It
 allows non-programmers to use a classic computer science tool which
 would otherwise be unavailable to them.
 .
 Seriously, though: this is an example of how to do a Debian package.
 It is the Debian version of the GNU Project's `hello world' program
 (which is itself an example for the GNU Project)."""


@pytest.fixture
def complex_depends_content() -> str:
    """Return control content with complex dependencies for testing."""
    return """Package: test-complex
Version: 1:2.0.0~beta1-1ubuntu2
Architecture: amd64
Maintainer: Test <test@example.com>
Depends: libc6 (>= 2.34), libssl3 | libssl1.1, python3 (>= 3.10) | python3.9
Pre-Depends: dpkg (>= 1.19.0)
Recommends: vim | emacs, git
Suggests: docker-ce
Conflicts: test-old
Provides: test-provider
Description: A test package with complex dependencies
"""
