#!/usr/bin/env python3
"""
Utility Functions Module
Helper functions for formatting, file operations, and notifications
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_timestamp(timestamp: Optional[int]) -> str:
    """
    Format Unix timestamp to human-readable date

    Args:
        timestamp: Unix timestamp

    Returns:
        Formatted date string
    """
    if not timestamp:
        return "Unknown"

    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "Invalid date"


def send_notification(title: str, message: str, sound: bool = False) -> None:
    """
    Send macOS notification using osascript

    Args:
        title: Notification title
        message: Notification message
        sound: Whether to play sound
    """
    try:
        # Build osascript command
        script = f'display notification "{message}" with title "{title}"'

        if sound:
            script += ' sound name "default"'

        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Silently fail if notification fails
        pass


def send_notification_pync(title: str, message: str, open_url: Optional[str] = None) -> None:
    """
    Send macOS notification using pync (better for clickable notifications)

    Args:
        title: Notification title
        message: Notification message
        open_url: URL to open when notification is clicked
    """
    try:
        import pync

        kwargs = {
            "title": title,
            "message": message,
        }

        if open_url:
            kwargs["open"] = open_url

        pync.notify(**kwargs)
    except ImportError:
        # Fall back to osascript if pync not available
        send_notification(title, message)
    except Exception:
        # Silently fail if notification fails
        pass


def validate_file_path(file_path: str) -> Path:
    """
    Validate and resolve file path

    Args:
        file_path: File path string

    Returns:
        Resolved Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not a file
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    return path


def get_file_type(file_path: Path) -> str:
    """
    Get file type using macOS file command

    Args:
        file_path: Path to file

    Returns:
        File type description
    """
    try:
        result = subprocess.run(
            ["file", "-b", str(file_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return "Unknown"


def get_threat_emoji(threat_level: str) -> str:
    """
    Get emoji for threat level

    Args:
        threat_level: Threat level (CLEAN, SUSPICIOUS, MALICIOUS)

    Returns:
        Appropriate emoji
    """
    emoji_map = {
        "CLEAN": "✅",
        "SUSPICIOUS": "⚠️",
        "MALICIOUS": "🚨",
        "UNKNOWN": "❓"
    }

    return emoji_map.get(threat_level, "❓")


def get_threat_color(threat_level: str) -> str:
    """
    Get color for threat level (rich console colors)

    Args:
        threat_level: Threat level (CLEAN, SUSPICIOUS, MALICIOUS)

    Returns:
        Color name for rich console
    """
    color_map = {
        "CLEAN": "green",
        "SUSPICIOUS": "yellow",
        "MALICIOUS": "red",
        "UNKNOWN": "blue"
    }

    return color_map.get(threat_level, "white")


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def expand_paths(paths: list[str], recursive: bool = False) -> list[Path]:
    """
    Expand file paths, handling globs and directories

    Args:
        paths: List of file paths (can include globs)
        recursive: If True, recursively scan directories

    Returns:
        List of resolved file paths
    """
    expanded = []

    for path_str in paths:
        path = Path(path_str).expanduser()

        # Handle glob patterns
        if "*" in path_str or "?" in path_str:
            expanded.extend(Path(".").glob(path_str))
        elif path.is_dir():
            if recursive:
                expanded.extend(path.rglob("*"))
            else:
                expanded.extend(path.glob("*"))
        elif path.exists():
            expanded.append(path)

    # Filter to only files (not directories)
    return [p for p in expanded if p.is_file()]


def open_url(url: str) -> bool:
    """
    Open URL in default browser

    Args:
        url: URL to open

    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.run(
            ["open", url],
            capture_output=True,
            timeout=5
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def format_detection_summary(detections: int, total: int) -> str:
    """
    Format detection summary string

    Args:
        detections: Number of positive detections
        total: Total number of scans

    Returns:
        Formatted string (e.g., "3/70 detections")
    """
    if detections == 0:
        return f"0/{total} detections"

    return f"{detections}/{total} detections"
