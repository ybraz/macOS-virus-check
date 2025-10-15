#!/usr/bin/env python3
"""
Configuration Management Module
Handles storage and retrieval of API keys and settings
"""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Manages application configuration and API key storage"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager

        Args:
            config_dir: Custom config directory (default: ~/.config/vt-scanner)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".config" / "vt-scanner"

        self.config_file = self.config_dir / "config.json"
        self.cache_dir = self.config_dir / "cache"

        # Create directories if they don't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_api_key(self) -> Optional[str]:
        """
        Get VirusTotal API key from various sources

        Priority:
        1. Environment variable VT_API_KEY
        2. Config file
        3. Return None

        Returns:
            API key if found, None otherwise
        """
        # Check environment variable first
        env_key = os.getenv("VT_API_KEY")
        if env_key:
            return env_key

        # Check config file
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    return config_data.get("api_key")
            except (json.JSONDecodeError, KeyError, IOError):
                pass

        return None

    def set_api_key(self, api_key: str) -> None:
        """
        Save API key to config file

        Args:
            api_key: VirusTotal API key
        """
        config_data = {}

        # Load existing config if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
            except json.JSONDecodeError:
                pass

        # Update API key
        config_data["api_key"] = api_key

        # Save to file with restricted permissions
        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=2)

        # Set file permissions to 600 (owner read/write only)
        self.config_file.chmod(0o600)

    def get_setting(self, key: str, default=None):
        """
        Get a configuration setting

        Args:
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        if not self.config_file.exists():
            return default

        try:
            with open(self.config_file, "r") as f:
                config_data = json.load(f)
                return config_data.get(key, default)
        except (json.JSONDecodeError, IOError):
            return default

    def set_setting(self, key: str, value) -> None:
        """
        Set a configuration setting

        Args:
            key: Setting key
            value: Setting value
        """
        config_data = {}

        # Load existing config if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
            except json.JSONDecodeError:
                pass

        # Update setting
        config_data[key] = value

        # Save to file
        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=2)

        # Ensure proper permissions
        self.config_file.chmod(0o600)

    def is_configured(self) -> bool:
        """
        Check if API key is configured

        Returns:
            True if API key is available, False otherwise
        """
        return self.get_api_key() is not None

    def get_cache_path(self, file_hash: str) -> Path:
        """
        Get cache file path for a given file hash

        Args:
            file_hash: SHA256 hash of file

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{file_hash}.json"

    def get_cached_result(self, file_hash: str, max_age_days: int = 7) -> Optional[dict]:
        """
        Get cached scan result if available and not too old

        Args:
            file_hash: SHA256 hash of file
            max_age_days: Maximum age of cache in days

        Returns:
            Cached result if available and fresh, None otherwise
        """
        cache_file = self.get_cache_path(file_hash)

        if not cache_file.exists():
            return None

        # Check cache age
        import time
        cache_age_seconds = time.time() - cache_file.stat().st_mtime
        max_age_seconds = max_age_days * 24 * 60 * 60

        if cache_age_seconds > max_age_seconds:
            # Cache too old, delete it
            cache_file.unlink()
            return None

        # Load and return cached data
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def cache_result(self, file_hash: str, result: dict) -> None:
        """
        Cache a scan result

        Args:
            file_hash: SHA256 hash of file
            result: Scan result to cache
        """
        cache_file = self.get_cache_path(file_hash)

        try:
            with open(cache_file, "w") as f:
                json.dump(result, f, indent=2)
        except IOError:
            # Silently fail if cache write fails
            pass

    def clear_cache(self) -> int:
        """
        Clear all cached results

        Returns:
            Number of cache files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except IOError:
                pass

        return count
