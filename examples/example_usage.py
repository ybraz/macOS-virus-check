#!/usr/bin/env python3
"""
Example Usage of VirusTotal Scanner API
Demonstrates how to use the scanner programmatically
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vt_scanner import VirusTotalScanner
from config import Config
from utils import format_file_size, get_threat_emoji


def example_basic_scan():
    """Example: Basic file scan"""
    print("=" * 60)
    print("Example 1: Basic File Scan")
    print("=" * 60)

    # Initialize configuration
    config = Config()
    api_key = config.get_api_key()

    if not api_key:
        print("❌ API key not configured!")
        print("Run: vt-check config --api-key YOUR_KEY")
        return

    # Create scanner instance
    scanner = VirusTotalScanner(api_key)

    # Scan a file (replace with actual file path)
    file_path = Path("/path/to/test/file.txt")

    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        print("Update the file_path in this example to a real file")
        return

    try:
        print(f"\n🔍 Scanning: {file_path.name}")

        # Scan the file
        analysis_data, uploaded = scanner.scan_file(file_path)

        # Parse results
        result = scanner.parse_results(analysis_data)

        # Display results
        emoji = get_threat_emoji(result["threat_level"])
        print(f"\n{emoji} Result: {result['threat_level']}")
        print(f"Detections: {result['detections']}/{result['total_scans']}")
        print(f"File Size: {format_file_size(result['file_info']['file_size'])}")
        print(f"SHA-256: {result['file_info']['sha256'][:32]}...")
        print(f"Report: {result['permalink']}")
        print(f"Status: {'Uploaded' if uploaded else 'From database'}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_hash_check():
    """Example: Check hash without uploading"""
    print("\n" + "=" * 60)
    print("Example 2: Hash Check (No Upload)")
    print("=" * 60)

    config = Config()
    api_key = config.get_api_key()

    if not api_key:
        print("❌ API key not configured!")
        return

    scanner = VirusTotalScanner(api_key)

    # Example SHA-256 hash (replace with actual hash)
    file_hash = "a" * 64  # Fake hash for demonstration

    try:
        print(f"\n🔍 Checking hash: {file_hash[:32]}...")

        # Check hash
        analysis_data = scanner.check_hash(file_hash)

        if analysis_data:
            result = scanner.parse_results(analysis_data)
            emoji = get_threat_emoji(result["threat_level"])
            print(f"\n{emoji} Result: {result['threat_level']}")
            print(f"Detections: {result['detections']}/{result['total_scans']}")
        else:
            print("\n⚠️  Hash not found in VirusTotal database")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_batch_scan():
    """Example: Scan multiple files"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Scanning")
    print("=" * 60)

    config = Config()
    api_key = config.get_api_key()

    if not api_key:
        print("❌ API key not configured!")
        return

    scanner = VirusTotalScanner(api_key)

    # Example file list (replace with actual files)
    files = [
        Path("/path/to/file1.txt"),
        Path("/path/to/file2.pdf"),
        Path("/path/to/file3.dmg"),
    ]

    # Filter to existing files
    files = [f for f in files if f.exists()]

    if not files:
        print("⚠️  No files found to scan")
        print("Update the file paths in this example")
        return

    print(f"\n🔍 Scanning {len(files)} files...\n")

    results = []

    for file_path in files:
        try:
            print(f"Scanning: {file_path.name}...", end=" ")

            # Calculate hash and check cache
            file_hash = scanner.calculate_file_hash(file_path)
            cached = config.get_cached_result(file_hash)

            if cached:
                analysis_data = cached
                uploaded = False
            else:
                analysis_data, uploaded = scanner.scan_file(file_path)
                config.cache_result(file_hash, analysis_data)

            result = scanner.parse_results(analysis_data)
            results.append((file_path.name, result))

            emoji = get_threat_emoji(result["threat_level"])
            print(f"{emoji} {result['threat_level']}")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    for filename, result in results:
        emoji = get_threat_emoji(result["threat_level"])
        detections = f"{result['detections']}/{result['total_scans']}"
        print(f"{emoji} {filename}: {result['threat_level']} ({detections})")


def example_cache_usage():
    """Example: Using cache effectively"""
    print("\n" + "=" * 60)
    print("Example 4: Cache Management")
    print("=" * 60)

    config = Config()

    # Count cached results
    cache_count = len(list(config.cache_dir.glob("*.json")))
    print(f"\n📦 Current cache: {cache_count} results")

    # Get a cached result
    test_hash = "a" * 64
    cached = config.get_cached_result(test_hash)

    if cached:
        print(f"✅ Found cached result for {test_hash[:16]}...")
    else:
        print(f"⚠️  No cached result for {test_hash[:16]}...")

    # Clear cache
    print("\n🗑️  To clear cache:")
    print("  config.clear_cache()")
    print("  Or use: vt-check config --clear-cache")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("VirusTotal Scanner - Python API Examples")
    print("=" * 60)

    # Check if API key is configured
    config = Config()
    if not config.is_configured():
        print("\n❌ API key not configured!")
        print("\nConfigure with:")
        print("  vt-check config --api-key YOUR_KEY")
        print("\nOr set environment variable:")
        print("  export VT_API_KEY='your-key-here'")
        return

    print("\n✅ API key configured")
    print("\nRunning examples...\n")

    # Run examples
    example_basic_scan()
    example_hash_check()
    example_batch_scan()
    example_cache_usage()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nModify this file to test with your own files.")
    print("")


if __name__ == "__main__":
    main()
