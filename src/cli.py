#!/usr/bin/env python3
"""
Command Line Interface for VirusTotal Scanner
Provides rich, interactive CLI for scanning files
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import box

from vt_scanner import VirusTotalScanner
from config import Config
from utils import (
    format_file_size,
    format_timestamp,
    send_notification_pync,
    validate_file_path,
    get_threat_emoji,
    get_threat_color,
    expand_paths,
    format_detection_summary,
    open_url
)

console = Console()


def get_scanner() -> VirusTotalScanner:
    """
    Get configured VirusTotal scanner instance

    Returns:
        VirusTotalScanner instance

    Raises:
        click.ClickException: If API key is not configured
    """
    config = Config()
    api_key = config.get_api_key()

    if not api_key:
        console.print("\n[red]❌ VirusTotal API key not configured![/red]")
        console.print("\nTo configure, run one of the following:")
        console.print("  1. [cyan]vt-check config --api-key YOUR_KEY[/cyan]")
        console.print("  2. [cyan]export VT_API_KEY=YOUR_KEY[/cyan]")
        console.print("\nGet your API key at: [blue]https://www.virustotal.com/gui/my-apikey[/blue]\n")
        raise click.ClickException("API key not configured")

    return VirusTotalScanner(api_key)


def display_scan_result(file_path: Path, result: dict, uploaded: bool = False):
    """
    Display scan result in a formatted panel

    Args:
        file_path: Path to scanned file
        result: Parsed scan result
        uploaded: Whether file was uploaded (vs cached check)
    """
    threat_level = result["threat_level"]
    emoji = get_threat_emoji(threat_level)
    color = get_threat_color(threat_level)

    # Create result table
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("File", str(file_path.name))
    table.add_row("Size", format_file_size(result["file_info"]["file_size"]))
    table.add_row("Type", result["file_info"]["file_type"])
    table.add_row("SHA-256", result["file_info"]["sha256"][:32] + "...")

    detection_str = format_detection_summary(result["detections"], result["total_scans"])
    table.add_row("Result", f"[{color}]{emoji} {threat_level}[/{color}]")
    table.add_row("Detections", f"[{color}]{detection_str}[/{color}]")

    if result["suspicious"] > 0:
        table.add_row("Suspicious", f"[yellow]{result['suspicious']}[/yellow]")

    table.add_row("Last Analyzed", format_timestamp(result["last_analysis_date"]))
    table.add_row("Report", f"[blue]{result['permalink']}[/blue]")

    if uploaded:
        table.add_row("Status", "[yellow]Newly uploaded and analyzed[/yellow]")
    else:
        table.add_row("Status", "[green]Retrieved from VT database[/green]")

    # Create panel with result
    title = f"{emoji} Scan Result"
    panel = Panel(table, title=title, border_style=color)

    console.print(panel)


@click.group()
@click.version_option(version="1.0.0", prog_name="vt-check")
def cli():
    """
    VirusTotal Scanner for macOS

    Scan files for malware using VirusTotal API
    """
    pass


@cli.command()
@click.argument("files", nargs=-1, required=True, type=click.Path())
@click.option("--recursive", "-r", is_flag=True, help="Recursively scan directories")
@click.option("--force-upload", "-f", is_flag=True, help="Force upload even if hash exists")
@click.option("--notify", "-n", is_flag=True, help="Send macOS notification with results")
@click.option("--open-report", "-o", is_flag=True, help="Open detailed report in browser")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
@click.option("--cache/--no-cache", default=True, help="Use cached results (default: enabled)")
def scan(files, recursive, force_upload, notify, open_report, output_json, cache):
    """
    Scan one or more files for malware

    Examples:
      vt-check scan file.exe
      vt-check scan *.dmg
      vt-check scan -r ~/Downloads
      vt-check scan --notify suspicious.pdf
    """
    try:
        scanner = get_scanner()
        config = Config()

        # Expand file paths
        file_paths = expand_paths(list(files), recursive=recursive)

        if not file_paths:
            console.print("[yellow]⚠️  No files found to scan[/yellow]")
            return

        console.print(f"\n[cyan]🔍 Scanning {len(file_paths)} file(s)...[/cyan]\n")

        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            for file_path in file_paths:
                task = progress.add_task(f"Scanning {file_path.name}...", total=None)

                try:
                    # Calculate hash for cache check
                    file_hash = scanner.calculate_file_hash(file_path)

                    # Check cache first if enabled
                    if cache and not force_upload:
                        cached = config.get_cached_result(file_hash)
                        if cached:
                            parsed = scanner.parse_results(cached)
                            results.append((file_path, parsed, False))
                            progress.update(task, completed=True)
                            continue

                    # Scan file
                    analysis_data, uploaded = scanner.scan_file(file_path, force_upload=force_upload)
                    parsed = scanner.parse_results(analysis_data)

                    # Cache result
                    if cache:
                        config.cache_result(file_hash, analysis_data)

                    results.append((file_path, parsed, uploaded))

                except Exception as e:
                    console.print(f"[red]❌ Error scanning {file_path.name}: {e}[/red]")
                    continue
                finally:
                    progress.update(task, completed=True)

        # Display results
        console.print()
        for file_path, result, uploaded in results:
            if output_json:
                import json
                console.print(json.dumps(result, indent=2))
            else:
                display_scan_result(file_path, result, uploaded)
                console.print()

            # Send notification if requested
            if notify:
                emoji = get_threat_emoji(result["threat_level"])
                title = f"{emoji} VirusTotal Scan Complete"
                message = f"{file_path.name}: {result['threat_level']}"
                send_notification_pync(title, message, result["permalink"])

            # Open report in browser if requested
            if open_report:
                open_url(result["permalink"])

        # Summary
        if len(results) > 1:
            malicious_count = sum(1 for _, r, _ in results if r["threat_level"] == "MALICIOUS")
            suspicious_count = sum(1 for _, r, _ in results if r["threat_level"] == "SUSPICIOUS")
            clean_count = sum(1 for _, r, _ in results if r["threat_level"] == "CLEAN")

            console.print(Panel(
                f"[green]✅ Clean: {clean_count}[/green]  "
                f"[yellow]⚠️  Suspicious: {suspicious_count}[/yellow]  "
                f"[red]🚨 Malicious: {malicious_count}[/red]",
                title="Summary",
                border_style="blue"
            ))

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("hash_value")
@click.option("--open-report", "-o", is_flag=True, help="Open detailed report in browser")
def hash(hash_value, open_report):
    """
    Check a file hash (SHA-256) without uploading

    Example:
      vt-check hash a3f2b1c4d5e6f7890abcdef123456789...
    """
    try:
        scanner = get_scanner()

        console.print(f"\n[cyan]🔍 Checking hash: {hash_value}[/cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Querying VirusTotal...", total=None)

            analysis_data = scanner.check_hash(hash_value)
            progress.update(task, completed=True)

        if not analysis_data:
            console.print("[yellow]⚠️  Hash not found in VirusTotal database[/yellow]")
            console.print("The file may not have been scanned yet.\n")
            return

        parsed = scanner.parse_results(analysis_data)

        # Display result
        console.print()
        display_scan_result(Path(f"Hash: {hash_value[:16]}..."), parsed, False)

        if open_report:
            open_url(parsed["permalink"])

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--api-key", help="Set VirusTotal API key")
@click.option("--show", is_flag=True, help="Show current configuration")
@click.option("--clear-cache", is_flag=True, help="Clear cached scan results")
def config(api_key, show, clear_cache):
    """
    Manage configuration and settings

    Examples:
      vt-check config --api-key YOUR_KEY
      vt-check config --show
      vt-check config --clear-cache
    """
    cfg = Config()

    if api_key:
        cfg.set_api_key(api_key)
        console.print("[green]✅ API key saved successfully[/green]")
        console.print(f"Config file: [cyan]{cfg.config_file}[/cyan]\n")

    if show:
        current_key = cfg.get_api_key()

        table = Table(title="Current Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value")

        if current_key:
            masked_key = current_key[:8] + "..." + current_key[-8:]
            table.add_row("API Key", f"[green]{masked_key}[/green]")
            table.add_row("Source", "Environment" if "VT_API_KEY" in __import__("os").environ else "Config file")
        else:
            table.add_row("API Key", "[red]Not configured[/red]")

        table.add_row("Config Dir", str(cfg.config_dir))
        table.add_row("Cache Dir", str(cfg.cache_dir))

        # Count cache files
        cache_count = len(list(cfg.cache_dir.glob("*.json")))
        table.add_row("Cached Results", str(cache_count))

        console.print()
        console.print(table)
        console.print()

    if clear_cache:
        count = cfg.clear_cache()
        console.print(f"[green]✅ Cleared {count} cached result(s)[/green]\n")


if __name__ == "__main__":
    cli()
