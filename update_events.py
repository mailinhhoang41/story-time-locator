"""
Weekly Event Data Refresh Script

This script runs all parsers to update event data from Jersey City libraries.
Run this script once per week to keep your event data current.

Usage:
    python update_events.py
"""

import subprocess
import sys
from datetime import datetime
import os

def run_parser(parser_name):
    """Run a parser script and return success status"""
    print(f"\n{'='*80}")
    print(f"Running {parser_name}...")
    print('='*80)

    try:
        result = subprocess.run(
            [sys.executable, parser_name],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"[OK] {parser_name} completed successfully")
            # Print last few lines of output
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:
                print(f"   {line}")
            return True
        else:
            print(f"[ERROR] {parser_name} failed with error:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print(f"[ERROR] {parser_name} timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] {parser_name} encountered an error: {e}")
        return False

def main():
    print("="*80)
    print("STORY TIME LOCATOR - WEEKLY EVENT DATA REFRESH")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Check if we're in the right directory
    if not os.path.exists('jc_library_rss_parser.py'):
        print("[ERROR] jc_library_rss_parser.py not found!")
        print("   Make sure you're running this from the Story Time Locator directory")
        sys.exit(1)

    # List of parsers to run
    parsers = [
        'jc_library_rss_parser.py',     # Jersey City libraries
        'hoboken_library_rss_parser.py', # Hoboken Public Library
        # Add future parsers here:
        # 'bookstore_scraper.py',
    ]

    results = {}

    # Run each parser
    for parser in parsers:
        if os.path.exists(parser):
            results[parser] = run_parser(parser)
        else:
            print(f"[WARNING] Skipping {parser} (not found)")
            results[parser] = None

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    successful = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    print(f"[OK] Successful: {successful}")
    print(f"[ERROR] Failed: {failed}")
    print(f"[WARNING] Skipped: {skipped}")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Check for data files
    print("\nData Files:")
    data_files = ['jersey_city_storytimes.json', 'hoboken_storytimes.json']
    for file in data_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            modified = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"  [OK] {file} ({size:,} bytes, updated {modified.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"  [ERROR] {file} not found")

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Review jersey_city_storytimes.json and hoboken_storytimes.json")
    print("2. Run this script again next week to refresh events")
    print("3. Consider scheduling this with Windows Task Scheduler")
    print("="*80)

    # Exit with error code if any parser failed
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
