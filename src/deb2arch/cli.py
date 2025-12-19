"""CLI interface for deb2arch."""

import click
from pathlib import Path
from rich.console import Console

from deb2arch.core.converter import Converter

console = Console()


@click.group()
@click.version_option()
def main():
    """Convert Debian packages to Arch Linux packages."""
    pass


@main.command()
@click.argument("target")
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Output directory for converted packages.",
)
@click.option(
    "--install",
    is_flag=True,
    help="Install the package after conversion (requires sudo).",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress output.")
def convert(target: str, output: Path, install: bool, quiet: bool):
    """Convert a Debian package to Arch.

    TARGET can be a local file path or a URL.
    """
    if not quiet:
        console.print(f"[bold green]Converting[/] {target}...")

    converter = Converter(output_dir=output, install=install, quiet=quiet)
    result = converter.convert(target)

    if result.success:
        if not quiet:
            console.print(f"[bold green]Success![/] Package created at: {result.package_path}")
            if result.warnings:
                console.print("[yellow]Warnings:[/]")
                for warning in result.warnings:
                    console.print(f"  - {warning}")
            if result.unmapped_deps:
                console.print("[yellow]Unmapped dependencies:[/]")
                for dep in result.unmapped_deps:
                    console.print(f"  - {dep}")
    else:
        if not quiet:
            console.print("[bold red]Conversion Failed![/]")
            for error in result.errors:
                console.print(f"  - {error}")
        ctx = click.get_current_context()
        ctx.exit(1)


@main.command()
def update():
    """Update pkgfile database."""
    # TODO: Implement pkgfile update wrapper
    console.print("[yellow]Not implemented yet[/]")


if __name__ == "__main__":
    main()
