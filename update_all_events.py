"""
Update All Events Script
Runs all parsers/scrapers and refreshes the Flask server automatically

Run this script weekly (or whenever you want fresh data) to:
1. Fetch latest events from Jersey City Library
2. Fetch latest events from Hoboken Library
3. Fetch latest events from bookstores
4. Auto-refresh the Flask server (if it's running)
"""

import subprocess
import requests
import sys

def run_parser(script_name, description):
    """Run a parser script and report status"""
    print(f"\n{'='*80}")
    print(f"Running {description}...")
    print(f"{'='*80}\n")

    try:
        result = subprocess.run(
            ['python', script_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print(f"[OK] {description} completed successfully!")
            return True
        else:
            print(f"[ERROR] {description} failed with return code {result.returncode}")
            return False

    except Exception as e:
        print(f"[ERROR] Error running {description}: {e}")
        return False

def refresh_flask_server():
    """Try to refresh the Flask server if it's running"""
    print(f"\n{'='*80}")
    print("Attempting to refresh Flask server...")
    print(f"{'='*80}\n")

    try:
        response = requests.post('http://127.0.0.1:5000/refresh', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Flask server refreshed successfully!")
            print(f"   Jersey City events: {data.get('jersey_city_count', 'N/A')}")
            print(f"   Hoboken events: {data.get('hoboken_count', 'N/A')}")
            print(f"   Bookstore events: {data.get('bookstore_count', 'N/A')}")
            return True
        else:
            print(f"[WARNING] Server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[WARNING] Flask server is not running. Data files updated, but server needs manual restart.")
        return False
    except Exception as e:
        print(f"[WARNING] Could not refresh server: {e}")
        return False

def main():
    print("="*80)
    print("STORY TIME LOCATOR - UPDATE ALL EVENTS")
    print("="*80)
    print("This script will fetch fresh data from all sources...")
    print()

    success_count = 0
    total_parsers = 3

    # Run Jersey City parser
    if run_parser('jc_library_rss_parser.py', 'Jersey City Library RSS Parser'):
        success_count += 1

    # Run Hoboken parser
    if run_parser('hoboken_library_rss_parser.py', 'Hoboken Library RSS Parser'):
        success_count += 1

    # Run Bookstore scraper
    if run_parser('bookstore_scraper.py', 'Bookstore Scraper'):
        success_count += 1

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY: {success_count}/{total_parsers} data sources updated successfully")
    print(f"{'='*80}\n")

    # Try to refresh Flask server
    if success_count > 0:
        refresh_flask_server()

    print("\n[DONE] Update complete!")
    print("\nNext steps:")
    print("  - If server is running: Data is already refreshed!")
    print("  - If server is NOT running: Start it with 'python app.py'")
    print()

if __name__ == '__main__':
    main()
