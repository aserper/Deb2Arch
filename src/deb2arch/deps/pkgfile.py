"""Integration with pkgfile for file-based dependency lookup."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from deb2arch.exceptions import DependencyError


class PkgFile:
    """Interface to pkgfile command."""
    
    def __init__(self):
        self.executable = shutil.which("pkgfile")
        
    @property
    def is_available(self) -> bool:
        """Check if pkgfile is installed."""
        return self.executable is not None
        
    def lookup_file(self, filename: str) -> Optional[str]:
        """Find the package that owns a file.
        
        Args:
            filename: Name of the file to look up (basename or partial path).
            
        Returns:
            Name of the package containing the file, or None if not found.
        """
        if not self.is_available:
            return None
            
        try:
            # -b: search for binaries in bin/sbin
            # -v: verbose output (we just want the first match usually)
            # using -b might be too restrictive, let's try generic search but prioritize bin
            
            # Start with binary search as it's most common for deps
            result = subprocess.run(
                [self.executable, "-b", filename],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # pkgfile output format is just "package" or "core/package"
                # we want the package name
                line = result.stdout.splitlines()[0]
                return line.split("/")[-1] if "/" in line else line
                
            # Fallback to generic search
            result = subprocess.run(
                [self.executable, filename],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0 and result.stdout.strip():
                line = result.stdout.splitlines()[0]
                return line.split("/")[-1] if "/" in line else line
                
        except (subprocess.SubprocessError, OSError):
            pass
            
        return None
        
    def update(self) -> None:
        """Update the pkgfile database."""
        if not self.is_available:
            raise DependencyError("pkgfile is not installed")
            
        try:
            # often requires sudo, we'll try without and see
            subprocess.run([self.executable, "-u"], check=True)
        except subprocess.CalledProcessError as e:
            raise DependencyError(f"Failed to update pkgfile: {e}")
