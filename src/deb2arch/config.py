"""Configuration management for deb2arch."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class DepStrategy(str, Enum):
    """Strategy for handling unmappable dependencies."""

    INTERACTIVE = "interactive"
    CONFIG = "config"
    SKIP = "skip"
    RECURSIVE = "recursive"


def get_config_dir() -> Path:
    """Get the configuration directory following XDG spec."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "deb2arch"
    return Path.home() / ".config" / "deb2arch"


def get_cache_dir() -> Path:
    """Get the cache directory following XDG spec."""
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "deb2arch"
    return Path.home() / ".cache" / "deb2arch"


def get_config_path() -> Path:
    """Get the main config file path."""
    return get_config_dir() / "config.toml"


def get_mappings_path() -> Path:
    """Get the user mappings file path."""
    return get_config_dir() / "mappings.toml"


class Config(BaseModel):
    """Application configuration."""

    # Output settings
    output_dir: Path = Field(default_factory=Path.cwd)

    # Dependency handling
    dep_strategy: DepStrategy = DepStrategy.INTERACTIVE
    custom_mappings_file: Optional[Path] = None
    recursive: bool = False

    # Script handling
    include_scripts: Optional[bool] = None  # None = prompt user

    # UI settings
    quiet: bool = False
    verbose: bool = False

    # Installation
    auto_install: bool = False

    # Directories
    cache_dir: Path = Field(default_factory=get_cache_dir)
    config_dir: Path = Field(default_factory=get_config_dir)

    class Config:
        arbitrary_types_allowed = True


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file.

    Args:
        config_path: Path to config file, or None to use default location.

    Returns:
        Loaded configuration, or defaults if file doesn't exist.
    """
    if config_path is None:
        config_path = get_config_path()

    if not config_path.exists():
        return Config()

    try:
        import tomllib

        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        return Config(**data)
    except Exception:
        return Config()


def load_user_mappings(mappings_path: Optional[Path] = None) -> dict[str, str]:
    """Load user-defined package name mappings.

    Args:
        mappings_path: Path to mappings file, or None to use default location.

    Returns:
        Dictionary mapping Debian package names to Arch package names.
    """
    if mappings_path is None:
        mappings_path = get_mappings_path()

    if not mappings_path.exists():
        return {}

    try:
        import tomllib

        with open(mappings_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("mappings", {})
    except Exception:
        return {}
