"""Data models for deb2arch."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Architecture(str, Enum):
    """Debian architecture with mapping to Arch equivalents."""

    I386 = "i386"
    AMD64 = "amd64"
    ARMHF = "armhf"
    ARM64 = "arm64"
    ARMEL = "armel"
    MIPS = "mips"
    MIPSEL = "mipsel"
    MIPS64EL = "mips64el"
    PPC64EL = "ppc64el"
    S390X = "s390x"
    ALL = "all"

    def to_arch(self) -> str:
        """Convert Debian architecture to Arch Linux equivalent."""
        mapping = {
            "i386": "i686",
            "amd64": "x86_64",
            "armhf": "armv7h",
            "arm64": "aarch64",
            "armel": "arm",
            "all": "any",
        }
        return mapping.get(self.value, self.value)

    @classmethod
    def from_string(cls, value: str) -> "Architecture":
        """Create Architecture from string, with fallback to ALL for unknown."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.ALL


class DebControl(BaseModel):
    """Parsed Debian control file metadata."""

    package: str
    version: str
    architecture: Architecture
    maintainer: Optional[str] = None
    installed_size: Optional[int] = None
    description: str = ""
    depends: list[str] = Field(default_factory=list)
    pre_depends: list[str] = Field(default_factory=list)
    recommends: list[str] = Field(default_factory=list)
    suggests: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    breaks: list[str] = Field(default_factory=list)
    provides: list[str] = Field(default_factory=list)
    replaces: list[str] = Field(default_factory=list)
    section: Optional[str] = None
    priority: Optional[str] = None
    homepage: Optional[str] = None
    source: Optional[str] = None


class DebPackage(BaseModel):
    """Represents an extracted .deb package."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    control: DebControl
    data_dir: Path
    control_dir: Path
    preinst: Optional[str] = None
    postinst: Optional[str] = None
    prerm: Optional[str] = None
    postrm: Optional[str] = None
    conffiles: list[str] = Field(default_factory=list)


class DependencyStatus(str, Enum):
    """Status of a dependency mapping."""

    MAPPED = "mapped"
    UNMAPPED = "unmapped"
    SKIPPED = "skipped"
    VIRTUAL = "virtual"


class DependencySource(str, Enum):
    """Source of a dependency mapping."""

    BUILTIN = "builtin"
    CONFIG = "config"
    PKGFILE = "pkgfile"
    PACMAN = "pacman"
    FUZZY = "fuzzy"
    USER = "user"
    NONE = "none"


class DependencyMapping(BaseModel):
    """Result of mapping a single Debian dependency to Arch."""

    debian_name: str
    arch_name: Optional[str] = None
    status: DependencyStatus = DependencyStatus.UNMAPPED
    source: DependencySource = DependencySource.NONE


class ArchPackageInfo(BaseModel):
    """Metadata for generating .PKGINFO in Arch package."""

    pkgname: str
    pkgver: str
    pkgrel: int = 1
    pkgdesc: str = ""
    arch: str = "x86_64"
    url: Optional[str] = None
    license: list[str] = Field(default_factory=lambda: ["custom"])
    packager: str = "deb2arch"
    depends: list[str] = Field(default_factory=list)
    optdepends: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    provides: list[str] = Field(default_factory=list)
    replaces: list[str] = Field(default_factory=list)
    backup: list[str] = Field(default_factory=list)
    size: int = 0
    builddate: Optional[int] = None


class ConversionResult(BaseModel):
    """Result of a package conversion operation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    package_path: Optional[Path] = None
    pkgbuild_path: Optional[Path] = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    unmapped_deps: list[str] = Field(default_factory=list)
    mapped_deps: list[DependencyMapping] = Field(default_factory=list)
