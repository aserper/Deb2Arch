"""Parser for Debian control files."""

from pathlib import Path
from typing import Optional

from debian.deb822 import Deb822

from deb2arch.exceptions import ParseError
from deb2arch.models import Architecture, DebControl


def parse_control_file(control_path: Path) -> DebControl:
    """Parse a Debian control file into a DebControl model.

    Args:
        control_path: Path to the control file.

    Returns:
        Parsed DebControl object.

    Raises:
        ParseError: If the control file cannot be parsed.
    """
    if not control_path.exists():
        raise ParseError(f"Control file not found: {control_path}")

    try:
        content = control_path.read_text()
        return parse_control_string(content)
    except Exception as e:
        raise ParseError(f"Failed to parse control file: {e}") from e


def parse_control_string(content: str) -> DebControl:
    """Parse control file content string into a DebControl model.

    Args:
        content: Control file content as string.

    Returns:
        Parsed DebControl object.

    Raises:
        ParseError: If the content cannot be parsed.
    """
    try:
        deb = Deb822(content)

        package = deb.get("Package")
        if not package:
            raise ParseError("Control file missing required 'Package' field")

        version = deb.get("Version")
        if not version:
            raise ParseError("Control file missing required 'Version' field")

        arch_str = deb.get("Architecture", "all")
        architecture = Architecture.from_string(arch_str)

        # Parse installed size
        installed_size: Optional[int] = None
        if "Installed-Size" in deb:
            try:
                installed_size = int(deb["Installed-Size"])
            except ValueError:
                pass

        return DebControl(
            package=package,
            version=version,
            architecture=architecture,
            maintainer=deb.get("Maintainer"),
            installed_size=installed_size,
            description=deb.get("Description", ""),
            depends=parse_dependency_list(deb.get("Depends", "")),
            pre_depends=parse_dependency_list(deb.get("Pre-Depends", "")),
            recommends=parse_dependency_list(deb.get("Recommends", "")),
            suggests=parse_dependency_list(deb.get("Suggests", "")),
            conflicts=parse_dependency_list(deb.get("Conflicts", "")),
            breaks=parse_dependency_list(deb.get("Breaks", "")),
            provides=parse_dependency_list(deb.get("Provides", "")),
            replaces=parse_dependency_list(deb.get("Replaces", "")),
            section=deb.get("Section"),
            priority=deb.get("Priority"),
            homepage=deb.get("Homepage"),
            source=deb.get("Source"),
        )
    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse control content: {e}") from e


def parse_dependency_list(deps_str: str) -> list[str]:
    """Parse a comma-separated dependency list.

    Handles version constraints and alternatives (|).
    For alternatives, takes the first option.

    Args:
        deps_str: Comma-separated dependency string.

    Returns:
        List of package names (without version constraints).
    """
    if not deps_str.strip():
        return []

    deps = []
    for dep in deps_str.split(","):
        dep = dep.strip()
        if not dep:
            continue

        # Handle alternatives (a | b) - take first
        if "|" in dep:
            dep = dep.split("|")[0].strip()

        # Extract package name (remove version constraints)
        # e.g., "libc6 (>= 2.17)" -> "libc6"
        if "(" in dep:
            dep = dep.split("(")[0].strip()

        # Remove :arch suffix (e.g., "libc6:amd64" -> "libc6")
        if ":" in dep:
            dep = dep.split(":")[0].strip()

        if dep:
            deps.append(dep)

    return deps


def clean_version(version: str) -> str:
    """Clean Debian version to Arch-compatible format.

    - Removes epoch (1:2.3.4 -> 2.3.4)
    - Replaces hyphens with underscores (2.3.4-1 -> 2.3.4_1)
    - Replaces tildes with underscores (2.3.4~beta -> 2.3.4_beta)

    Args:
        version: Debian version string.

    Returns:
        Arch-compatible version string.
    """
    # Remove epoch (e.g., "1:2.3.4" -> "2.3.4")
    if ":" in version:
        version = version.split(":", 1)[1]

    # Replace invalid characters for Arch
    version = version.replace("-", "_")
    version = version.replace("~", "_")
    version = version.replace("+", "_")

    return version
