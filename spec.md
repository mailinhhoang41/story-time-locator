# Story Time Locator - Specification

## Overview
A web app that helps parents find story time sessions at libraries and bookstores in Jersey City and Hoboken, NJ based on their schedule and preferences.

**New Approach**: Direct calendar scraping (no external APIs needed!)

---

## Requirements

### Target Areas
- **Jersey City, NJ**
  - Jersey City Free Public Library (6 branches)
  - Local bookstores
- **Hoboken, NJ**
  - Hoboken Public Library
  - Local bookstores

### User Inputs
1. **City** - Dropdown selection: "Jersey City" or "Hoboken"
2. **Kids Ages** - Text input or dropdown (e.g., "0-2", "3-5", "6-11")
3. **Day Preference** - Checkboxes (Monday-Sunday, Any)
4. **Time Preference** - Dropdown (Morning, Afternoon, Evening, Any)
5. **Language** - Optional text input (e.g., "Spanish", "Bilingual")

### Output Format
Display each story time event with:
- **Title**: Event name with emoji (📚 library, 📖 bookstore)
- **Date & Time**: Formatted (e.g., "Saturday, Oct 28 at 10:30 AM")
- **Location**: Venue name + branch
- **Age Range**: Target audience (e.g., "Ages 0-5")
- **Description**: Event details
- **Link**: Registration/info URL

### Data Sources
1. **Jersey City Free Public Library** (LibCal RSS feeds)
   - Main Library, Marion, Lafayette, Pavonia/Newport, Heights, Greenville
2. **Hoboken Public Library** (calendar system TBD)
3. **Bookstores** (various calendar systems)

---

## Tech Stack

### Data Collection
- **Scrapers**: Python scripts that fetch event data
- **Technologies**:
  - `requests` - HTTP requests to fetch calendar data
  - `xml.etree.ElementTree` - Parse RSS/XML feeds
  - `BeautifulSoup4` - Parse HTML (if needed for bookstores)
- **Data Storage**: JSON files
  - `jersey_city_storytimes.json`
  - `hoboken_storytimes.json`
  - `bookstore_storytimes.json`
  - `data/all_storytimes.json` (combined)

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask (lightweight web server)
- **No External APIs**: All data sourced from local JSON files

### Frontend
- **HTML5** - Form structure
- **CSS3** - Styling (mobile-responsive)
- **Vanilla JavaScript** - Form handling and filtering

### Dependencies
- `flask` - Web server
- `python-dotenv` - Environment variable management (if needed)
- `requests` - HTTP requests for scraping

---

## Architecture

### 1. Scraper Layer
**Purpose**: Fetch story time events from library and bookstore calendars

**Components**:
- `jc_library_rss_parser.py` - Jersey City Library (LibCal RSS feed parser)
- `hoboken_library_parser.py` - Hoboken Library (RSS parser or web scraper, TBD)
- `bookstore_scraper.py` - Bookstore calendars (web scraper)
- `update_events.py` - Master script that runs all parsers/scrapers

**Output**: Individual JSON files per source

### 2. Data Layer
**Purpose**: Store and combine event data

**Schema** (JSON):
```json
{
  "title": "Story Time",
  "city": "Jersey City",
  "venue_type": "library",
  "venue_name": "Jersey City Free Public Library",
  "branch": "Main Library",
  "date": "2025-10-28",
  "day_of_week": "Saturday",
  "start_time": "10:30:00",
  "formatted_time": "10:30 AM",
  "end_time": "11:00:00",
  "location": "PGML - Children's Room",
  "audience": "Early Childhood (0-5)",
  "description": "Join us for stories, songs, and fun!",
  "link": "https://jclibrary.libcal.com/event/12345",
  "categories": ["Children Events", "Storytime Events"]
}
```

**Files**:
- `data/all_storytimes.json` - Combined data from all sources

### 3. Application Layer (Flask)
**Purpose**: Serve web interface and filter events

**Endpoints**:
- `GET /` - Homepage with search form
- `POST /search` - Filter events and return results

