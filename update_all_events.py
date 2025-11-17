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

        # After Hoboken parser, add manual events (ballet classes and Bunny Hive)
        print("\n" + "="*80)
        print("Adding manual Hoboken events (ballet & Bunny Hive)...")
        print("="*80 + "\n")

        # Add ballet classes
        if run_parser('add_ballet_classes.py', 'Ballet Classes'):
            print("[OK] Ballet classes added")

        # Add Bunny Hive events
        try:
            import json
            with open('hoboken_storytimes.json', 'r', encoding='utf-8') as f:
                events = json.load(f)

            bunny_events = [
                {'title': 'Books and Bubbles Pop Up', 'location': 'The Bunny Hive', 'description': 'Friday, November 14 2025 12:00pm - 12:30pm \n Join us for Books and Bubbles at The Bunny Hive in Hoboken!', 'link': 'https://www.thebunnyhive.com/hoboken', 'date': '2025-11-14', 'day_of_week': 'Friday', 'start_time': '12:00:00', 'formatted_time': '12:00 PM', 'datetime': 'Fri, 14 Nov 2025 12:00:00 +0000', 'organizer': 'The Bunny Hive', 'full_description': 'Join us for Books and Bubbles at The Bunny Hive in Hoboken!', 'audience': 'All Ages'},
                {'title': 'Books and Bubbles Pop Up', 'location': 'The Bunny Hive', 'description': 'Friday, November 21 2025 12:00pm - 12:30pm \n Join us for Books and Bubbles at The Bunny Hive in Hoboken!', 'link': 'https://www.thebunnyhive.com/hoboken', 'date': '2025-11-21', 'day_of_week': 'Friday', 'start_time': '12:00:00', 'formatted_time': '12:00 PM', 'datetime': 'Fri, 21 Nov 2025 12:00:00 +0000', 'organizer': 'The Bunny Hive', 'full_description': 'Join us for Books and Bubbles at The Bunny Hive in Hoboken!', 'audience': 'All Ages'}
            ]

            events.extend(bunny_events)

            with open('hoboken_storytimes.json', 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)

            print(f"[OK] Bunny Hive events added ({len(bunny_events)} events)")
            print(f"[OK] Total Hoboken events: {len(events)}")
        except Exception as e:
            print(f"[WARNING] Could not add Bunny Hive events: {e}")

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

    # Push to GitHub to update live site
    # Note: Git commits should be done manually
    # if success_count > 0:
    #     push_to_github()

    print("\n[DONE] Update complete!")
    print("\nNext steps:")
    print("  - Review the updated JSON files")
    print("  - Restart Flask server if needed")
    print("  - Commit and push to GitHub manually if you want to update live site")
    print()

if __name__ == '__main__':
    main()
