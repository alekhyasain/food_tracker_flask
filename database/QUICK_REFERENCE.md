# Food Tracker - Quick Reference Card

## 🚀 Quick Start

```bash
# Setup (one-time)
./database/setup-db.sh

# Start server
node server-db.js

# Open browser
http://localhost:3000
```

## 📂 Key Files

| File | Purpose |
|------|---------|
| `server-db.js` | Database-enabled server (USE THIS) |
| `server.js` | Original JSON server (legacy) |
| `database/food_tracker.db` | SQLite database |
| `database/migrate.js` | Migration script |
| `food_tracker.html` | Frontend (with AI assistant) |

## 🔄 Migration Commands

```bash
# First time setup
npm install
node database/migrate.js
node server-db.js

# Re-migrate (overwrites database)
rm database/food_tracker.db
node database/migrate.js
```

## 🤖 AI Assistant - Quick Actions

| Button | What It Does |
|--------|--------------|
| 📊 Today's Analysis | Analyzes current day's nutrition |
| 📈 Weekly Progress | Shows 7-day averages & trends |
| 💡 Tips | Random nutrition tips |

## 🗄️ Database Tables

```
categories → ingredients → ingredient_measurements
recipes → recipe_nutrition
recipes → recipe_ingredients
meals → daily_summary (auto-updated)
```

## 🔌 API Endpoints (New)

```javascript
// AI Analysis
POST /api/ai/analyze
Body: { date: "2025-12-31" }

// Weekly Progress
POST /api/ai/weekly-progress

// Compare Periods
POST /api/ai/compare
Body: { currentStartDate: "...", currentEndDate: "..." }

// Get Recommendations
POST /api/ai/recommendations
Body: { deficientNutrients: ["protein", "fiber"] }

// Daily Summary
GET /api/analytics/daily/:date

// Weekly Summary
GET /api/analytics/weekly?startDate=...&endDate=...

// Health Check
GET /api/health
```

## 💾 Backup & Restore

```bash
# Backup
cp database/food_tracker.db database/backup_$(date +%Y%m%d).db

# Restore
cp database/backup_20251231.db database/food_tracker.db

# Revert to JSON (emergency)
node server.js  # Use old server
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Database not found | Run `node database/migrate.js` |
| Port 3000 in use | `PORT=3001 node server-db.js` |
| AI not working | Check meals exist for date |
| Migration fails | Check JSON files exist |
| Old data showing | Clear browser cache |

## 📊 Performance Tips

✅ Database is indexed - queries are fast
✅ Daily summaries auto-calculated
✅ Use date range queries for analytics
✅ AI analysis is real-time

## 🎯 Common Tasks

### Add New Ingredient
1. Use existing UI (Manage Ingredients)
2. Or POST to `/api/ingredients`

### View Nutrition Stats
1. Click AI button (purple)
2. Click "Today's Analysis"

### Export Data
1. Use Export feature in UI
2. Or query database directly:
   ```bash
   sqlite3 database/food_tracker.db
   .mode csv
   .output meals.csv
   SELECT * FROM meals WHERE date >= '2025-01-01';
   ```

### Check Database Health
```bash
# View table info
sqlite3 database/food_tracker.db ".tables"

# Count records
sqlite3 database/food_tracker.db "SELECT COUNT(*) FROM meals;"

# View recent meals
sqlite3 database/food_tracker.db "SELECT date, description FROM meals ORDER BY date DESC LIMIT 10;"
```

## 🔐 Data Safety

✅ Original JSON files untouched
✅ Database has foreign key constraints
✅ Triggers maintain data consistency
✅ Transaction support (ACID)
✅ Can backup anytime

## 📱 Access Points

| What | Where |
|------|-------|
| Web UI | http://localhost:3000 |
| API Base | http://localhost:3000/api |
| Database | ./database/food_tracker.db |
| Logs | Console output |
| Docs | database/README.md |

## 🎨 UI Features

**AI Assistant:**
- Purple floating button (bottom-right)
- Chat-style interface
- Quick actions
- Color-coded messages:
  - 🟣 Purple = Assistant
  - 🟢 Green = Success
  - 🟡 Yellow = Warning
  - 🔵 Blue = Info

## 🔧 Development

```bash
# Watch mode (if nodemon installed)
npx nodemon server-db.js

# Direct database queries
sqlite3 database/food_tracker.db

# View schema
sqlite3 database/food_tracker.db ".schema"

# Database size
du -h database/food_tracker.db
```

## 📞 Need Help?

1. Check console for errors
2. Read database/README.md
3. View database/IMPLEMENTATION_SUMMARY.md
4. Check server logs

## ✅ Verification Checklist

After setup, verify:
- [ ] Server starts without errors
- [ ] Website loads at localhost:3000
- [ ] Existing meals visible
- [ ] Can add new meal
- [ ] AI button appears (purple, bottom-right)
- [ ] AI analysis works
- [ ] No console errors

## 🎉 You're All Set!

Your Food Tracker now has:
- ✅ Fast SQLite database
- ✅ AI nutrition insights
- ✅ Better performance
- ✅ Same familiar interface

Enjoy tracking with intelligence! 🚀
