# Food Tracker - Python/Flask Version

A comprehensive food tracking application converted from Node.js/JavaScript to Python/Flask.

## Features

- 🥗 **Ingredient Management**: Track raw ingredients with nutritional information
- 🍳 **Recipe Management**: Create and manage recipes with calculated nutrition
- 📊 **Meal Logging**: Log daily meals and track nutrition intake
- 📈 **Analytics**: Daily and weekly nutrition summaries
- 🤖 **AI Assistant**: Get personalized nutrition advice using Google Gemini AI
- 🔌 **REST API**: Full-featured Flask REST API
- 💻 **CLI Tool**: Command-line interface for all operations

## Installation

### Prerequisites

- Python 3.8 or higher
- SQLite3 (usually comes with Python)
- (Optional) Google Gemini API key for AI features

### Setup

1. Run the setup script:
```bash
chmod +x setup_python.sh
./setup_python.sh
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. (Optional) Set your Gemini API key:
```bash
export GEMINI_API_KEY='your_api_key_here'
```

## Usage

### Option 1: Flask API Server

Start the server:
```bash
python app.py
```

The API will be available at `http://localhost:3000`

### Option 2: Command-Line Interface

The CLI provides full access to all features without needing the web server.

#### View Help
```bash
python cli.py --help
```

#### Add a Meal
```bash
python cli.py add-meal "Oatmeal with banana" breakfast --calories 350 --protein 10 --carbs 60 --fat 8 --fiber 8
```

#### List Today's Meals
```bash
python cli.py list-meals
```

#### List Meals for Specific Date
```bash
python cli.py list-meals --date 2026-01-01
```

#### View Daily Summary
```bash
python cli.py summary
```

#### View Weekly Summary
```bash
python cli.py weekly
```

#### Get AI Analysis
```bash
python cli.py analyze
```

#### Get Food Recommendations
```bash
python cli.py recommend protein,fiber
```

#### Copy Meals from One Day to Another
```bash
python cli.py copy-meals 2026-01-01 2026-01-02
```

#### List Ingredients
```bash
python cli.py list-ingredients
```

#### Add Ingredient
```bash
python cli.py add-ingredient "Grains" "brown_rice" "Brown Rice" "cup_cooked" 215 5 45 1.8 3.5
```

#### List Recipes
```bash
python cli.py list-recipes
```

#### Export Data
```bash
python cli.py export backup.json
python cli.py export meals.json --type meals
```

#### Import Data
```bash
python cli.py import backup.json
```

## API Endpoints

### Ingredients
- `GET /api/ingredients` - Get all ingredients
- `POST /api/ingredients` - Add new ingredient
- `PUT /api/ingredients/:category/:key` - Update ingredient
- `DELETE /api/ingredients/:category/:key` - Delete ingredient
- `GET /api/categories` - Get all categories

### Recipes
- `GET /api/recipes` - Get all recipes
- `POST /api/recipes` - Add new recipe
- `PUT /api/recipes/:key` - Update recipe
- `DELETE /api/recipes/:key` - Delete recipe

### Meals
- `GET /api/meals?date=YYYY-MM-DD` - Get meals by date
- `GET /api/meals?startDate=...&endDate=...` - Get meals by date range
- `POST /api/meals` - Add new meal
- `PUT /api/meals/:id` - Update meal
- `DELETE /api/meals/:id` - Delete meal
- `POST /api/meals/copy` - Copy meals between dates
- `DELETE /api/meals/by-date/:date` - Delete all meals for a date

### Analytics
- `GET /api/analytics/daily/:date` - Get daily summary
- `GET /api/analytics/weekly?startDate=...&endDate=...` - Get weekly summary

### AI Assistant
- `POST /api/ai/chat` - Chat with AI assistant
- `POST /api/ai/analyze` - Get nutrition analysis
- `POST /api/ai/weekly-progress` - Get weekly progress
- `POST /api/ai/compare` - Compare periods
- `POST /api/ai/recommendations` - Get food recommendations

### Health Check
- `GET /api/health` - Check server status

## Database

The application uses SQLite database located at `./database/food_tracker.db`. The database schema includes:

- `categories` - Ingredient categories
- `ingredients` - Raw ingredients
- `ingredient_measurements` - Nutritional data for ingredients
- `recipes` - Recipe definitions
- `recipe_nutrition` - Recipe nutritional totals
- `recipe_ingredients` - Recipe ingredient lists
- `meals` - Daily meal logs
- `daily_summary` - Cached daily nutrition summaries

## Project Structure

```
.
├── app.py                  # Flask REST API server
├── db_service.py          # Database service layer
├── ai_assistant.py        # AI assistant service
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── setup_python.sh       # Setup script
├── README_PYTHON.md      # This file
└── database/
    ├── food_tracker.db   # SQLite database
    └── schema.sql        # Database schema
```

## Differences from Node.js Version

1. **No HTML/JavaScript**: This version is pure Python backend
2. **CLI Interface**: Full command-line tool for all operations
3. **Flask instead of Express**: Using Flask web framework
4. **Same Database**: Compatible with existing SQLite database
5. **Same API**: REST API endpoints match the original

## Tips

1. **Daily Tracking**: Use the CLI to quickly log meals throughout the day
2. **Regular Analysis**: Run `python cli.py analyze` daily to get insights
3. **Export Backups**: Regularly export your data with `python cli.py export`
4. **Use Both**: Run the API server for integrations, use CLI for quick access

## Troubleshooting

### Import Errors
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### Database Not Found
The database should exist at `./database/food_tracker.db`. If using a new installation, you may need to migrate your existing database or run the database setup script.

### AI Features Not Working
Set your Gemini API key:
```bash
export GEMINI_API_KEY='your_api_key_here'
```

## License

Same as the original project.
