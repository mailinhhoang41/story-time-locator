"""
Hoboken Public Library RSS Feed Parser

This parser fetches story time events from Hoboken Public Library's Communico system
by consuming their official RSS feeds. This is NOT web scraping - we're using
their public RSS feed designed for machine consumption.

Communico provides RSS feeds with base64-encoded filter parameters to get future events.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import base64

def build_rss_url(days=365):
    """
    Build Hoboken Library RSS URL with encoded parameters

    Args:
        days: Number of days ahead to fetch (default 365)

    Returns:
        Complete RSS feed URL
    """
    # Build filter parameters
    params = {
        "feedType": "rss",
        "filters": {
            "location": ["all"],
            "ages": ["all"],
            "types": ["all"],
            "tags": [],
            "term": "",
            "days": days
        }
    }

    # Encode parameters as base64
    params_json = json.dumps(params)
    params_encoded = base64.b64encode(params_json.encode()).decode()

    return f"https://hobokenlibrary.libnet.info/feeds?data={params_encoded}"


def fetch_storytime_events(days=365):
    """
    Fetch story time events from Hoboken Public Library using RSS feed

    Args:
        days: Number of days ahead to fetch (default 365)

    Returns:
        List of story time event dictionaries
    """

    print(f"Fetching story time events for next {days} days...")
    print("=" * 80)

    # Build RSS URL
    url = build_rss_url(days)
    print(f"\nFetching Hoboken Public Library events...")
    print(f"URL: {url[:80]}...")

    all_events = []

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        # Find all event items
        items = root.findall('.//item')
        print(f"Found {len(items)} total events")

        story_time_count = 0

        for item in items:
            # Extract basic fields
            title_elem = item.find('title')
            if title_elem is None:
                continue

            title = title_elem.text
            title_lower = title.lower()

            # Check if this is a story time or children's event
            keywords = ['story', 'storytime', 'story time', 'lap sit', 'reading',
                       'toddler', 'preschool', 'baby', 'babies', 'children', 'kids',
                       'early childhood', 'bilingual', 'little', 'movers']

            is_story_time = any(keyword in title_lower for keyword in keywords)

            # Also check description for keywords
            desc_elem = item.find('description')
            if desc_elem is not None and desc_elem.text:
                desc_lower = desc_elem.text.lower()
                if any(keyword in desc_lower for keyword in keywords):
                    is_story_time = True

            if is_story_time:
                story_time_count += 1

                # Build event dictionary
                event = {
                    'title': title,
                    'location': 'Hoboken Public Library'
                }

                # Extract description
                if desc_elem is not None and desc_elem.text:
                    event['description'] = desc_elem.text.strip()

                # Extract link
                link = item.find('link')
                if link is not None and link.text:
                    event['link'] = link.text

                # Extract publication date (event date/time)
                pub_date = item.find('pubDate')
                if pub_date is not None and pub_date.text:
                    try:
                        # Parse: "Wed, 22 Oct 2025 10:30:00 +0000"
                        dt = datetime.strptime(pub_date.text, '%a, %d %b %Y %H:%M:%S %z')

                        event['date'] = dt.strftime('%Y-%m-%d')
                        event['day_of_week'] = dt.strftime('%A')
                        event['start_time'] = dt.strftime('%H:%M:%S')
                        event['formatted_time'] = dt.strftime('%I:%M %p')
                        event['datetime'] = pub_date.text
                    except Exception as e:
                        print(f"Error parsing date '{pub_date.text}': {e}")

                # Extract author/organizer
                author = item.find('author')
                if author is not None and author.text:
                    event['organizer'] = author.text

                # Extract content (full description)
                content = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
                if content is not None and content.text:
                    event['full_description'] = content.text.strip()

                all_events.append(event)

        print(f"Found {story_time_count} story time events")

    except Exception as e:
        print(f"Error fetching Hoboken Library events: {str(e)}")

    return all_events


def display_events(events):
    """
    Display events in a readable format
    """
    print("\n" + "=" * 80)
    print(f"TOTAL STORY TIME EVENTS FOUND: {len(events)}")
    print("=" * 80)

    if not events:
        print("\nNo story time events found.")
        return

    # Group by day of week
    by_day = {}
    for event in events:
        day = event.get('day_of_week', 'Unknown')
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(event)

    # Display by day of week (in order)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days_order:
        if day in by_day:
            day_events = by_day[day]
            print(f"\n{day}: {len(day_events)} events")
            print("-" * 80)

            for event in day_events:
                print(f"\n  {event['title']}")

                if event.get('date') and event.get('formatted_time'):
                    print(f"  {event['date']} at {event['formatted_time']}")
                elif event.get('date'):
                    print(f"  {event['date']}")

                if event.get('description'):
                    # Show first 150 characters of description
                    # Clean up special characters that cause encoding issues
                    desc = event['description'][:150]
                    # Replace smart quotes, dashes, and other special chars
                    desc = (desc.replace('\x92', "'").replace('\x91', "'")
                               .replace('\x93', '"').replace('\x94', '"')
                               .replace('\x96', '-').replace('\x97', '-')
                               .encode('ascii', 'ignore').decode('ascii'))
                    if len(event['description']) > 150:
                        desc += "..."
                    print(f"  {desc}")

                if event.get('link'):
                    print(f"  Link: {event['link']}")


def save_to_json(events, filename='hoboken_storytimes.json'):
    """
    Save events to JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(events)} events to {filename}")


def main():
    print("=" * 80)
    print("HOBOKEN PUBLIC LIBRARY RSS FEED PARSER")
    print("Consuming Communico RSS Feeds (Not Web Scraping)")
    print("=" * 80)
    print()

    # Fetch events for next year
    events = fetch_storytime_events(days=365)

    if events:
        # Display results
        display_events(events)

        # Save to JSON
        save_to_json(events)

        print("\n" + "=" * 80)
        print("SUCCESS! Story time data collected automatically!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Review hoboken_storytimes.json")
        print("2. Run this script weekly to keep data current")
        print("3. Integrate with Jersey City data for combined results")
    else:
        print("\nNo story time events found. This could mean:")
        print("1. No events scheduled for the next year")
        print("2. Library hasn't published events yet")
        print("3. RSS feed parameters need adjustment")


if __name__ == "__main__":
    main()
