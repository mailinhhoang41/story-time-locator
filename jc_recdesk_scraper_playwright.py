"""
Jersey City Recreation Department Scraper (Playwright Version)

This scraper uses Playwright to fetch POP UP classes from RecDesk.
Playwright is more modern and reliable than Selenium, and it manages
its own browsers so there are no driver compatibility issues!
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time


def extract_schedule_from_detail_page(page, program_link):
    """
    Visit a program detail page and extract schedule (dates/times) and age range

    Args:
        page: Playwright page object
        program_link: URL to the program detail page

    Returns:
        list: List of schedule entries with dates/times and age range
    """
    schedules = []
    age_min = None
    age_max = None

    try:
        print(f"[RecDesk]   Visiting detail page...")
        page.goto(program_link, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Extract age range from the detail table
        # Find all table rows and look for "Age Minimum" label
        all_rows = soup.find_all('tr')
        for i, row in enumerate(all_rows):
            row_text = row.get_text(strip=True)

            # Check if this row contains "Age Minimum"
            if 'Age Minimum' in row_text:
                # Extract the value from <strong> tag
                strong_tag = row.find('strong')
                if strong_tag:
                    age_text = strong_tag.get_text(strip=True)
                    age_min = age_text.replace(' years', '').replace(' year', '').strip()

                # Check the NEXT row for "Maximum"
                if i + 1 < len(all_rows):
                    next_row = all_rows[i + 1]
                    next_row_text = next_row.get_text(strip=True)

                    if 'Maximum' in next_row_text:
                        strong_tag = next_row.find('strong')
                        if strong_tag:
                            age_text = strong_tag.get_text(strip=True)
                            age_max = age_text.replace(' years', '').replace(' year', '').strip()

                break  # Found what we need, exit loop

        if age_min and age_max:
            print(f"[RecDesk]   Found age range: {age_min} - {age_max}")

        # Look for the schedule tab div with id="program-schedule"
        schedule_div = soup.find(id='program-schedule')

        if schedule_div:
            # Find the table within the schedule div
            schedule_table = schedule_div.find('table')

            if schedule_table:
                # Find all table rows (skip header row)
                rows = schedule_table.find('tbody').find_all('tr') if schedule_table.find('tbody') else []

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:  # Need at least date, day, start time
                        schedule = {}

                        # Cell 0: Date (e.g., "12/04/2025")
                        date_text = cells[0].get_text(strip=True)
                        try:
                            dt = datetime.strptime(date_text, '%m/%d/%Y')
                            schedule['date'] = dt.strftime('%Y-%m-%d')
                            schedule['day_of_week'] = dt.strftime('%A')
                        except:
                            continue

                        # Cell 2: Start Time (e.g., "4:50 PM")
                        if len(cells) > 2:
                            time_text = cells[2].get_text(strip=True)
                            try:
                                time_obj = datetime.strptime(time_text, '%I:%M %p')
                                schedule['start_time'] = time_obj.strftime('%H:%M:%S')
                                schedule['formatted_time'] = time_text
                            except:
                                try:
                                    time_obj = datetime.strptime(time_text, '%I:%M%p')
                                    schedule['start_time'] = time_obj.strftime('%H:%M:%S')
                                    schedule['formatted_time'] = time_obj.strftime('%I:%M %p')
                                except:
                                    pass

                        # Cell 4: Location (get the actual venue location)
                        if len(cells) > 4:
                            location = cells[4].get_text(strip=True)
                            if location and len(location) > 2:  # Make sure it's not empty
                                schedule['location'] = location

                        # Only add if we have at least date and time
                        if schedule.get('date') and schedule.get('start_time'):
                            # Add age range to this schedule entry
                            if age_min:
                                schedule['age_min'] = age_min
                            if age_max:
                                schedule['age_max'] = age_max
                            schedules.append(schedule)

            print(f"[RecDesk]   Found {len(schedules)} scheduled sessions")

    except Exception as e:
        print(f"[RecDesk]   Error extracting schedule: {e}")

    return schedules


def scrape_recdesk_with_playwright():
    """
    Use Playwright to scrape RecDesk programs

    Returns:
        list: List of POP UP class dictionaries
    """
    print("\n[RecDesk] Starting Playwright browser...")
    programs = []

    with sync_playwright() as p:
        try:
            # Launch browser (headless=False shows the browser window)
            print("[RecDesk] Launching Chromium...")
            browser = p.chromium.launch(headless=False)  # Set to True to hide browser

            # Create a new page
            page = browser.new_page()

            # Set longer timeout for page operations
            page.set_default_timeout(60000)

            # Navigate to RecDesk
            url = "https://jcrec.recdesk.com/Community/Program"
            print(f"[RecDesk] Loading {url}...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Wait for initial content
            time.sleep(3)

            # Select "100" from the results per page dropdown to see all programs
            print("[RecDesk] Setting results per page to 100...")
            try:
                # Find and click the dropdown
                page.select_option('#ResultsPerPage', '100')
                time.sleep(5)  # Wait for page to reload with 100 results
                print("[RecDesk] Successfully set to 100 results per page")
            except Exception as e:
                print(f"[RecDesk] Could not change results per page: {e}")

            # Get HTML with all programs loaded
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Find all POP UP programs
            all_popup_programs_found = []
            data_list = soup.find(id='data-list')
            if data_list:
                rows = data_list.find_all('tr')
                print(f"\n[RecDesk] Total programs loaded: {len(rows)}")

                for row in rows:
                    try:
                        program = parse_program_row(row)
                        if program and is_popup_program(program):
                            print(f"[RecDesk] Found POP UP: {program['title']}")
                            all_popup_programs_found.append(program)
                    except Exception as e:
                        pass

            print(f"\n[RecDesk] Found {len(all_popup_programs_found)} total POP UP programs across all pages")

            # Now visit each program's detail page to get schedules
            for program in all_popup_programs_found:
                if program.get('link'):
                    schedules = extract_schedule_from_detail_page(page, program['link'])

                    # If we found schedules, create separate entries for each session
                    if schedules:
                        for schedule in schedules:
                            # Create a copy of the program with this specific schedule
                            program_with_schedule = program.copy()
                            program_with_schedule.update(schedule)
                            programs.append(program_with_schedule)
                    else:
                        # No schedule found, add program as-is
                        programs.append(program)
                else:
                    # No link, add program as-is
                    programs.append(program)

            # Also search for any text containing "POP UP"
            if not programs:
                print("[RecDesk] No programs in table, searching full page...")
                all_elements = soup.find_all(text=re.compile(r'POP[\s-]?UP', re.I))
                print(f"[RecDesk] Found {len(all_elements)} elements with 'POP UP' text")

                for element in all_elements:
                    try:
                        parent = element.parent
                        program_text = parent.get_text(strip=True)

                        if len(program_text) > 5:
                            program = {
                                'title': program_text[:200],
                                'venue_type': 'recreation',
                                'venue_name': 'Jersey City Recreation Department',
                                'city': 'Jersey City',
                                'categories': ['Recreation Classes', 'FREE', 'POP UP'],
                                'is_all_day': False
                            }

                            # Try to find link
                            link = parent.find_parent('a') or parent.find('a')
                            if link and link.get('href'):
                                href = link.get('href')
                                if not href.startswith('http'):
                                    program['link'] = f"https://jcrec.recdesk.com{href}"
                                else:
                                    program['link'] = href

                            # Avoid duplicates
                            if not any(p.get('title') == program['title'] for p in programs):
                                programs.append(program)
                                print(f"[RecDesk] Found POP UP: {program['title']}")

                    except Exception as e:
                        pass

            # Close browser
            browser.close()
            print(f"\n[RecDesk] Successfully found {len(programs)} POP UP programs")

        except Exception as e:
            print(f"[RecDesk] Error: {e}")
            import traceback
            traceback.print_exc()

    return programs


def parse_program_row(row):
    """
    Parse a table row for program information

    Args:
        row: BeautifulSoup tr element

    Returns:
        dict: Program data or None
    """
    cells = row.find_all('td')
    if not cells:
        return None

    program = {
        'venue_type': 'recreation',
        'venue_name': 'Jersey City Recreation Department',
        'city': 'Jersey City',
        'categories': ['Recreation Classes', 'FREE', 'POP UP'],
        'is_all_day': False
    }

    # First cell usually has title
    title_cell = cells[0]
    title_link = title_cell.find('a')

    if title_link:
        program['title'] = title_link.get_text(strip=True)
        href = title_link.get('href', '')
        if href and not href.startswith('http'):
            program['link'] = f"https://jcrec.recdesk.com{href}"
    else:
        program['title'] = title_cell.get_text(strip=True)

    # Try to extract info from other cells
    for cell in cells[1:]:
        text = cell.get_text(strip=True)

        # Date pattern
        date_match = re.match(r'(\d{1,2}/\d{1,2}/\d{4})', text)
        if date_match:
            try:
                dt = datetime.strptime(date_match.group(1), '%m/%d/%Y')
                program['date'] = dt.strftime('%Y-%m-%d')
                program['day_of_week'] = dt.strftime('%A')
            except:
                pass

        # Time pattern
        if re.search(r'\d{1,2}:\d{2}\s*[AP]M', text, re.I):
            if 'description' not in program:
                program['description'] = text

        # Age pattern
        if 'age' in text.lower() and len(text) < 50:
            program['audience'] = text

        # Location
        if len(text) > 10 and len(text) < 100 and 'location' not in program:
            if not any(char.isdigit() for char in text):  # Probably not a date/time
                program['location'] = text

    return program if 'title' in program and len(program['title']) > 3 else None


def is_popup_program(program):
    """Check if program is a POP UP class"""
    title = program.get('title', '')
    # Check for "pop" anywhere in title (case insensitive)
    return 'pop' in title.lower()


def save_popup_programs(programs, filename='jc_recdesk_popup.json'):
    """Save POP UP programs to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(programs, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCCESS] Saved {len(programs)} POP UP programs to {filename}")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to save: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("JERSEY CITY RECDESK - PLAYWRIGHT SCRAPER")
    print("=" * 60)
    print("\nPlaywright will open a browser window.")
    print("Watch it navigate and load the programs!")
    print("=" * 60)

    # Scrape programs
    programs = scrape_recdesk_with_playwright()

    # Save results
    if programs:
        save_popup_programs(programs)
        print("\nSuccess! Next steps:")
        print("1. Review jc_recdesk_popup.json")
        print("2. Update app.py to load these classes")
        print("3. Restart Flask and check your website!")
    else:
        print("\nNo POP UP programs found.")
        print("Check recdesk_playwright.html to see what was captured.")
        print("\nYou can also:")
        print("- Use manual entry: python add_popup_classes_manual.py")
        print("- Email me the RecDesk page content for debugging")

    print("=" * 60)
    return programs


if __name__ == '__main__':
    main()
