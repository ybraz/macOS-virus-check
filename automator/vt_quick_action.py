#!/usr/bin/env python3
"""
VirusTotal Quick Action Script
Called by Automator workflow for Finder context menu integration
"""

import sys
import subprocess
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vt_scanner import VirusTotalScanner
from config import Config
from utils import (
    send_notification_pync,
    get_threat_emoji,
    format_detection_summary
)


def send_notification(title: str, message: str, url: str = None):
    """Send macOS notification with fallback"""
    try:
        send_notification_pync(title, message, url)
    except Exception:
        # Fallback to osascript
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], timeout=5)
        except Exception:
            pass


def scan_file(file_path: str):
    """
    Scan a file and show notification with results

    Args:
        file_path: Path to file to scan
    """
    try:
        # Initialize
        config = Config()
        api_key = config.get_api_key()

        if not api_key:
            send_notification(
                "❌ VirusTotal Scanner",
                "API key not configured. Run: vt-check config --api-key YOUR_KEY"
            )
            return 1

        scanner = VirusTotalScanner(api_key)
        file_path = Path(file_path)

        # Show scanning notification
        send_notification(
            "🔍 VirusTotal Scanner",
            f"Scanning {file_path.name}..."
        )

        # Calculate hash and check cache
        file_hash = scanner.calculate_file_hash(file_path)
        cached = config.get_cached_result(file_hash)

        if cached:
            analysis_data = cached
            uploaded = False
        else:
            # Scan file
            analysis_data, uploaded = scanner.scan_file(file_path)

            # Cache result
            config.cache_result(file_hash, analysis_data)

        # Parse results
        result = scanner.parse_results(analysis_data)

        # Prepare notification
        emoji = get_threat_emoji(result["threat_level"])
        threat_level = result["threat_level"]
        detection_str = format_detection_summary(result["detections"], result["total_scans"])

        title = f"{emoji} {file_path.name}"

        if threat_level == "MALICIOUS":
            message = f"⚠️ THREAT DETECTED: {detection_str}"
        elif threat_level == "SUSPICIOUS":
            message = f"⚠️ Suspicious: {detection_str}"
        else:
            message = f"✅ Clean: {detection_str}"

        # Add analysis info
        if uploaded:
            message += " (Newly analyzed)"
        else:
            message += " (From VT database)"

        # Send result notification
        send_notification(title, message, result["permalink"])

        return 0

    except FileNotFoundError:
        send_notification(
            "❌ VirusTotal Scanner",
            f"File not found: {file_path}"
        )
        return 1

    except Exception as e:
        send_notification(
            "❌ VirusTotal Scanner",
            f"Error: {str(e)}"
        )
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: vt_quick_action.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    sys.exit(scan_file(file_path))
