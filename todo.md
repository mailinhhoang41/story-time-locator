# Story Time Locator - Development Roadmap

**New Approach**: Direct calendar scraping from public libraries and bookstores (no Google Places API or Claude AI needed!)

**Target Areas**: Jersey City & Hoboken, NJ

---

## 📋 Project Overview

### What We're Building
A web app that displays story time events from:
- Jersey City Free Public Library (6 branches)
- Hoboken Public Library
- Local bookstores in both cities

### How It Works
1. **Scrapers** fetch event data from library/bookstore calendars
2. **JSON files** store the combined event data
3. **Flask web app** loads events and filters by user preferences
4. **Frontend** displays filtered results with date/time/location

### No External APIs Needed!
- ✅ No Google Places API
- ✅ No Claude AI API
- ✅ Just web scraping + local data filtering

---

# 🚀 Phase 1: Test Jersey City Library Scraper

**Status**: ⏳ IN PROGRESS (NOT YET TESTED)

**File**: `jc_library_rss_parser.py`

**Goal**: Verify the Jersey City LibCal scraper works and produces valid data

## Tasks

### 1.1 Test the RSS Parser ⏳
- [ ] Run `python jc_library_rss_parser.py`
- [ ] Check console output for errors
- [ ] Verify it fetches events from all 6 branches:
  - [ ] Main Library (ID: 17419)
  - [ ] Marion Branch (ID: 17424)
  - [ ] Lafayette Branch (ID: 17425)
  - [ ] Pavonia/Newport Branch (ID: 17422)
  - [ ] Heights Branch (ID: 17421)
  - [ ] Greenville Branch (ID: 17420)

### 1.2 Validate Output Data
- [ ] Check `jersey_city_storytimes.json` is created
- [ ] Verify JSON structure contains:
  - [ ] title
  - [ ] branch
  - [ ] date (YYYY-MM-DD format)
  - [ ] day_of_week
  - [ ] start_time / formatted_time
  - [ ] location
  - [ ] audience (age range)
  - [ ] description
  - [ ] link (registration URL)
- [ ] Confirm events are actually story time / children's events
- [ ] Check date range covers next 3 months

### 1.3 Debug & Fix Issues
- [ ] Fix any errors found during testing
- [ ] Adjust keyword filters if needed (currently: story, storytime, lap sit, reading, toddler, preschool, baby, children, kids, early childhood, bilingual)
- [ ] Verify RSS feed URLs are working
- [ ] Test with different month ranges if needed

### 1.4 Document Findings
- [ ] Note how many total events found
- [ ] Note how many per branch
- [ ] Identify any branches with no events (possible issues)
- [ ] Document any quirks or special handling needed

---

# 🚀 Phase 2: Hoboken Library Integration

**Status**: 📝 PLANNED (Starts after Phase 1 complete)

**Goal**: Add Hoboken Public Library story time events

## Tasks

### 2.1 Research Hoboken Library System
- [ ] Visit Hoboken Public Library website
- [ ] Find their events/calendar page
- [ ] Identify calendar technology:
  - [ ] Is it LibCal? (like Jersey City)
  - [ ] Custom calendar system?
  - [ ] Third-party service (Evanced, Communico, etc.)?
  - [ ] Static HTML pages?
- [ ] Check if RSS feeds available
- [ ] Check if API available
- [ ] Document calendar URLs

### 2.2 Build Hoboken Parser/Scraper
- [ ] Create `hoboken_library_parser.py`
- [ ] If LibCal: Adapt Jersey City scraper code
- [ ] If different system: Build custom scraper using BeautifulSoup/requests
- [ ] Extract same data fields as Jersey City (title, date, time, audience, etc.)
- [ ] Filter for children's/story time events
- [ ] Save to `hoboken_storytimes.json`

### 2.3 Test Hoboken Parser
- [ ] Run parser/scraper and verify it works
- [ ] Validate JSON output structure
- [ ] Check data quality (dates, times, descriptions)
- [ ] Verify age ranges are captured
- [ ] Test with different date ranges

### 2.4 Combine Data Sources
- [ ] Create `combined_events.json` with both JC and Hoboken
- [ ] Add `city` field to distinguish sources
- [ ] Ensure consistent data schema across both

---

# 🚀 Phase 3: Bookstore Integration

**Status**: 📝 PLANNED (Starts after Phase 2 complete)

**Goal**: Add bookstore story time events from Jersey City and Hoboken

## Tasks

### 3.1 Research Jersey City Bookstores
- [ ] Identify bookstores with children's events:
  - [ ] Barnes & Noble (if in Jersey City)
  - [ ] Independent bookstores
  - [ ] Children's specialty stores
- [ ] Check which ones host story times
- [ ] Find their event calendar pages
- [ ] Document calendar URLs and formats

### 3.2 Research Hoboken Bookstores
- [ ] Identify bookstores with children's events
- [ ] Check for story time programs
- [ ] Find event calendar pages
- [ ] Document URLs

### 3.3 Build Bookstore Scrapers
- [ ] Create `bookstore_scraper.py`
- [ ] Handle different calendar formats per store
- [ ] Extract event data (title, date, time, age range, location)
- [ ] Add `venue_type: "bookstore"` field
- [ ] Save to `bookstore_storytimes.json`

### 3.4 Test Bookstore Scrapers
- [ ] Verify all bookstore calendars scrape correctly
- [ ] Validate data quality
- [ ] Check for story time events specifically
- [ ] Ensure location/address included

