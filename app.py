"""
Story Time Locator - Flask Backend (Rewritten for Local Data)

NEW APPROACH: No APIs needed!
This app now:
1. Loads story time data from local JSON files (scraped from library RSS feeds)
2. Filters events based on user preferences
3. Returns matching results instantly

Architecture:
- Data Layer: JSON files with pre-scraped events
- Application Layer: Flask filters and serves data
- No external API calls = Free, fast, reliable!
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import json
import os
import re

# Initialize Flask app
# Flask is a web framework that handles HTTP requests/responses
app = Flask(__name__)

# Global variables to store event data
# We load this once when the server starts, then filter it for each search
jersey_city_events = []
hoboken_events = []
bookstore_events = []


def load_event_data():
    """
    Load story time events from JSON files into memory

    This runs once when the server starts. We read the JSON files
    that were created by our RSS parsers and store them in memory
    for fast filtering.

    Why load at startup? Much faster than reading files on every search!
    """
    global jersey_city_events, hoboken_events, bookstore_events

    try:
        # Load Jersey City events
        jc_path = os.path.join(os.path.dirname(__file__), 'jersey_city_storytimes.json')
        with open(jc_path, 'r', encoding='utf-8') as f:
            jersey_city_events = json.load(f)
            print(f"[OK] Loaded {len(jersey_city_events)} Jersey City events")
    except FileNotFoundError:
        print("[WARNING] jersey_city_storytimes.json not found - run jc_library_rss_parser.py first")
        jersey_city_events = []
    except Exception as e:
        print(f"[ERROR] Error loading Jersey City data: {e}")
        jersey_city_events = []

    try:
        # Load Hoboken events
        hoboken_path = os.path.join(os.path.dirname(__file__), 'hoboken_storytimes.json')
        with open(hoboken_path, 'r', encoding='utf-8') as f:
            hoboken_events = json.load(f)
            print(f"[OK] Loaded {len(hoboken_events)} Hoboken events")
    except FileNotFoundError:
        print("[WARNING] hoboken_storytimes.json not found - run hoboken_library_rss_parser.py first")
        hoboken_events = []
    except Exception as e:
        print(f"[ERROR] Error loading Hoboken data: {e}")
        hoboken_events = []

    try:
        # Load Bookstore events
        bookstore_path = os.path.join(os.path.dirname(__file__), 'bookstore_storytimes.json')
        with open(bookstore_path, 'r', encoding='utf-8') as f:
            bookstore_events = json.load(f)
            print(f"[OK] Loaded {len(bookstore_events)} bookstore events")
    except FileNotFoundError:
        print("[WARNING] bookstore_storytimes.json not found - run bookstore_scraper.py first")
        bookstore_events = []
    except Exception as e:
        print(f"[ERROR] Error loading bookstore data: {e}")
        bookstore_events = []


@app.route('/')
def index():
    """
    Homepage route - serves the main HTML form

    When a user visits the root URL, Flask looks for index.html
    in the templates/ folder and sends it to their browser
    """
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """
    Search endpoint - filters events based on user preferences

    NEW APPROACH: Instead of calling external APIs, we filter our
    local JSON data. This is much faster and completely free!

    Filtering steps:
    1. Filter by city (Jersey City, Hoboken, or both)
    2. Filter by age range (match to event audience)
    3. Filter by day of week
    4. Filter out past events (only show upcoming)
    5. Sort by date (soonest first)
    """
    try:
        # Extract user inputs from the POST request
        # The frontend sends these as JSON in the request body
        data = request.get_json()
        city = data.get('city', 'both')  # 'jersey_city', 'hoboken', or 'both'
        kids_ages = data.get('kids_ages', '')
        days_preference = data.get('days', [])  # List of selected days
        date_range = data.get('date_range', 'all')  # 'week', '2weeks', 'month', 'all'
        time_of_day = data.get('time_of_day', [])  # ['morning', 'afternoon', 'evening']
        venue_type = data.get('venue_type', 'all')  # 'all', 'library', 'bookstore'
        event_type = data.get('event_type', 'all')  # 'all', 'storytime', 'arts', 'steam', 'music'

        # Start with all events based on city selection
        events = []

        if city == 'jersey_city':
            # Include Jersey City library events + bookstore events in Jersey City
            events = jersey_city_events.copy()
            # Add bookstore events that are in Jersey City
            events += [event for event in bookstore_events if event.get('city', '').lower() == 'jersey city']
        elif city == 'hoboken':
            # Include Hoboken library events + bookstore events in Hoboken
            events = hoboken_events.copy()
            # Add bookstore events that are in Hoboken
            events += [event for event in bookstore_events if event.get('city', '').lower() == 'hoboken']
        else:  # 'both'
            # Combine both cities and add a 'city' field for display
            events = [
                {**event, 'city': 'Jersey City'}
                for event in jersey_city_events
            ] + [
                {**event, 'city': 'Hoboken'}
                for event in hoboken_events
            ] + [
                # Bookstore events already have a 'city' field, so include them as-is
                event for event in bookstore_events
            ]

        # Filter out past events first (before other filters)
        events = filter_upcoming_events(events)

        # Filter by date range if specified
        if date_range != 'all':
            events = filter_by_date_range(events, date_range)

        # Filter by age range if specified
        # Age format: "0-2", "3-5", "6-11", etc.
        if kids_ages:
            events = filter_by_age(events, kids_ages)

        # Filter by day of week if specified
        # Days format: ["Monday", "Wednesday", "Saturday"]
        if days_preference:
            events = filter_by_days(events, days_preference)

        # Filter by time of day if specified
        # Time format: ["morning", "afternoon", "evening"]
        if time_of_day:
            events = filter_by_time_of_day(events, time_of_day)

        # Filter by venue type if specified
        if venue_type != 'all':
            events = filter_by_venue_type(events, venue_type)

        # Filter by event type if specified
        if event_type != 'all':
            events = filter_by_event_type(events, event_type)

        # Add duration info to each event (for frontend display)
        events = add_duration_info(events)

        # Sort by date (soonest first)
        events = sort_by_date(events)

        # Return results
        return jsonify({
            'results': events,
            'count': len(events),
            'user_preferences': {
                'city': city,
                'kids_ages': kids_ages,
                'days': days_preference,
                'date_range': date_range,
                'time_of_day': time_of_day,
                'event_type': event_type
            }
        })

    except Exception as e:
        # Catch any unexpected errors and return a friendly message
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


def extract_age_range_from_text(text):
    """
    Extract age range from description text using regex

    Looks for patterns like:
    - "ages 4-18"
    - "for ages 0-5"
    - "ages 3 to 11"
    - "4-18 years old"

    Args:
        text: Event description text

    Returns:
        tuple: (min_age, max_age) or None if not found
    """
    if not text:
        return None

    # Pattern 1: "ages X-Y" or "ages X to Y"
    pattern1 = r'ages?\s+(\d+)\s*(?:-|to)\s*(\d+)'
    match = re.search(pattern1, text.lower())
    if match:
        return (int(match.group(1)), int(match.group(2)))

    # Pattern 2: "for ages X-Y"
    pattern2 = r'for\s+ages?\s+(\d+)\s*(?:-|to)\s*(\d+)'
    match = re.search(pattern2, text.lower())
    if match:
        return (int(match.group(1)), int(match.group(2)))

    # Pattern 3: "X-Y years old"
    pattern3 = r'(\d+)\s*-\s*(\d+)\s*years?\s+old'
    match = re.search(pattern3, text.lower())
    if match:
        return (int(match.group(1)), int(match.group(2)))

    return None


def check_age_overlap(user_min, user_max, event_min, event_max):
    """
    Check if there's ANY overlap between user's age range and event's age range

    Uses inclusive overlap logic:
    - If ranges overlap at all, return True
    - Examples:
      - User: 3-5, Event: 0-5 → True (overlap on 3-5)
      - User: 3-5, Event: 4-18 → True (overlap on 4-5)
      - User: 0-2, Event: 6-11 → False (no overlap)

    Args:
        user_min, user_max: User's age range
        event_min, event_max: Event's age range

    Returns:
        bool: True if ranges overlap
    """
    return not (user_max < event_min or user_min > event_max)


def filter_by_age(events, age_input):
    """
    Filter events by age range (IMPROVED VERSION)

    Now parses BOTH audience field AND description text for age ranges.
    Uses inclusive matching - if there's ANY overlap, include the event.

    Age matching logic:
    - Parse user input: "0-2" → (0, 2)
    - Check audience field for structured data
    - ALSO parse description for "ages 4-18" patterns
    - Include if ANY overlap exists

    Args:
        events: List of event dictionaries
        age_input: String like "0-2" or "3-5"

    Returns:
        Filtered list of events matching the age range
    """
    # Parse user's age range
    try:
        # Handle formats like "0-2", "3-5", or just "3"
        if '-' in age_input:
            user_min, user_max = map(int, age_input.split('-'))
        else:
            user_min = user_max = int(age_input)
    except ValueError:
        # If we can't parse the age, return all events
        return events

    filtered = []
    for event in events:
        matched = False
        audience = event.get('audience', '').lower()
        description = event.get('description', '')

        # Check for "all ages" first (but only if it's the main age designation)
        # Don't match phrases like "activities for all ages are encouraged"
        if 'all ages' in audience:
            filtered.append(event)
            continue

        # Try to extract age range from description text
        desc_age_range = extract_age_range_from_text(description)
        if desc_age_range:
            event_min, event_max = desc_age_range
            if check_age_overlap(user_min, user_max, event_min, event_max):
                filtered.append(event)
            # If we found age range in description, skip audience field check
            continue

        # Fall back to audience field patterns
        # Extract numbers from audience field (e.g., "0-5" from "Early Childhood (0-5)")
        audience_match = re.search(r'(\d+)\s*-\s*(\d+)', audience)
        if audience_match:
            event_min = int(audience_match.group(1))
            event_max = int(audience_match.group(2))
            if check_age_overlap(user_min, user_max, event_min, event_max):
                filtered.append(event)
                continue

        # Keyword-based fallback (less precise but covers edge cases)
        if 'toddler' in audience and user_max >= 1 and user_min <= 3:
            filtered.append(event)
        elif 'baby' in audience or 'infant' in audience and user_max >= 0 and user_min <= 2:
            filtered.append(event)
        elif 'preschool' in audience and user_max >= 3 and user_min <= 5:
            filtered.append(event)
        # If no age info found anywhere, exclude the event
        # (Better to be strict than show irrelevant events)

    return filtered


def filter_by_days(events, selected_days):
    """
    Filter events by day of week

    User can select which days they're available (Monday, Tuesday, etc.)
    We only show events on those days.

    Args:
        events: List of event dictionaries
        selected_days: List of day names ["Monday", "Wednesday", etc.]

    Returns:
        Filtered list of events on selected days
    """
    if not selected_days:
        return events

    # Normalize day names to match what's in our data
    selected_days_lower = [day.lower() for day in selected_days]

    filtered = []
    for event in events:
        event_day = event.get('day_of_week', '').lower()
        if event_day in selected_days_lower:
            filtered.append(event)

    return filtered


def filter_upcoming_events(events):
    """
    Filter out past events - only show future events

    We compare each event's date to today's date and only include
    events that haven't happened yet.

    Args:
        events: List of event dictionaries

    Returns:
        Filtered list of only upcoming events
    """
    today = datetime.now().date()

    filtered = []
    for event in events:
        try:
            # Parse event date (format: "2025-10-28")
            event_date = datetime.strptime(event.get('date', ''), '%Y-%m-%d').date()

            # Only include if date is today or in the future
            if event_date >= today:
                filtered.append(event)
        except ValueError:
            # If date parsing fails, include the event anyway
            # (better to show too much than miss an event)
            filtered.append(event)

    return filtered


def sort_by_date(events):
    """
    Sort events by date, soonest first

    This helps users see the next upcoming events at the top.

    Args:
        events: List of event dictionaries

    Returns:
        Sorted list of events
    """
    def get_sort_key(event):
        try:
            # Parse date and time for sorting
            date_str = event.get('date', '9999-12-31')
            time_str = event.get('start_time', '00:00:00')
            return datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # If parsing fails, put at the end
            return datetime.max

    return sorted(events, key=get_sort_key)


def filter_by_date_range(events, date_range):
    """
    Filter events by date range preset

    Args:
        events: List of event dictionaries
        date_range: String - 'week' (7 days), '2weeks' (14 days), 'month' (30 days)

    Returns:
        Filtered list of events within the date range
    """
    today = datetime.now().date()

    # Calculate end date based on range
    if date_range == 'week':
        end_date = today + timedelta(days=7)
    elif date_range == '2weeks':
        end_date = today + timedelta(days=14)
    elif date_range == 'month':
        end_date = today + timedelta(days=30)
    else:
        # 'all' or unrecognized - return all events
        return events

    filtered = []
    for event in events:
        try:
            event_date = datetime.strptime(event.get('date', ''), '%Y-%m-%d').date()
            if today <= event_date <= end_date:
                filtered.append(event)
        except ValueError:
            # If date parsing fails, include the event
            filtered.append(event)

    return filtered


def filter_by_time_of_day(events, times):
    """
    Filter events by time of day

    Args:
        events: List of event dictionaries
        times: List of strings - ['morning', 'afternoon', 'evening']

    Returns:
        Filtered list of events matching selected times
    """
    if not times:
        return events

    filtered = []
    for event in events:
        try:
            start_time = event.get('start_time', '00:00:00')
            hour = int(start_time.split(':')[0])

            # Morning: before 12pm, Afternoon: 12pm-5pm, Evening: after 5pm
            is_morning = hour < 12
            is_afternoon = 12 <= hour < 17
            is_evening = hour >= 17

            if ('morning' in times and is_morning) or \
               ('afternoon' in times and is_afternoon) or \
               ('evening' in times and is_evening):
                filtered.append(event)
        except (ValueError, IndexError):
            # If time parsing fails, include the event
            filtered.append(event)

    return filtered


def filter_by_venue_type(events, venue_type):
    """
    Filter events by venue type (library vs bookstore)

    Args:
        events: List of event dictionaries
        venue_type: String - 'library' or 'bookstore'

    Returns:
        Filtered list of events matching the venue type
    """
    if venue_type == 'all':
        return events

    filtered = []
    for event in events:
        event_venue_type = event.get('venue_type', 'library')  # Default to library if not specified
        if event_venue_type == venue_type:
            filtered.append(event)

    return filtered


def filter_by_event_type(events, event_type):
    """
    Filter events by category type

    Args:
        events: List of event dictionaries
        event_type: String - 'storytime', 'arts', 'steam', 'music'

    Returns:
        Filtered list of events matching the type
    """
    if event_type == 'all':
        return events

    # Map event types to category keywords
    type_keywords = {
        'storytime': ['Storytime Events', 'storytime', 'story time'],
        'arts': ['Arts and Crafts', 'arts', 'crafts'],
        'steam': ['S.T.E.A.M', 'STEM', 'steam', 'stem'],
        'music': ['Music and Dance', 'music', 'dance']
    }

    keywords = type_keywords.get(event_type, [])
    if not keywords:
        return events

    filtered = []
    for event in events:
        categories = event.get('categories', [])
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()

        # Check if any keyword matches categories, title, or description
        match = False
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check categories
            if any(keyword_lower in cat.lower() for cat in categories):
                match = True
                break
            # Check title and description as fallback
            if keyword_lower in title or keyword_lower in description:
                match = True
                break

        if match:
            filtered.append(event)

    return filtered


def add_duration_info(events):
    """
    Add duration information to each event

    Calculates duration and adds:
    - duration_hours: Number of hours (float)
    - is_all_day: True if duration >= 6 hours
    - formatted_end_time: Nicely formatted end time (if available)

    Args:
        events: List of event dictionaries

    Returns:
        List of events with duration info added
    """
    for event in events:
        try:
            start_time = event.get('start_time', '00:00:00')
            end_time = event.get('end_time', '')

            if end_time:
                # Parse times
                start_dt = datetime.strptime(start_time, '%H:%M:%S')
                end_dt = datetime.strptime(end_time, '%H:%M:%S')

                # Calculate duration
                duration = end_dt - start_dt
                duration_hours = duration.total_seconds() / 3600

                # Add duration info
                event['duration_hours'] = duration_hours
                event['is_all_day'] = duration_hours >= 6

                # Format end time (e.g., "5:30 PM")
                hour = end_dt.hour
                minute = end_dt.minute
                period = 'AM' if hour < 12 else 'PM'
                display_hour = hour if hour <= 12 else hour - 12
                if display_hour == 0:
                    display_hour = 12
                event['formatted_end_time'] = f"{display_hour}:{minute:02d} {period}"
            else:
                event['duration_hours'] = 0
                event['is_all_day'] = False
                event['formatted_end_time'] = None

        except (ValueError, TypeError):
            # If parsing fails, set defaults
            event['duration_hours'] = 0
            event['is_all_day'] = False
            event['formatted_end_time'] = None

    return events


@app.route('/refresh', methods=['POST'])
def refresh_data():
    """
    Refresh endpoint - reload JSON files without restarting server

    This is useful when you run the update_events.py script to fetch
    new data. Just call this endpoint to reload the data into memory.

    You can trigger this by visiting /refresh in your browser or calling
    it from a script after updating the JSON files.
    """
    load_event_data()
    return jsonify({
        'message': 'Event data refreshed',
        'jersey_city_count': len(jersey_city_events),
        'hoboken_count': len(hoboken_events),
        'bookstore_count': len(bookstore_events)
    })


if __name__ == '__main__':
    """
    Run the Flask development server

    debug=True means:
    - Server auto-restarts when you change code
    - Detailed error messages in browser
    - Don't use debug=True in production!
    """
    print("=" * 50)
    print("Story Time Locator - Starting Server")
    print("=" * 50)

    # Load event data before starting server
    load_event_data()

    total_events = len(jersey_city_events) + len(hoboken_events) + len(bookstore_events)
    print(f"\nTotal events loaded: {total_events}")
    print("\nServer starting...")
    print("Visit http://127.0.0.1:5000 in your browser")
    print("\nTo refresh data after running update_events.py:")
    print("   Visit http://127.0.0.1:5000/refresh")
    print("=" * 50)

    app.run(debug=True, port=5000)
