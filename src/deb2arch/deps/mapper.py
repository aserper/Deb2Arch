"""Dependency mapper for converting Debian package names to Arch Linux."""

import re
from typing import Optional

from deb2arch.deps.mappings import NAME_MAPPINGS, VIRTUAL_MAPPINGS
from deb2arch.deps.pkgfile import PkgFile
from deb2arch.models import DependencyMapping, DependencySource, DependencyStatus


class DependencyMapper:
    """Maps Debian dependencies to Arch Linux packages."""

    def __init__(
        self,
        user_mappings: Optional[dict[str, str]] = None,
        pkgfile: Optional[PkgFile] = None,
    ):
        """Initialize the mapper.

        Args:
            user_mappings: Optional dictionary of user-defined mappings.
            pkgfile: Optional PkgFile instance for file-based lookup.
        """
        self.user_mappings = user_mappings or {}
        self.pkgfile = pkgfile or PkgFile()

    def map_dependency(self, deb_name: str) -> DependencyMapping:
        """Map a Debian dependency to an Arch package.

        Args:
            deb_name: The Debian package name (e.g., "python3-requests").

        Returns:
            DependencyMapping object with the result.
        """
        # Strip version constraints and architecture
        clean_name = self._clean_package_name(deb_name)

        # 1. Check user mappings
        if clean_name in self.user_mappings:
            return DependencyMapping(
                debian_name=deb_name,
                arch_name=self.user_mappings[clean_name],
                status=DependencyStatus.MAPPED,
                source=DependencySource.USER,
            )

        # 2. Check built-in mappings
        if clean_name in NAME_MAPPINGS:
            return DependencyMapping(
                debian_name=deb_name,
                arch_name=NAME_MAPPINGS[clean_name],
                status=DependencyStatus.MAPPED,
                source=DependencySource.BUILTIN,
            )

        # 3. Check virtual mappings
        if clean_name in VIRTUAL_MAPPINGS:
            # For now, just pick the first preference
            # Ideally we might prompt the user, but this is the automatic mapper
            return DependencyMapping(
                debian_name=deb_name,
                arch_name=VIRTUAL_MAPPINGS[clean_name][0],
                status=DependencyStatus.VIRTUAL,
                source=DependencySource.BUILTIN,
            )

        # 4. Check pkgfile (if available)
        # This is useful for things like "python3" which might be owned by "python"
        # But we also have built-in mappings for that.
        # This is more for shared libs like "libsomething.so.1" if passed as dep?
        # Debian dependencies are usually package names, not files.
        # But sometimes they match.
        if self.pkgfile.is_available:
            # Trying to map package name to package name via pkgfile isn't direct
            # unless we search for a typical file in that package?
            # actually pkgfile finds which package owns a file.
            # If we just have the package name, pkgfile isn't super helpful directly
            # UNLESS it's a library package implied by name?
            # Actually, `pkgfile` search is for filenames.
            pass

        # 5. Fuzzy matching / Heuristics
        fuzzy_match = self._fuzzy_match(clean_name)
        if fuzzy_match:
            return DependencyMapping(
                debian_name=deb_name,
                arch_name=fuzzy_match,
                status=DependencyStatus.MAPPED,
                source=DependencySource.FUZZY,
            )

        # Failed to map
        return DependencyMapping(
            debian_name=deb_name,
            status=DependencyStatus.UNMAPPED,
        )

    def _clean_package_name(self, name: str) -> str:
        """Clean Debian package name (remove version, arch)."""
        # Remove version constraints (e.g. " (>= 1.0)")
        name = name.split("(")[0].strip()
        # Remove architecture (e.g. ":amd64")
        name = name.split(":")[0].strip()
        return name

    def _fuzzy_match(self, name: str) -> Optional[str]:
        """Attempt to fuzzily match a Debian name to Arch."""
        # Common pattern: libfoo1 -> libfoo
        # Regex to strip trailing numbers/versions
        
        # Rule 1: python3-foo -> python-foo
        if name.startswith("python3-"):
            return name.replace("python3-", "python-")
            
        # Rule 2: libfoo-dev -> libfoo or foo (Arch includes headers usually)
        if name.endswith("-dev"):
             base = name[:-4]
             # check known mappings for base?
             # For now just strip -dev
             return base
             
        # Rule 3: remove version suffixes like -1, -1.2, 1a
        # e.g. libpng16-16 -> libpng
        # This is tricky because some libs need versions.
        # But commonly in Arch they are just "libpng" or "libpng12"
        
        # Strategy: strip trailing digits and separated digits
        # libfoo1 -> libfoo
        match = re.match(r"^(lib.+?)\d+$", name)
        if match:
            return match.group(1)
            
        return None
