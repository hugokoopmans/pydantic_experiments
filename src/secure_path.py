"""Validate paths are within working directory."""
import os
from pathlib import Path


def is_path_safe(path: str) -> bool:
    """Check if path is under working directory."""
    try:
        requested = Path(path).resolve()
        cwd = Path.cwd().resolve()
        return requested.is_relative_to(cwd)
    except (ValueError, OSError):
        return False


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    return Path(path).stat().st_size


def validate_size(size_bytes: int, max_mb: int = 10) -> bool:
    """Check if size is within limit."""
    return size_bytes <= max_mb * 1024 * 1024