# deb2arch

**deb2arch** is a Python CLI tool that converts Debian packages (`.deb`) to Arch Linux packages (`.pkg.tar.zst`). It automates extracting the Debian archive, resolving dependencies (mapping Debian names to Arch names), and repacking for pacman.

## Features

- **Automated Conversion**: Extracts `.deb` content and creates a valid Arch Linux package.
- **Dependency Mapping**:
  - Built-in mappings for common packages (e.g., `libc6` → `glibc`).
  - Fuzzy matching for versioned packages (e.g., `libssl1.1` → `openssl`).
  - Virtual package handling.
  - User-configurable mappings via `mappings.toml`.
- **Directory Compliance**: automatically moves `/bin`, `/sbin`, and `/lib` to `/usr/*` to comply with Arch Linux standards.
- **Source Handling**: Supports local `.deb` files and URLs.
- **Rich CLI**: Progress bars and colorized output.

## Prerequisites

- Python 3.10+
- `libarchive` (bsdtar)
- `fakeroot`

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/deb2arch.git
cd deb2arch

# Install dependencies
pip install .
```

## Usage

### Convert a Package

```bash
deb2arch convert /path/to/package.deb -o output_directory
```

Or from a URL:

```bash
deb2arch convert http://example.com/package.deb
```

### Options

- `-o, --output <DIR>`: Output directory (default: current directory).
- `--install`: Install the package after conversion (requires sudo).
- `-q, --quiet`: Suppress output.

## Development

1. **Setup**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

2. **Run Tests**:
   ```bash
   pytest
   ```

## License

MIT
