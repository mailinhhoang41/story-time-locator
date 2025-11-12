"""
Geocode library and bookstore addresses to get lat/lng coordinates
Uses a free geocoding service (Nominatim/OpenStreetMap)
"""
import requests
import json
import time

# All library and bookstore addresses
locations = {
    # Jersey City Libraries
    "Priscilla Gardner Main Library": {
        "address": "472 Jersey Ave, Jersey City, NJ 07302",
        "type": "library",
        "city": "Jersey City"
    },
    "Pavonia Branch": {
        "address": "326 8th Street, Jersey City, NJ",
        "type": "library",
        "city": "Jersey City"
    },
    "Heights Branch": {
        "address": "14 Zabriskie Street, Jersey City, NJ 07307",
        "type": "library",
        "city": "Jersey City"
    },
    "Earl A. Morgan Branch (Greenville)": {
        "address": "1841 Kennedy Boulevard, Jersey City, NJ 07305",
        "type": "library",
        "city": "Jersey City"
    },
    "Five Corners Branch": {
        "address": "678 Newark Ave, Jersey City, NJ 07306",
        "type": "library",
        "city": "Jersey City"
    },
    "Marion Branch": {
        "address": "1017 West Side Avenue, Jersey City, NJ 07306",
        "type": "library",
        "city": "Jersey City"
    },
    "West Bergen Branch": {
        "address": "546 West Side Avenue, Jersey City, NJ",
        "type": "library",
        "city": "Jersey City"
    },
    "Communipaw Branch": {
        "address": "295 Johnston Avenue, Jersey City, NJ 07304",
        "type": "library",
        "city": "Jersey City"
    },
    "Glenn D. Cunningham Branch": {
        "address": "275 Martin Luther King Dr, Jersey City, NJ",
        "type": "library",
        "city": "Jersey City"
    },
    "Miller Branch": {
        "address": "489 Bergen Avenue, Jersey City, NJ",
        "type": "library",
        "city": "Jersey City"
    },
    # Hoboken Library
    "Hoboken Public Library": {
        "address": "500 Park Ave, Hoboken, NJ 07030",
        "type": "library",
        "city": "Hoboken"
    },
    # Bookstores
    "WORD Bookstore": {
        "address": "29 McWilliams Place, Jersey City, NJ",
        "type": "bookstore",
        "city": "Jersey City"
    },
    "Little City Books": {
        "address": "100 Bloomfield St, Hoboken, NJ 07030",
        "type": "bookstore",
        "city": "Hoboken"
    },
    "The Bunny Hive": {
        "address": "1001 Bloomfield St, Hoboken, NJ 07030",
        "type": "play_center",
        "city": "Hoboken"
    },
    "Garden Street School of the Performing Arts": {
        "address": "1018 Washington St, Hoboken, NJ 07030",
        "type": "dance_studio",
        "city": "Hoboken"
    }
}

def geocode_address(address):
    """
    Use Nominatim (OpenStreetMap) to geocode an address
    Free service, no API key needed, but be respectful with rate limits
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'StoryTimeLocator/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()

        if results:
            return {
                'lat': float(results[0]['lat']),
                'lng': float(results[0]['lon'])
            }
        else:
            print(f"  WARNING: No results found for: {address}")
            return None
    except Exception as e:
        print(f"  ERROR geocoding {address}: {e}")
        return None

# Geocode all locations
print("Geocoding addresses...")
print("=" * 50)

for name, info in locations.items():
    print(f"\n{name}")
    print(f"   Address: {info['address']}")

    coords = geocode_address(info['address'])
    if coords:
        info['lat'] = coords['lat']
        info['lng'] = coords['lng']
        print(f"   OK Coordinates: {coords['lat']}, {coords['lng']}")
    else:
        print(f"   FAILED to geocode")

    # Be nice to the free API - wait 1 second between requests
    time.sleep(1)

# Save to JSON file
output_file = 'locations.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(locations, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 50)
print(f"SAVED location data to {output_file}")
print(f"Total locations: {len(locations)}")
