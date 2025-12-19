# deb2arch

Convert Debian packages (.deb) to Arch Linux packages (.pkg.tar.zst).

## Installation

```bash
pip install deb2arch
```

## Usage

```bash
# Convert a local .deb file
deb2arch convert ./package.deb

# Convert from URL
deb2arch convert https://example.com/package.deb

# Convert from Debian repos
deb2arch convert apt:package-name

# Convert and install
deb2arch convert ./package.deb --install
```

## Requirements

- Python 3.10+
- `fakeroot` and `bsdtar` (for package building)
- `pkgfile` (optional, for enhanced dependency resolution)

## License

MIT
