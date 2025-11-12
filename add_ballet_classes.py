"""
Add Garden Street Music ballet classes to hoboken_storytimes.json
Generates recurring weekly classes through December 2025
"""
import json
from datetime import datetime, timedelta

# Load existing events
with open('hoboken_storytimes.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

# Ballet class definitions
ballet_classes = [
    {
        "title": "Ballerina Princess (FREE)",
        "day": "Monday",
        "time": "09:30:00",
        "formatted_time": "09:30 AM",
        "duration": 45,  # minutes
        "age": "Ages 2-3"
    },
    {
        "title": "Ballerina Princess (FREE)",
        "day": "Wednesday",
        "time": "09:30:00",
        "formatted_time": "09:30 AM",
        "duration": 45,
        "age": "Walking to 2 years"
    },
    {
        "title": "Ballerina Princess (FREE)",
        "day": "Saturday",
        "time": "08:45:00",
        "formatted_time": "08:45 AM",
        "duration": 45,
        "age": "Ages 2-3"
    },
    {
        "title": "Ballerina Princess (FREE)",
        "day": "Saturday",
        "time": "09:30:00",
        "formatted_time": "09:30 AM",
        "duration": 45,
        "age": "Ages 2-3"
    },
    {
        "title": "Tiny Dancers Ballet - Level 1 (FREE)",
        "day": "Monday",
        "time": "10:30:00",
        "formatted_time": "10:30 AM",
        "duration": 45,
        "age": "Walking to 2 years"
    },
    {
        "title": "Tiny Dancers Ballet - Level 1 (FREE)",
        "day": "Saturday",
        "time": "10:30:00",
        "formatted_time": "10:30 AM",
        "duration": 45,
        "age": "Walking to 2 years"
    },
    {
        "title": "Tiny Dancers Ballet - Level 2 (FREE)",
        "day": "Wednesday",
        "time": "10:30:00",
        "formatted_time": "10:30 AM",
        "duration": 45,
        "age": "Ages 2-3"
    }
]

# Generate dates for remaining November and all of December 2025
start_date = datetime(2025, 11, 13)  # Start from Nov 13
end_date = datetime(2025, 12, 31)

day_name_to_num = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

new_events = []

for ballet_class in ballet_classes:
    target_day = day_name_to_num[ballet_class["day"]]

    # Find all occurrences of this day between start and end
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == target_day:
            # Calculate end time
            start_dt = datetime.strptime(ballet_class["time"], "%H:%M:%S")
            end_dt = start_dt + timedelta(minutes=ballet_class["duration"])

            event = {
                "title": ballet_class["title"],
                "location": "Garden Street School of the Performing Arts",
                "description": f"{ballet_class['day']}, {current_date.strftime('%B %d %Y')} {ballet_class['formatted_time']} - {end_dt.strftime('%I:%M %p').lstrip('0')} \n {ballet_class['age']}. Free drop-in ballet class at Garden Street Music.",
                "link": "https://www.gardenstreetmusic.com/2019-summer-dance-classes",
                "date": current_date.strftime("%Y-%m-%d"),
                "day_of_week": ballet_class["day"],
                "start_time": ballet_class["time"],
                "formatted_time": ballet_class["formatted_time"],
                "datetime": current_date.strftime(f"%a, %d %b %Y {ballet_class['time']} +0000"),
                "organizer": "Garden Street School of the Performing Arts",
                "full_description": f"{ballet_class['age']}. Free drop-in ballet class at Garden Street Music.",
                "audience": ballet_class["age"],
                "categories": ["Dance Classes", "Free Events"]
            }
            new_events.append(event)

        current_date += timedelta(days=1)

print(f"Generated {len(new_events)} ballet class events")

# Merge with existing events and sort by date
all_events = events + new_events
all_events.sort(key=lambda x: x['date'])

# Save back to file
with open('hoboken_storytimes.json', 'w', encoding='utf-8') as f:
    json.dump(all_events, f, indent=2, ensure_ascii=False)

print(f"✅ Added {len(new_events)} ballet classes to hoboken_storytimes.json")
print(f"Total events: {len(all_events)}")
