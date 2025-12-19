"""Download utility using httpx."""

from pathlib import Path
from typing import Optional

import httpx
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from deb2arch.exceptions import DownloadError


def download_file(url: str, dest: Path) -> Path:
    """Download a file from URL to destination with progress bar.

    Args:
        url: URL to download.
        dest: Destination path (file).

    Returns:
        Path to the downloaded file.

    Raises:
        DownloadError: If download fails.
    """
    try:
        with httpx.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            with open(dest, "wb") as f:
                with Progress(
                    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    "•",
                    DownloadColumn(),
                    "•",
                    TransferSpeedColumn(),
                    "•",
                    TimeRemainingColumn(),
                ) as progress:
                    task = progress.add_task(
                        "download", filename=url.split("/")[-1], total=total
                    )
                    
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
                        
    except httpx.HTTPError as e:
        raise DownloadError(f"Failed to download {url}: {e}")
    except Exception as e:
        raise DownloadError(f"An unexpected error occurred: {e}")

    return dest