**Filtering Logic**:
1. Load `data/all_storytimes.json`
2. Filter by city (if specified)
3. Filter by age range (match to `audience` field)
4. Filter by day of week (match to `day_of_week` field)
5. Filter by time of day (parse `start_time`)
6. Filter by language (search in `title` or `description`)
7. Filter out past events (only show upcoming)
8. Sort by date (soonest first)
9. Return filtered results as JSON

### 4. Presentation Layer
**Purpose**: Display results to user

**Components**:
- `templates/index.html` - Search form and results display
- `static/style.css` - Styling
- `static/script.js` - Handle form submission, API calls, display results

---

## Design Guidelines

### User Experience
- **Simple first**: Single page with form at top, results below
- **Mobile-friendly**: Responsive design, touch-friendly
- **Fast**: Results appear instantly (no API calls, just local filtering)
- **Clear**: Show date, time, location prominently

### Visual Design
- Clean, minimal interface
- Large, readable fonts (16px minimum)
- Color scheme: Warm, family-friendly
- Result cards with clear hierarchy

### Result Cards Format
```
📚 Story Time
Saturday, October 28 at 10:30 AM
Jersey City Library - Main Branch
Ages 0-5

Join us for stories, songs, and fingerplays! Perfect for toddlers
and preschoolers.

📍 472 Jersey Ave, Jersey City | 🔗 Register Online
```

---

## Phases

### Phase 1: Test Jersey City Library RSS Parser
**Goal**: Verify existing RSS parser works
- Test `jc_library_rss_parser.py`
- Validate JSON output
- Fix any bugs

### Phase 2: Hoboken Library Integration
**Goal**: Add Hoboken library events
- Research Hoboken library calendar system
- Build RSS parser or web scraper (depending on what they offer)
- Test and validate

### Phase 3: Bookstore Integration
**Goal**: Add bookstore story times
- Research bookstores in both cities
- Build scrapers for each
- Combine all data sources

### Phase 4: Web App Rewrite
**Goal**: Use scraped data instead of Google Places API
- Remove old API code
- Load events from JSON
- Implement filtering
- Update frontend

### Phase 5: Polish & Deploy (Optional)
**Goal**: Production-ready
- Auto-update script (weekly scraper runs)
- UI improvements
- Documentation
- Deploy to hosting

---

## Key Advantages Over API Approach

### No External APIs Needed
- ✅ **No costs** - Completely free
- ✅ **No rate limits** - Unlimited searches
- ✅ **No API keys** - Simpler setup
- ✅ **More reliable** - No dependency on external services

### Better Data Quality
- ✅ **More accurate** - Direct from source
- ✅ **Complete info** - Full event details, schedules, ages
- ✅ **Up to date** - Run scrapers weekly to refresh

### Faster Performance
- ✅ **Instant results** - Local filtering vs API latency
- ✅ **Works offline** - Once data is scraped
- ✅ **Predictable** - No API failures or timeouts

### Educational Value
- ✅ **Learn web scraping** - Real-world skill
- ✅ **Understand data pipelines** - Scrape → Store → Filter → Display
- ✅ **Practice automation** - Scheduled updates

---

## Technical Learning Points

### Architecture Concepts
1. **Separation of Concerns**: Scrapers, data storage, app logic, presentation
2. **Data Pipeline**: Extract → Transform → Load → Query
3. **Client-Server Model**: Frontend requests → Backend filters → Frontend displays

### Python Skills
1. **XML/RSS Parsing**: Working with structured data feeds
2. **Web Scraping**: Extracting data from websites
3. **JSON**: Reading, writing, manipulating structured data
4. **Date/Time**: Parsing and formatting timestamps

### Web Development
1. **REST API**: Building endpoints that return filtered data
2. **Filtering Logic**: Complex multi-criteria queries
3. **Frontend/Backend Communication**: POST requests with JSON

---

## Next Steps

1. **Test Jersey City RSS parser** (`jc_library_rss_parser.py`)
2. **Research Hoboken library** calendar system
3. **Research bookstores** in both cities
4. **Build remaining scrapers**
5. **Rewrite Flask app** to use JSON data
6. **Update frontend** for new filtering UI
7. **Deploy and share!**
