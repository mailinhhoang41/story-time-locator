# How to Refresh Event Data

Your Story Time Locator pulls data from library RSS feeds and bookstore websites. This data gets stale over time as new events are added. Here are **4 ways** to refresh the data:

---

## ⭐ Option 1: Double-Click the Batch File (EASIEST - Windows Only)

1. **Double-click** `update_events.bat` in this folder
2. Wait for it to finish (usually 30-60 seconds)
3. Done! Data is refreshed

**When to use:** This is the easiest option if you're on Windows. Just double-click whenever you want fresh data (recommended: weekly).

---

## Option 2: Run the Python Script

1. Open a terminal/command prompt
2. Navigate to this folder:
   ```bash
   cd "C:\Users\maili\OneDrive\Desktop\Story Time Locator"
   ```
3. Run the update script:
   ```bash
   python update_all_events.py
   ```
4. Wait for it to finish
5. Done! Data is refreshed

**When to use:** Works on any operating system (Windows, Mac, Linux). Great if you want to see detailed output.

---

## Option 3: Use the /refresh Endpoint (Server Must Be Running)

If the Flask server is already running at http://127.0.0.1:5000:

1. **FIRST**, run the parsers to fetch new data:
   ```bash
   python jc_library_rss_parser.py
   python hoboken_library_rss_parser.py
   python bookstore_scraper.py
   ```

2. **THEN**, refresh the server:
   - Open your browser and visit: http://127.0.0.1:5000/refresh
   - OR use curl: `curl -X POST http://127.0.0.1:5000/refresh`

**When to use:** When the server is already running and you've updated the JSON files manually.

---

## Option 4: Restart the Server

1. Stop the Flask server (Ctrl+C in the terminal)
2. Run the parsers to fetch new data (if you haven't already):
   ```bash
   python jc_library_rss_parser.py
   python hoboken_library_rss_parser.py
   python bookstore_scraper.py
   ```
3. Start the server again:
   ```bash
   python app.py
   ```

**When to use:** When you've made code changes to app.py or want a fresh start.

---

## 📅 Recommended Schedule

**How often should you refresh?**
- **Weekly**: Ideal for keeping data current without too much effort
- **After holidays**: Libraries often add special events after holidays
- **When you notice missing events**: If someone mentions an event that's not showing up

---

## 🔍 What Gets Updated?

When you refresh data, these files are updated:
- `jersey_city_storytimes.json` - Jersey City Library events
- `hoboken_storytimes.json` - Hoboken Library events
- `bookstore_storytimes.json` - Bookstore events (Little City Books + WORD)

---

## ⚙️ Technical Notes

**How it works:**
1. The parsers fetch data from RSS feeds/websites
2. They save the data to JSON files
3. Flask loads these JSON files into memory
4. The `/refresh` endpoint reloads the JSON files without restarting the server

**Why do I need to refresh?**
- Libraries add new events to their calendars regularly
- Past events get filtered out automatically
- Bookstore schedules can change

**Can I automate this?**
Yes! You can set up a Windows Task Scheduler job to run `update_all_events.py` weekly. Or use a cron job on Mac/Linux.

---

## 🚨 Troubleshooting

**"Server is not running" warning:**
- This is normal if the Flask server isn't started
- Your data files are still updated!
- Just start the server with `python app.py` and it will load the fresh data

**Parser errors:**
- Check your internet connection
- Library websites might be down temporarily
- Try running the individual parser again

**No new events showing up:**
- Make sure you refreshed the server AFTER running the parsers
- Check that the JSON files have recent timestamps
- Try restarting the server completely (Option 4)

---

Need help? Check the main README or ask for assistance!
