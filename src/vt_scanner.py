#!/usr/bin/env python3
"""
VirusTotal Scanner Core Module
Handles all interactions with the VirusTotal API v3
"""

import requests
import time
import hashlib
from typing import Dict, Optional, Tuple
from pathlib import Path


class VirusTotalScanner:
    """VirusTotal API client for file scanning and analysis"""

    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self, api_key: str):
        """
        Initialize VirusTotal scanner

        Args:
            api_key: VirusTotal API key
        """
        self.api_key = api_key
        self.headers = {
            "x-apikey": api_key,
            "Accept": "application/json"
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file

        Args:
            file_path: Path to the file

        Returns:
            SHA256 hash as hexadecimal string
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def check_hash(self, file_hash: str) -> Optional[Dict]:
        """
        Check if a file hash exists in VirusTotal database

        Args:
            file_hash: SHA256 hash of the file

        Returns:
            Analysis data if exists, None if not found
        """
        url = f"{self.BASE_URL}/files/{file_hash}"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error checking hash: {e}")

    def upload_file(self, file_path: Path) -> str:
        """
        Upload a file to VirusTotal for analysis

        Args:
            file_path: Path to the file to upload

        Returns:
            Analysis ID
        """
        url = f"{self.BASE_URL}/files"

        # Check file size (max 32MB for free API, 650MB for premium)
        file_size = file_path.stat().st_size
        max_size = 32 * 1024 * 1024  # 32MB

        if file_size > max_size:
            # For large files, get upload URL
            url = self._get_upload_url()

        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f)}
                response = requests.post(
                    url,
                    headers={"x-apikey": self.api_key},
                    files=files
                )

            response.raise_for_status()
            data = response.json()

            # Extract analysis ID from response
            return data["data"]["id"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error uploading file: {e}")

    def _get_upload_url(self) -> str:
        """Get upload URL for large files"""
        url = f"{self.BASE_URL}/files/upload_url"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error getting upload URL: {e}")

    def get_analysis(self, analysis_id: str, wait: bool = True, max_wait: int = 300) -> Dict:
        """
        Get analysis results

        Args:
            analysis_id: Analysis ID from upload
            wait: Whether to wait for analysis to complete
            max_wait: Maximum time to wait in seconds

        Returns:
            Analysis results
        """
        url = f"{self.BASE_URL}/analyses/{analysis_id}"

        start_time = time.time()

        while True:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                status = data["data"]["attributes"]["status"]

                if status == "completed":
                    return data

                if not wait:
                    return data

                # Check if we've exceeded max wait time
                if time.time() - start_time > max_wait:
                    raise Exception("Analysis timeout - file is still being processed")

                # Wait before polling again (respect rate limits)
                time.sleep(5)

            except requests.exceptions.RequestException as e:
                raise Exception(f"Error getting analysis: {e}")

    def scan_file(self, file_path: Path, force_upload: bool = False) -> Tuple[Dict, bool]:
        """
        Scan a file using VirusTotal

        Args:
            file_path: Path to the file
            force_upload: Force upload even if hash exists

        Returns:
            Tuple of (analysis_data, was_uploaded)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Calculate file hash
        file_hash = self.calculate_file_hash(file_path)

        # Check if file already exists in VT database
        if not force_upload:
            existing_data = self.check_hash(file_hash)
            if existing_data:
                return existing_data, False

        # Upload file for new analysis
        analysis_id = self.upload_file(file_path)

        # Wait for analysis to complete
        analysis_data = self.get_analysis(analysis_id, wait=True)

        return analysis_data, True

    def parse_results(self, analysis_data: Dict) -> Dict:
        """
        Parse and summarize analysis results

        Args:
            analysis_data: Raw analysis data from API

        Returns:
            Parsed summary with key information
        """
        try:
            attrs = analysis_data["data"]["attributes"]
            stats = attrs.get("stats", {})

            # Handle both file reports and analysis reports
            if "last_analysis_stats" in attrs:
                stats = attrs["last_analysis_stats"]

            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            undetected = stats.get("undetected", 0)
            harmless = stats.get("harmless", 0)

            total_scans = malicious + suspicious + undetected + harmless

            # Determine threat level
            if malicious > 0:
                threat_level = "MALICIOUS"
                color = "red"
            elif suspicious > 0:
                threat_level = "SUSPICIOUS"
                color = "yellow"
            else:
                threat_level = "CLEAN"
                color = "green"

            # Get file info
            file_info = {
                "sha256": attrs.get("sha256", "N/A"),
                "md5": attrs.get("md5", "N/A"),
                "sha1": attrs.get("sha1", "N/A"),
                "file_type": attrs.get("type_description", "Unknown"),
                "file_size": attrs.get("size", 0),
            }

            # Get last analysis date
            last_analysis = attrs.get("last_analysis_date")
            if not last_analysis:
                last_analysis = attrs.get("date")

            # Build permalink
            permalink = f"https://www.virustotal.com/gui/file/{file_info['sha256']}"

            return {
                "threat_level": threat_level,
                "color": color,
                "detections": malicious,
                "suspicious": suspicious,
                "total_scans": total_scans,
                "file_info": file_info,
                "last_analysis_date": last_analysis,
                "permalink": permalink,
                "raw_stats": stats
            }

        except (KeyError, TypeError) as e:
            raise Exception(f"Error parsing results: {e}")
