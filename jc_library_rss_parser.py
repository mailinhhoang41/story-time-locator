"""
Jersey City Library RSS Feed Parser

This parser fetches story time events from Jersey City Library's LibCal system
by consuming their official RSS feeds. This is NOT web scraping - we're using
their public API/RSS feed designed for machine consumption.

LibCal provides RSS feeds with date range parameters to get future events.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

def fetch_storytime_events(months=3):
    """
    Fetch story time events from Jersey City Library using LibCal RSS feeds

    Args:
        months: Number of months ahead to fetch (default 3)

    Returns:
        List of story time event dictionaries
    """

    # Calendar IDs for ALL Jersey City Library calendars (12 total!)
    # NOTE: Heights Branch (17426) is closed for renovation - events at West Bergen (17421)
    calendar_ids = {
        17419: "Priscilla Gardner Main Library",
        17420: "Earl A. Morgan Branch (Greenville)",
        17421: "West Bergen Branch",  # Temporary location for Heights Branch events
        17422: "Pavonia Branch",
        17423: "Miller Branch",
        17424: "Marion Branch",
        17425: "Lafayette Branch",
        17426: "Heights Branch",  # Closed for renovation, check if has any events
        17427: "Glenn D. Cunningham Branch",
        17430: "Five Corners Branch",  # HAS LITTLE MOVERS STORYTIME!
        17432: "Bookmobile",
        19967: "Communipaw Branch",
    }

    all_events = []

    print(f"Fetching story time events for next {months} months...")
    print("=" * 80)

    for cid, branch_name in calendar_ids.items():
        # Build RSS URL with month mode parameter
        # Using m=month gets events for the coming month
        # Note: months= and days= parameters don't work reliably
        url = f"https://jclibrary.libcal.com/rss.php?cid={cid}&m=month"

        print(f"\nFetching {branch_name} (ID: {cid})...")
        print(f"URL: {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Define namespace for LibCal elements
            ns = {'libcal': 'https://libcal.com/rss_xmlns.php'}

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
                keywords = ['story', 'storytime', 'lap sit', 'reading', 'toddler', 'preschool',
                           'baby', 'children', 'kids', 'early childhood', 'bilingual']

                is_story_time = any(keyword in title_lower for keyword in keywords)

                # Also check audience field
                audience = item.find('libcal:audience', ns)
                if audience is not None and audience.text:
                    audience_text = audience.text.lower()
                    if 'early childhood' in audience_text or 'children' in audience_text:
                        is_story_time = True

                if is_story_time:
                    story_time_count += 1

                    # Build event dictionary
                    # IMPORTANT: Don't use calendar branch name for location!
                    # Events can be at different branches (e.g., Heights calendar
                    # shows events at West Bergen while Heights is closed)
                    event = {
                        'title': title,
                        'calendar_source': branch_name,  # Which calendar it came from
                        'calendar_id': cid
                    }

                    # Extract description
                    desc = item.find('description')
                    if desc is not None and desc.text:
                        event['description'] = desc.text

                    # Extract link
                    link = item.find('link')
                    if link is not None and link.text:
                        event['link'] = link.text

                    # Extract LibCal-specific fields
                    date_elem = item.find('libcal:date', ns)
                    if date_elem is not None and date_elem.text:
                        event['date'] = date_elem.text

                        # Parse date to get day of week
                        try:
                            dt = datetime.strptime(date_elem.text, '%Y-%m-%d')
                            event['day_of_week'] = dt.strftime('%A')
                        except:
                            pass

                    # Start time
                    start_elem = item.find('libcal:start', ns)
                    if start_elem is not None and start_elem.text:
                        event['start_time'] = start_elem.text

                        # Format as readable time
                        try:
                            time_obj = datetime.strptime(start_elem.text, '%H:%M:%S')
                            event['formatted_time'] = time_obj.strftime('%I:%M %p')
                        except:
                            pass

                    # End time
                    end_elem = item.find('libcal:end', ns)
                    if end_elem is not None and end_elem.text:
                        event['end_time'] = end_elem.text

                    # Location - THIS IS THE ACTUAL LOCATION, use this for display!
                    location = item.find('libcal:location', ns)
                    if location is not None and location.text:
                        event['location'] = location.text  # Use this to show users where event is

                    # Audience (age range)
                    if audience is not None and audience.text:
                        event['audience'] = audience.text

                    # Categories
                    categories = item.findall('category')
                    if categories:
                        event['categories'] = [cat.text for cat in categories if cat.text]

                    all_events.append(event)

            print(f"Found {story_time_count} story time events")

        except Exception as e:
            print(f"Error fetching {branch_name}: {str(e)}")

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

    # Group by actual location (not calendar source)
    by_location = {}
    for event in events:
        # Use actual location for grouping, not calendar source
        location = event.get('location', 'Unknown Location')
        if location not in by_location:
            by_location[location] = []
        by_location[location].append(event)

    # Display by actual location
    for location, location_events in sorted(by_location.items()):
        print(f"\n{location}: {len(location_events)} events")
        print("-" * 80)

        for event in location_events:
            print(f"\n  {event['title']}")

            if event.get('day_of_week') and event.get('formatted_time'):
                print(f"  {event['day_of_week']}, {event['date']} at {event['formatted_time']}")
            elif event.get('date'):
                print(f"  {event['date']}")

            # Show calendar source if different from location
            if event.get('calendar_source'):
                print(f"  Calendar: {event['calendar_source']}")

            if event.get('audience'):
                print(f"  Ages: {event['audience']}")

            if event.get('link'):
                print(f"  Link: {event['link']}")


def save_to_json(events, filename='jersey_city_storytimes.json'):
    """
    Save events to JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(events)} events to {filename}")


def main():
    print("=" * 80)
    print("JERSEY CITY LIBRARY RSS FEED PARSER")
    print("Consuming LibCal RSS Feeds (Not Web Scraping)")
    print("=" * 80)
    print()

    # Fetch events for next 3 months
    events = fetch_storytime_events(months=3)

    if events:
        # Display results
        display_events(events)

        # Save to JSON
        save_to_json(events)

        print("\n" + "=" * 80)
        print("SUCCESS! Story time data collected automatically!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Review jersey_city_storytimes.json")
        print("2. Run this script weekly to keep data current")
        print("3. Integrate this data into your main app")
        print("4. No manual research needed - fully automated!")
    else:
        print("\nNo story time events found. This could mean:")
        print("1. No events scheduled for the next 3 months")
        print("2. Library hasn't published events yet")
        print("3. RSS feed parameters need adjustment")


if __name__ == "__main__":
    main()
