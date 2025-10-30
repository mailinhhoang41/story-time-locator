"""
Update and Deploy Script - ONE COMMAND TO UPDATE EVERYTHING

This script:
1. Fetches fresh data from libraries & bookstores
2. Commits changes to git
3. Pushes to GitHub (triggers Render deployment)
4. Updates both local AND live site

Just run: python update_and_deploy.py
OR double-click: update_and_deploy.bat
"""

import subprocess
import sys
from datetime import datetime

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*80}")
    print(f"{description}...")
    print(f"{'='*80}\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=True if isinstance(cmd, str) else False
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(result.stderr)

        if result.returncode == 0:
            print(f"[OK] {description} completed")
            return True
        else:
            print(f"[ERROR] {description} failed")
            return False
    except Exception as e:
        print(f"[ERROR] {description} failed: {e}")
        return False

def main():
    print("="*80)
    print("STORY TIME LOCATOR - UPDATE AND DEPLOY")
    print("="*80)
    print("This will update data locally AND on the live site")
    print("="*80)
    print()

    # Step 1: Run parsers
    parsers = [
        ('python jc_library_rss_parser.py', 'Fetching Jersey City Library events'),
        ('python hoboken_library_rss_parser.py', 'Fetching Hoboken Library events'),
        ('python bookstore_scraper.py', 'Fetching Bookstore events'),
    ]

    success_count = 0
    for cmd, desc in parsers:
        if run_command(cmd, desc):
            success_count += 1

    print(f"\n{'='*80}")
    print(f"PARSERS COMPLETE: {success_count}/3 successful")
    print(f"{'='*80}\n")

    if success_count == 0:
        print("[ERROR] All parsers failed. Aborting deployment.")
        return

    # Step 2: Check if there are changes
    print(f"\n{'='*80}")
    print("Checking for changes...")
    print(f"{'='*80}\n")

    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        print("[INFO] No changes detected - data is already up to date!")
        print("       Both local and live site have the latest data.")
        return

    print("[INFO] Changes detected in data files")

    # Step 3: Git add
    if not run_command(
        ['git', 'add', '*_storytimes.json'],
        'Adding updated data files to git'
    ):
        print("[ERROR] Failed to add files. Aborting.")
        return

    # Step 4: Git commit
    timestamp = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    commit_msg = f"Auto-update: Fresh event data - {timestamp}"

    if not run_command(
        ['git', 'commit', '-m', commit_msg],
        f'Creating commit: {commit_msg}'
    ):
        print("[ERROR] Failed to commit. Aborting.")
        return

    # Step 5: Git push
    if not run_command(
        ['git', 'push'],
        'Pushing to GitHub'
    ):
        print("[ERROR] Failed to push to GitHub")
        print("        You may need to check your git credentials")
        return

    # Success!
    print(f"\n{'='*80}")
    print("SUCCESS! DEPLOYMENT INITIATED")
    print(f"{'='*80}\n")
    print("✅ Local data: UPDATED")
    print("✅ GitHub: UPDATED")
    print("✅ Render deployment: STARTED (will complete in 3-5 minutes)")
    print()
    print("Live site: https://story-time-locator.onrender.com")
    print()
    print("Check deployment status at:")
    print("https://dashboard.render.com/")
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
