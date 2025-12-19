"""Custom exceptions for deb2arch."""


class Deb2ArchError(Exception):
    """Base exception for all deb2arch errors."""

    pass


class ExtractionError(Deb2ArchError):
    """Error extracting .deb file."""

    pass


class ParseError(Deb2ArchError):
    """Error parsing control file or package metadata."""

    pass


class DependencyError(Deb2ArchError):
    """Error resolving or mapping dependencies."""

    pass


class BuildError(Deb2ArchError):
    """Error building the Arch package."""

    pass


class DownloadError(Deb2ArchError):
    """Error downloading package from URL or repository."""

    pass


class ConfigError(Deb2ArchError):
    """Error in configuration file or settings."""

    pass


class SourceError(Deb2ArchError):
    """Error with package source (file not found, invalid format, etc.)."""

    pass
