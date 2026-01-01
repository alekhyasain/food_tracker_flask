# Database Behavior FAQ

## Question: Do daily logs go to database automatically?

**Answer:** It depends on which server you're running:

### ✅ Using `server-db.js` (Database Server)
- **YES**, all meals are saved directly to the database automatically
- When you add/edit/delete meals, they go straight to `database/food_tracker.db`
- No JSON files are updated
- AI assistant works immediately

### ❌ Using `server.js` (Old Server)
- **NO**, meals are saved to `meals.json` (JSON file)
- Database is NOT updated
- AI assistant won't see your new meals
- You must manually migrate to update database

## How to Check Which Server is Running

```bash
# Check running process
ps aux | grep "node server"

# If you see "server-db.js" → Database server ✅
# If you see "server.js" → JSON server ❌
```

## Current Setup (After Migration)

You should be running: **`server-db.js`**

Start it with:
```bash
node server-db.js
```

## What About Browser LocalStorage?

The food tracker ALSO saves data in your browser's localStorage as a backup. This means:

1. **You add a meal** → Saved to localStorage immediately (fast!)
2. **Page loads** → Tries to sync with server
3. **Server-db.js** → Saves to database automatically
4. **AI Assistant** → Reads from database

## Viewing Database Per Day

Instead of Excel export, use the **AI Assistant**:

1. Click the purple AI button (bottom-right)
2. Click **"📋 View All Days"** button
3. See a clean table with:
   - Last 14 days
   - Meals per day
   - Calories, Protein, Carbs, Fat, Fiber

This is much faster and cleaner than Excel!

## Direct Database Queries

You can also query directly:

```bash
# View last 10 days
sqlite3 database/food_tracker.db "SELECT date, meal_count, total_calories, total_protein FROM daily_summary ORDER BY date DESC LIMIT 10;"

# View specific date
sqlite3 database/food_tracker.db "SELECT * FROM meals WHERE date = '2025-12-30';"

# All meals for a date with details
sqlite3 database/food_tracker.db -header -column "SELECT description, meal_type, calories, protein, carbs FROM meals WHERE date = '2025-12-30';"
```

## Export to Excel Issue

The error "body stream already read" happens when trying to read the HTTP response twice. This is a bug in the export code that needs fixing. 

**Workaround:** Use the AI Assistant's "View All Days" feature instead - it's better anyway!

## Summary

✅ **Use:** `node server-db.js`
✅ **View data:** AI Assistant → "📋 View All Days"
✅ **Automatic:** All meals auto-saved to database
✅ **AI works:** Immediately with all data

❌ **Don't use:** `server.js` (old)
❌ **Don't rely on:** Excel export (buggy)
