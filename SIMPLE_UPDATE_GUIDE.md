# 📱 Simple Update Guide - Keep Your Live Site Fresh

## ⭐ THE ONLY COMMAND YOU NEED

**To update BOTH your local site AND live site:**

### Windows:
**Double-click:** `update_and_deploy.bat`

### Command Line:
```bash
python update_and_deploy.py
```

**That's it!** This ONE command:
1. ✅ Fetches fresh data from all libraries & bookstores
2. ✅ Updates your local files
3. ✅ Commits to git
4. ✅ Pushes to GitHub
5. ✅ Triggers Render to deploy (auto-happens in 3-5 min)

---

## 📅 Recommended Schedule

**Run `update_and_deploy.bat` once a week:**
- Every Monday morning, OR
- Whatever day works for you

**Why weekly?**
- Libraries add new events regularly
- Keeps your site fresh and useful
- Takes only 2-3 minutes

---

## 🔄 What Happens Behind The Scenes

```
You run update_and_deploy.bat
    ↓
Fetches data from:
├─ Jersey City Libraries
├─ Hoboken Libraries
└─ Bookstores
    ↓
Saves to JSON files on your computer
    ↓
Commits to git
    ↓
Pushes to GitHub
    ↓
Render detects change
    ↓
Render auto-deploys (3-5 min)
    ↓
Live site updated! ✨
```

---

## ⚠️ IMPORTANT: Don't Use Old Scripts!

**DON'T use anymore:**
- ❌ `update_events.bat` (old - only updates local)
- ❌ `update_all_events.py` (old - only updates local)

**USE instead:**
- ✅ `update_and_deploy.bat` (NEW - updates local AND live!)

---

## 🆘 Troubleshooting

**"No changes detected"**
→ Good! Data is already up to date on both local and live site

**"Failed to push to GitHub"**
→ Check your internet connection
→ You may need to enter GitHub credentials

**"Parsers failed"**
→ Check internet connection
→ Library websites might be temporarily down
→ Try again in 10 minutes

**Live site doesn't show new data after 5 minutes**
→ Check Render dashboard for deployment status
→ Clear your browser cache (Ctrl+Shift+R)

---

## 🎯 Remember

**The key difference:**
- **Old way:** Update local, then manually git push (error-prone!)
- **New way:** ONE command does everything automatically! ✨

**Never worry about sync issues again!**

---

Need help? Email: mailinh.hoang41@gmail.com
