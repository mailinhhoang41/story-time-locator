"""
Bookstore Event Scraper

This scraper fetches story time and children's events from local bookstores
in Jersey City and Hoboken.

Current sources:
- Little City Books (Hoboken) - littlecitybooks.com/events

Unlike libraries which have RSS feeds, bookstores usually have HTML event pages
that require web scraping with BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import re


def scrape_little_city_books():
    """
    Scrape events from Little City Books in Hoboken

    URL: https://littlecitybooks.com/events

    Returns:
        list: List of event dictionaries
    """
    print("\n[Little City Books] Scraping events...")

    url = "https://littlecitybooks.com/events"
    events = []

    try:
        # Fetch the events page with proper headers to avoid bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find event containers
        # Little City Books uses Drupal with custom event-list classes
        # Each event is in a <div class="views-row"> container
        event_blocks = soup.find_all('div', class_='views-row')

        print(f"[Little City Books] Found {len(event_blocks)} event blocks")

        for block in event_blocks:
            try:
                event = parse_little_city_event(block)
                if event and is_children_event(event):
                    events.append(event)
            except Exception as e:
                print(f"[Little City Books] Error parsing event: {e}")
                continue

        print(f"[Little City Books] Successfully scraped {len(events)} children's events")

    except requests.RequestException as e:
        print(f"[Little City Books] Error fetching events: {e}")
    except Exception as e:
        print(f"[Little City Books] Unexpected error: {e}")

    return events


def parse_little_city_event(block):
    """
    Parse a single event block from Little City Books

    Args:
        block: BeautifulSoup element containing event data

    Returns:
        dict: Event data
    """
    event = {
        'venue_type': 'bookstore',
        'venue_name': 'Little City Books',
        'city': 'Hoboken',
        'location': 'Little City Books, 100 Bloomfield St, Hoboken, NJ'
    }

    # Extract title from <h3 class="event-list__title">
    title_elem = block.find('h3', class_='event-list__title')
    if title_elem:
        title_link = title_elem.find('a')
        if title_link:
            event['title'] = title_link.get_text(strip=True)
            # Also get the event detail link
            href = title_link.get('href', '')
            if href and not href.startswith('http'):
                event['link'] = f"https://littlecitybooks.com{href}"

    # Extract description from <div class="event-list__body">
    desc_elem = block.find('div', class_='event-list__body')
    if desc_elem:
        event['description'] = desc_elem.get_text(strip=True)
        event['full_description'] = event['description']

    # Extract date and time from event-list__details--item divs
    details_items = block.find_all('div', class_='event-list__details--item')

    for detail in details_items:
        label = detail.find('span', class_='event-list__details--label')
        if label:
            label_text = label.get_text(strip=True)
            # Get the text after the label
            value_text = detail.get_text(strip=True).replace(label_text, '').strip()

            if 'Date:' in label_text and value_text:
                # Parse date like "Wed, 10/1/2025"
                try:
                    # Extract day of week
                    if ',' in value_text:
                        day_part, date_part = value_text.split(',', 1)
                        event['day_of_week'] = day_part.strip()
                        date_str = date_part.strip()

                        # Parse date (format: 10/1/2025)
                        dt = datetime.strptime(date_str, '%m/%d/%Y')
                        event['date'] = dt.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"[Parse Error] Date parsing failed: {e}")

            elif 'Time:' in label_text and value_text:
                # Parse time like "10:00am - 10:45am"
                try:
                    if ' - ' in value_text:
                        start_str, end_str = value_text.split(' - ', 1)

                        # Parse start time
                        start_time = datetime.strptime(start_str.strip(), '%I:%M%p')
                        event['start_time'] = start_time.strftime('%H:%M:%S')
                        event['formatted_time'] = start_time.strftime('%I:%M %p').lstrip('0')

                        # Parse end time
                        end_time = datetime.strptime(end_str.strip(), '%I:%M%p')
                        event['end_time'] = end_time.strftime('%H:%M:%S')
                        event['formatted_end_time'] = end_time.strftime('%I:%M %p').lstrip('0')
                except Exception as e:
                    print(f"[Parse Error] Time parsing failed: {e}")

    # Extract RSVP/registration link
    rsvp_elem = block.find('a', class_='event-list__links--rsvp')
    if rsvp_elem:
        rsvp_link = rsvp_elem.get('href', '')
        if rsvp_link:
            event['registration_link'] = rsvp_link

    # Extract age range from description if available
    if 'description' in event:
        age_match = re.search(r'(\d+)\s*-\s*(\d+)', event['description'])
        if age_match:
            event['audience'] = f"Ages {age_match.group(1)}-{age_match.group(2)}"
        elif '0-5' in event['description'] or '0 -5' in event['description']:
            event['audience'] = "Ages 0-5"

    # Add categories
    event['categories'] = ['Bookstore Events', 'Storytime Events']

    return event if 'title' in event else None


def is_children_event(event):
    """
    Check if event is for children

    Args:
        event: Event dictionary

    Returns:
        bool: True if children's event
    """
    children_keywords = [
        'story time', 'storytime', 'children', 'kids', 'toddler',
        'baby', 'preschool', 'family', 'laura', 'ages 0'
    ]

    text = (event.get('title', '') + ' ' + event.get('description', '')).lower()

    return any(keyword in text for keyword in children_keywords)


def expand_recurring_story_time(template_event):
    """
    Generate recurring Wednesday story time events for the next 12 weeks

    Little City Books has "Story Time with Laura" every Wednesday at 10am.
    Since they don't list all future dates, we generate them.

    Args:
        template_event: Template event dictionary

    Returns:
        list: List of recurring events
    """
    events = []

    # Start from next Wednesday
    today = datetime.now().date()
    days_until_wednesday = (2 - today.weekday()) % 7  # 2 = Wednesday
    if days_until_wednesday == 0 and datetime.now().hour >= 10:
        # If it's Wednesday after 10am, start next week
        days_until_wednesday = 7

    next_wednesday = today + timedelta(days=days_until_wednesday)

    # Generate 12 weeks of Wednesday events
    for week in range(12):
        event_date = next_wednesday + timedelta(weeks=week)

        event = template_event.copy()
        event['date'] = event_date.strftime('%Y-%m-%d')
        event['day_of_week'] = 'Wednesday'
        event['start_time'] = '10:00:00'
        event['formatted_time'] = '10:00 AM'
        event['end_time'] = '10:45:00'

        # Update description to include specific date
        date_str = event_date.strftime('%B %d, %Y')
        event['description'] = f"Story Time with Laura on {date_str}. For kids 0-5ish. Join Laura for stories, songs, and boundless affection."

        events.append(event)

    return events


def save_bookstore_events(events, filename='bookstore_storytimes.json'):
    """
    Save bookstore events to JSON file

    Args:
        events: List of event dictionaries
        filename: Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCCESS] Saved {len(events)} bookstore events to {filename}")
    except Exception as e:
        print(f"\n[ERROR] Failed to save events: {e}")


def main():
    """
    Main function to scrape all bookstore events
    """
    print("=" * 60)
    print("BOOKSTORE EVENT SCRAPER")
    print("=" * 60)

    all_events = []

    # Scrape Little City Books
    little_city_events = scrape_little_city_books()
    all_events.extend(little_city_events)

    # Future: Add more bookstores here
    # word_events = scrape_word_jersey_city()
    # all_events.extend(word_events)

    # Save to JSON
    if all_events:
        save_bookstore_events(all_events)
        print(f"\nTotal bookstore events: {len(all_events)}")
    else:
        print("\n[WARNING] No bookstore events found")

    print("=" * 60)


if __name__ == '__main__':
    main()
