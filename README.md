# Story Time Locator

A web app that helps parents find story time sessions at libraries and bookstores in Jersey City and Hoboken, NJ based on their location, schedule, and preferences.

**Approach**: Direct RSS feed parsing from public library calendars - no external APIs needed!

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Fetch Event Data

```bash
# Option A: Run individual parsers
python jc_library_rss_parser.py      # Jersey City only
python hoboken_library_rss_parser.py  # Hoboken only

# Option B: Run the master update script (recommended)
python update_events.py
```

This will:
- Fetch events from ALL 12 Jersey City Library calendars (~206 events, 31 days)
- Fetch events from Hoboken Public Library (~68 events, 365 days)
- Filter for children's events (story times + activities)
- Save results to `jersey_city_storytimes.json` and `hoboken_storytimes.json`

### 3. View the Data

**Jersey City** (`jersey_city_storytimes.json`):
- Event title, date, and time
- Actual location (exact branch/room)
- Age range (Early Childhood 0-5, Children 6-11, etc.)
- Full description
- Registration link

**Hoboken** (`hoboken_storytimes.json`):
- Event title, date, and time
- Location (generic "Hoboken Public Library" - click event link for specific branch)
- Full description with organizer details
- Registration link (includes branch information)

### 4. Keep Data Fresh - Weekly Refresh

**Run manually whenever you want updated data:**
```bash
python update_events.py
```

**Or schedule automatically** (see "Automated Weekly Refresh" section below)

---

## Project Structure

```
story-time-locator/
├── jc_library_rss_parser.py        # Jersey City Library RSS parser (all 12 calendars)
├── hoboken_library_rss_parser.py   # Hoboken Public Library RSS parser
├── update_events.py                # Master script to refresh all event data
├── update_events.bat               # Windows batch file for scheduling
├── jersey_city_storytimes.json     # Jersey City event data (~206 events, ~31 days)
├── hoboken_storytimes.json         # Hoboken event data (~68 events, 365 days)
├── requirements.txt                # Python dependencies (flask, python-dotenv, requests)
├── README.md                       # This file
├── spec.md                         # Technical specification
├── todo.md                         # Development roadmap
├── CLAUDE.md                       # Learning notes
└── (Coming soon)
    ├── bookstore_scraper.py        # Bookstore event scraper
    ├── app.py                      # Flask web app
    ├── static/                     # CSS & JavaScript
    └── templates/                  # HTML templates
```

---

## How It Works

### Architecture: RSS Parser → JSON Storage → Web App → User

```
┌──────────────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│ JC Library RSS   │────>│  JSON File  │────>│  Flask   │────>│  User    │
│ (LibCal, 12 cal) │     │  Storage    │     │  App     │     │  Browser │
└──────────────────┘     └─────────────┘     └──────────┘     └──────────┘
┌──────────────────┐            │
│ Hoboken Lib RSS  │────────────┘
│ (Communico, 1)   │
└──────────────────┘
```

**Step 1: RSS Feed Parsers**

*Jersey City (LibCal):*
- Python script connects to Jersey City Library's LibCal RSS feeds
- Fetches from all 12 calendars (Main, Marion, Lafayette, Pavonia, Heights/West Bergen, Greenville, Miller, Communipaw, Cunningham, Five Corners, Bookmobile)
- Filters events by keywords (story, storytime, children, etc.) AND audience field
- Extracts: title, date, time, actual location (branch/room), age range, description, link

*Hoboken (Communico):*
- Python script connects to Hoboken Public Library's Communico RSS feed
- Fetches events for 365 days ahead using base64-encoded parameters
- Filters events by keywords (story, baby, toddler, children, etc.)
- Extracts: title, date, time, organizer, description, link
- **Note**: RSS feed doesn't include specific branch location - users click event link for venue details

**Step 2: JSON Storage**
- Events saved to `jersey_city_storytimes.json` and `hoboken_storytimes.json`
- Jersey City events include actual location field (not calendar name)
- Hoboken events show generic location (specific branch available via event link)
- Data structure ready for web app filtering

**Step 3: Web App (Coming Soon)**
- Flask loads both JSON files
- Filters by: city, age, day of week, time, language
- Provides event links so users can view full details including exact branch location
- Returns filtered results to user

---

## Current Status

### ✅ Phase 1: Jersey City Library - COMPLETE!

