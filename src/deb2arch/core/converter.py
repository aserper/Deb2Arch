"""Main converter orchestrator."""

import time
from pathlib import Path
from typing import Optional, List

from deb2arch.core.extractor import DebExtractor
from deb2arch.core.builder import ArchBuilder
from deb2arch.deps.mapper import DependencyMapper
from deb2arch.sources.local import LocalSource
from deb2arch.sources.url import UrlSource
from deb2arch.sources.base import PackageSource
from deb2arch.models import (
    ArchPackageInfo,
    Architecture,
    ConversionResult,
    DependencyStatus,
    DependencyMapping,
)


class Converter:
    """Orchestrates the conversion from .deb to .pkg.tar.zst."""

    def __init__(
        self,
        output_dir: Path,
        install: bool = False,
        quiet: bool = False,
        user_mappings: Optional[dict[str, str]] = None,
    ):
        """Initialize converter.

        Args:
            output_dir: Output directory for Arch packages.
            install: Whether to install the specified package.
            quiet: Suppress user interaction/output.
            user_mappings: Custom dependency mappings.
        """
        self.output_dir = output_dir
        self.install = install
        self.quiet = quiet
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.mapper = DependencyMapper(user_mappings=user_mappings)
        self.builder = ArchBuilder()

    def convert(self, target: str) -> ConversionResult:
        """Convert a Debian package to Arch.

        Args:
            target: Path, URL, or package identifier.

        Returns:
            ConversionResult object.
        """
        result = ConversionResult(success=False)
        source: Optional[PackageSource] = None
        
        try:
            # 1. Determine Source
            source = self._get_source(target)
            deb_path = source.get_package(target)
            
            # 2. Extract
            with DebExtractor() as extractor:
                deb_pkg = extractor.extract(deb_path)
                
                # 3. Map Dependencies
                mapped_deps = []
                unmapped_deps = []
                arch_depends = []
                
                for dep in deb_pkg.control.depends:
                    # Dep might be "pkg (>= 1.0)"
                    # We pass the full string to mapper?
                    # Mapper expects package name.
                    # We should parse dependency list properly first
                    # But deb_pkg.control.depends is list[str] like ["libc6 (>= 2.14)", "python3"]
                    
                    mapping = self.mapper.map_dependency(dep)
                    mapped_deps.append(mapping)
                    
                    if mapping.status == DependencyStatus.MAPPED or mapping.status == DependencyStatus.VIRTUAL:
                        if mapping.arch_name:
                            arch_depends.append(mapping.arch_name)
                    elif mapping.status == DependencyStatus.UNMAPPED:
                        unmapped_deps.append(dep)
                        
                result.mapped_deps = mapped_deps
                result.unmapped_deps = unmapped_deps
                
                if unmapped_deps:
                    if not self.quiet:
                        # TODO: Interactive prompts logic here
                        pass
                    result.warnings.append(f"Unmapped dependencies: {unmapped_deps}")
                
                # 4. Prepare Arch Metadata
                arch_pkg = ArchPackageInfo(
                    pkgname=deb_pkg.control.package,
                    pkgver=deb_pkg.control.version.replace("-", "_"), # sanitize version
                    pkgdesc=deb_pkg.control.description.splitlines()[0] if deb_pkg.control.description else "",
                    arch=deb_pkg.control.architecture.to_arch(),
                    url=deb_pkg.control.homepage,
                    packager="deb2arch",
                    size=deb_pkg.control.installed_size or 0,
                    depends=list(set(arch_depends)),
                    # TODO: handling conflicts, provides etc.
                )
                
                # 5. Build Package
                pkg_path = self.builder.build_package(
                    arch_pkg,
                    deb_pkg.data_dir,
                    self.output_dir,
                    install_script=None # TODO: Handle script conversion status
                )
                
                result.success = True
                result.package_path = pkg_path
                
                # 6. Install (Optional)
                if self.install and pkg_path:
                    # TODO: Implement install logic (pacman -U)
                    pass
                    
        except Exception as e:
            result.errors.append(str(e))
        finally:
            if source:
                source.cleanup()
                
        return result

    def _get_source(self, target: str) -> PackageSource:
        """Determine source handler from target string."""
        if target.startswith("http://") or target.startswith("https://"):
            return UrlSource()
        return LocalSource()