### 3.5 Master Data File
- [ ] Create `data/all_storytimes.json` combining:
  - [ ] Jersey City Library events
  - [ ] Hoboken Library events
  - [ ] Bookstore events
- [ ] Add fields to distinguish:
  - [ ] `city`: "Jersey City" or "Hoboken"
  - [ ] `venue_type`: "library" or "bookstore"
  - [ ] `venue_name`: Full name
  - [ ] `branch`: Branch name (if applicable)

---

# 🚀 Phase 4: Web App Rewrite

**Status**: 📝 PLANNED (Starts after Phase 3 complete)

**Goal**: Rewrite Flask app to use scraped calendar data instead of Google Places API

## Tasks

### 4.1 Clean Up Old Code
- [ ] Remove Google Places API code from `app.py`
- [ ] Remove Claude AI integration code
- [ ] Remove geocoding code (not needed initially)
- [ ] Delete test files: `test_api.py`, `test_claude.py`, `test_geocode.py`, etc.
- [ ] Delete obsolete docs: `prompt.md`

### 4.2 Create New Backend (`app.py` rewrite)
- [ ] Load `data/all_storytimes.json` at startup
- [ ] Create `/search` endpoint that filters events by:
  - [ ] City (Jersey City or Hoboken)
  - [ ] Age range (match to event audience)
  - [ ] Day of week
  - [ ] Time of day
  - [ ] Date range (upcoming events only)
  - [ ] Language preferences (if specified)
- [ ] Return filtered JSON results

### 4.3 Update Frontend
- [ ] Simplify form inputs:
  - [ ] City dropdown: "Jersey City" or "Hoboken"
  - [ ] Kids ages: text input or dropdown
  - [ ] Day preference: checkboxes (Mon-Sun, Any)
  - [ ] Time preference: dropdown (Morning, Afternoon, Evening, Any)
  - [ ] Language: optional text input
- [ ] Update JavaScript to display:
  - [ ] Event title
  - [ ] Date and time (formatted nicely)
  - [ ] Location (venue + branch)
  - [ ] Age range
  - [ ] Description
  - [ ] Registration link
- [ ] Add emoji by type (📚 library, 📖 bookstore)

### 4.4 Add Filtering Logic
- [ ] Filter by age range (parse "0-5", "6-11", etc.)
- [ ] Filter by day of week
- [ ] Filter by upcoming dates only (no past events)
- [ ] Sort by date (soonest first)

### 4.5 Testing
- [ ] Test filtering by each preference
- [ ] Test with no filters (show all)
- [ ] Test edge cases (no results, invalid input)
- [ ] Test on mobile browser

---

# 🚀 Phase 5: Polish & Deploy (Optional)

**Status**: 📝 PLANNED

**Goal**: Make production-ready

## Tasks

### 5.1 Auto-Update Script
- [ ] Create `update_events.py` that runs all scrapers
- [ ] Schedule weekly runs (cron job or Task Scheduler)
- [ ] Add error notifications if scraper fails

### 5.2 UI Polish
- [ ] Improve styling
- [ ] Add loading indicators
- [ ] Better error messages
- [ ] Add "no results" state with suggestions

### 5.3 Documentation
- [ ] Update README with new approach
- [ ] Add scraper maintenance guide
- [ ] Document how to add new libraries/bookstores

### 5.4 Optional Deployment
- [ ] Deploy to Render, Railway, or PythonAnywhere
- [ ] Set up automatic scraper runs on server
- [ ] Share with friends/family!

---

# 📊 Progress Tracking

## Overall Status
- ✅ Phase 0: Jersey City RSS parser code written
- ✅ Phase 1: Testing Jersey City RSS parser (COMPLETE)
- ✅ Phase 2: Hoboken library (COMPLETE)
- ✅ Phase 3: Bookstores (COMPLETE - removed due to stale data)
- ✅ Phase 4: Web app rewrite (COMPLETE)
- ✅ Phase 5: Polish & deploy (BASIC VERSION COMPLETE)

## Recent Fixes (Oct 27, 2025)
- ✅ Fixed story time filter to match both "storytime" and "story time" variations
- ✅ Removed bookstore integration (only 1 upcoming event, stale data issue)
- ✅ Fixed UI nesting bug by stripping HTML from event descriptions and titles
- ✅ App fully functional with Jersey City (206 events) and Hoboken (68 events) libraries

## Key Learning Points

### Technical Skills You'll Gain
1. **Web Scraping**: Extracting data from websites using requests & BeautifulSoup
2. **XML/RSS Parsing**: Working with RSS feeds using ElementTree
3. **Data Transformation**: Converting raw data to structured JSON
4. **API Design**: Building REST endpoints that filter/serve data
5. **Frontend Filtering**: Client-side data filtering and display
6. **Automation**: Scheduling scripts to keep data current

### Architecture Understanding
- **Scraper Layer**: Fetch data from external sources
- **Data Layer**: Store in JSON files (later: could migrate to SQLite database)
- **Application Layer**: Flask app loads and filters data
- **Presentation Layer**: HTML/CSS/JS displays results

### Why This Approach is Better
- ✅ No API costs (completely free!)
- ✅ No API rate limits
- ✅ More accurate (direct from source)
- ✅ Faster (no API latency)
- ✅ More reliable (works offline once data is scraped)
- ✅ Learn real web scraping skills

---

# 🎯 Current Focus: Phase 1

**Next Step**: Run `python jc_library_rss_parser.py` and verify it works!

Let's test the Jersey City scraper and see what data we get!