**What Works**:
- ✅ All 12 Jersey City library calendars connected
- ✅ RSS feed parsing (not web scraping!)
- ✅ 206+ children's events captured (~31 days rolling window)
- ✅ Correct location mapping (actual venue, not calendar name)
- ✅ 51 story time sessions + 155 other children's activities
- ✅ Weekly refresh capability

**Event Examples Found**:
- Storytime at Main Library - Wednesdays 11:00 AM
- PRE-K Story Hour at Marion - Thursdays 10:30 AM
- Story Time at Pavonia - Tuesdays/Thursdays
- Story Hour with Miss Sheena at West Bergen - Wednesdays 10:00 AM
- Little Mover's Storytime at Five Corners - Tuesdays 11:00 AM
- Storytime with Peanut at Miller Branch - Saturdays
- Special Spanish Story Time with Maria Conde at Communipaw
- Fall Storytime at Biblioteca Criolla (bilingual) - Mondays 10:15 AM

### ✅ Phase 2: Hoboken Public Library - COMPLETE!

**What Works**:
- ✅ Hoboken Public Library RSS feed connected (Communico system)
- ✅ RSS feed parsing with base64-encoded parameters
- ✅ 68+ children's events captured (365 days ahead - full year!)
- ✅ Event links included for users to view specific branch locations
- ✅ Weekly refresh capability

**Event Examples Found**:
- Toddler Story Time - Wednesdays 10:30 AM
- Baby Story Time - Thursdays 12:00 PM
- Bilingual Story Time - Tuesdays 3:30 PM
- Yoga Story Time - Select Wednesdays 10:30 AM
- Baby Music Class - Select Mondays 12:00 PM
- After School Story Time - Various days
- Therapy Dog Story Time - Special events
- Sensory Play Time - Monthly sessions

**Known Limitation**:
- ⚠️ Hoboken RSS feed doesn't include specific branch location (shows generic "Hoboken Public Library")
- ✅ Solution: Event links provided - users click to view venue details on library website

### 📝 Coming Next
- Phase 3: Bookstores (Jersey City & Hoboken)
- Phase 4: Web app to filter and display events
- Phase 5: Deploy online

---

## Data Sources

### Jersey City Free Public Library ✅
- **System**: LibCal (Springshare)
- **Method**: RSS feed parsing (official feeds)
- **All 12 Calendars**:
  1. Priscilla Gardner Main Library (17419)
  2. Earl A. Morgan Branch/Greenville (17420)
  3. West Bergen Branch (17421) - Temporary location for Heights events
  4. Pavonia Branch (17422)
  5. Miller Branch (17423)
  6. Marion Branch (17424)
  7. Lafayette Branch (17425)
  8. Heights Branch (17426) - Closed for renovation
  9. Glenn D. Cunningham Branch (17427)
  10. Five Corners Branch (17430)
  11. Bookmobile (17432)
  12. Communipaw Branch (19967)
- **RSS URL Pattern**: `https://jclibrary.libcal.com/rss.php?cid={id}&m=month`
- **Date Range**: ~31 days rolling window (LibCal limitation)

### Hoboken Public Library ✅
- **System**: Communico
- **Method**: RSS feed parsing (official feed with base64-encoded parameters)
- **RSS URL Pattern**: `https://hobokenlibrary.libnet.info/feeds?data={base64_encoded_json}`
- **Date Range**: 365 days (full year ahead!)
- **Events Captured**: 68+ children's story time and activity events
- **Location Details**: RSS feed shows generic "Hoboken Public Library" - specific branch available via event link
- **Parameters**: `{"feedType": "rss", "filters": {"location": ["all"], "ages": ["all"], "types": ["all"], "days": 365}}`

### Bookstores 📝
- **Status**: To be researched (Phase 3)

---

## Automated Weekly Refresh

To keep your event data current, run the update script weekly.

### Option A: Manual Running

Double-click `update_events.bat` or run:
```bash
python update_events.py
```

### Option B: Windows Task Scheduler (Automated)

**Set up once, runs automatically every week:**

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create Basic Task**
   - Click "Create Basic Task" in right panel
   - Name: `Story Time Locator - Weekly Refresh`
   - Description: `Updates event data from Jersey City and Hoboken libraries`

3. **Set Trigger**
   - Choose "Weekly"
   - Select day: Monday (or your preference)
   - Time: 6:00 AM (before you check for events)
   - Click Next

4. **Set Action**
   - Choose "Start a program"
   - Program/script: Browse to `update_events.bat`
   - Click Next, then Finish

5. **Test It**
   - Right-click your new task → "Run"
   - Check that `jersey_city_storytimes.json` and `hoboken_storytimes.json` get updated

**Now your event data will refresh automatically every week!**

---

## Why This Approach?

### No External APIs Needed
- ✅ **Completely free** - No API costs
- ✅ **No rate limits** - Use official RSS feeds
- ✅ **No API keys** - Simpler setup
- ✅ **More reliable** - Direct from library system

### Better Data Quality
- ✅ **Direct from source** - Most accurate event info
- ✅ **Complete details** - Full schedules, age ranges (JC), descriptions, registration links
- ✅ **Always current** - Run weekly to refresh (31 days for JC, 365 days for Hoboken)

### Faster Performance
- ✅ **Instant results** - Local data filtering vs API calls
- ✅ **Works offline** - Once data is scraped
- ✅ **Predictable** - No API timeouts or failures

### Educational Value
- ✅ **Learn RSS parsing** - Practical, in-demand skill
- ✅ **Understand data pipelines** - Fetch → Parse → Store → Filter → Display
- ✅ **Practice automation** - Scheduled updates

---

## Tech Stack

### Data Collection
- **requests** - HTTP requests to fetch RSS feeds
- **xml.etree.ElementTree** - Parse RSS/XML feeds
- **BeautifulSoup4** - Parse HTML (for future bookstore scraping)

### Backend
- **Flask** - Lightweight Python web framework (coming soon)
- **JSON** - Data storage format

### Frontend (Coming Soon)
- **HTML5/CSS3** - Structure and styling
- **Vanilla JavaScript** - Form handling and display

### Dependencies
```
flask
python-dotenv
requests
```

---

## Key Technical Details

### RSS Feed Systems Comparison

**Jersey City (LibCal)**:
- **Parameters**: `m=month` (gives ~31 days of events)
- **Doesn't work**: `months=12`, `days=365`, `start/end` dates
- **Limitation**: LibCal RSS only supports 1 month rolling window
- **Location Field**: Has `<libcal:location>` with actual venue/room
- **Age Field**: Has `<libcal:audience>` (Early Childhood 0-5, Children 6-11, etc.)

**Hoboken (Communico)**:
- **Parameters**: Base64-encoded JSON with `days` parameter (supports up to 365!)
- **Date Range**: Full year ahead (365 days)
- **Limitation**: No specific branch location in RSS feed (generic "Hoboken Public Library")
- **Workaround**: Event links provided - users click to view venue details on library website

### Location Mapping (Jersey City)
- **Calendar ID ≠ Physical Location**
- We use `<libcal:location>` field (actual venue) not calendar name
- Example: Heights calendar (17426) is closed, events show at West Bergen (actual location)

### Event Filtering
- **Keywords**: story, storytime, lap sit, reading, toddler, preschool, baby, children, kids, early childhood, bilingual, little, movers
- **Jersey City Audience Field**: Early Childhood (0-5), Children (6-11)
- **Results**:
  - Jersey City: 51 story times + 155 other children's activities = 206 total events
  - Hoboken: 68 story time and children's activity events

---

## Development Workflow

### Update Event Data
```bash
# Manual refresh (run anytime) - updates both cities
python update_events.py

# Or run individual parsers
python jc_library_rss_parser.py       # Jersey City only
python hoboken_library_rss_parser.py  # Hoboken only
```

### Testing (Coming Soon)
```bash
# Start Flask development server
python app.py

# Visit in browser
http://127.0.0.1:5000
```

---

## Next Steps

See `todo.md` for the complete development roadmap.

**Current**: Phase 1 & 2 Complete ✅ (Jersey City & Hoboken)
**Next**: Phase 3 - Bookstores

**To run right now**:
```bash
python update_events.py
```

Then check the JSON files:
- `jersey_city_storytimes.json` - 206+ events (31 days)
- `hoboken_storytimes.json` - 68+ events (365 days)

---

## Contributing

This is a personal learning project, but suggestions are welcome!

Focus areas:
- Finding bookstores with story times in Jersey City and Hoboken
- Building the Flask web app with filtering
- UI/UX improvements
- Handling Hoboken location details (potential web scraping for branch info)

---

## License

MIT - Feel free to use and modify for your own area!

---

## Questions?

Check out:
- `todo.md` - Development roadmap and detailed tasks
- `spec.md` - Technical specification and architecture
- `CLAUDE.md` - Learning notes and tips for becoming more technical
