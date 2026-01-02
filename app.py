"""
Flask Food Tracker API
A REST API for tracking food intake, nutrition, and recipes
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import google.generativeai as genai
from db_service import DatabaseService
from ai_assistant import AIAssistantService
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure max request size
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
gemini_model = None

if GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_API_KEY_HERE':
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-pro')
        print('✅ Gemini AI initialized')
    except Exception as error:
        print(f'❌ Failed to initialize Gemini AI: {error}')
        gemini_model = None
else:
    print('⚠️  Gemini API key not set. AI chat will use fallback responses.')
    print('   Set GEMINI_API_KEY environment variable to enable AI chat.')

# Initialize database service
db = DatabaseService()
ai_assistant = AIAssistantService(db)

# Database connection flag
db_connected = False


def initialize_database():
    """Initialize database connection"""
    global db_connected
    try:
        db.connect()
        db_connected = True
        print('✅ Database service initialized')
    except Exception as error:
        print(f'❌ Failed to initialize database: {error}')
        db_connected = False
        raise


def require_db():
    """Middleware to check database connection"""
    if not db_connected:
        return jsonify({'error': 'Database not available'}), 503
    return None


# ============= STATIC FILES & WEB INTERFACE =============

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'food_tracker.html')

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Food Tracker API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'ingredients': '/api/ingredients',
            'recipes': '/api/recipes',
            'meals': '/api/meals',
            'analytics': '/api/analytics',
            'ai': '/api/ai',
            'download_db': '/api/download-db'
        },
        'status': 'running'
    })

@app.route('/api/download-db')
def download_database():
    """Download the database file"""
    try:
        return send_from_directory('./database', 'food_tracker.db', 
                                   as_attachment=True,
                                   download_name=f'food_tracker_{datetime.now().strftime("%Y%m%d")}.db')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    """Return 204 for favicon requests"""
    return '', 204

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (if any exist)"""
    try:
        return send_from_directory('.', filename)
    except:
        return jsonify({'error': 'File not found'}), 404


# ============= INGREDIENTS API =============

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Get all ingredients"""
    check = require_db()
    if check:
        return check
    
    try:
        ingredients = db.get_all_ingredients()
        return jsonify(ingredients)
    except Exception as error:
        print(f'Error reading ingredients: {error}')
        return jsonify({'error': 'Failed to read ingredients'}), 500


@app.route('/api/ingredients', methods=['POST'])
def add_ingredient():
    """Add a new ingredient"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        category = data.get('category')
        ingredient_key = data.get('ingredientKey')
        ingredient_data = data.get('ingredientData')
        
        if not category or not ingredient_key or not ingredient_data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not ingredient_data.get('name') or not ingredient_data.get('measurements'):
            return jsonify({'error': 'Invalid ingredient data'}), 400
        
        db.add_ingredient(category, ingredient_key, ingredient_data)
        
        return jsonify({
            'success': True,
            'message': f'Ingredient "{ingredient_data["name"]}" added successfully'
        })
    except Exception as error:
        print(f'Error adding ingredient: {error}')
        error_msg = str(error).lower()
        
        if 'ingredient already exists' in error_msg:
            # Upsert: merge measurements into existing ingredient
            try:
                existing = db.get_ingredient(category, ingredient_key)
                if not existing:
                    return jsonify({'error': 'Ingredient exists but could not be retrieved'}), 500
                
                merged = {**existing.get('measurements', {}), **ingredient_data.get('measurements', {})}
                db.update_ingredient(category, ingredient_key, {
                    'name': ingredient_data.get('name', existing['name']),
                    'measurements': merged
                })
                return jsonify({
                    'success': True,
                    'message': 'Ingredient updated with new measurements (merged)'
                })
            except Exception as merge_err:
                print(f'Error merging measurements on duplicate add: {merge_err}')
                return jsonify({'error': str(merge_err) or 'Failed to merge measurements'}), 500
        
        return jsonify({'error': str(error) or 'Failed to add ingredient'}), 500


@app.route('/api/ingredients/<category>/<ingredient_key>', methods=['PUT'])
def update_ingredient(category, ingredient_key):
    """Update an existing ingredient"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        ingredient_data = data.get('ingredientData')
        
        if not ingredient_data or not ingredient_data.get('name') or not ingredient_data.get('measurements'):
            return jsonify({'error': 'Invalid ingredient data'}), 400
        
        db.update_ingredient(category, ingredient_key, ingredient_data)
        
        return jsonify({
            'success': True,
            'message': f'Ingredient "{ingredient_data["name"]}" updated successfully'
        })
    except Exception as error:
        print(f'Error updating ingredient: {error}')
        return jsonify({'error': str(error) or 'Failed to update ingredient'}), 500


@app.route('/api/ingredients/<category>/<ingredient_key>', methods=['DELETE'])
def delete_ingredient(category, ingredient_key):
    """Delete an ingredient"""
    check = require_db()
    if check:
        return check
    
    try:
        result = db.delete_ingredient(category, ingredient_key)
        
        return jsonify({
            'success': True,
            'message': f'Ingredient "{result["name"]}" deleted successfully'
        })
    except Exception as error:
        print(f'Error deleting ingredient: {error}')
        return jsonify({'error': str(error) or 'Failed to delete ingredient'}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all ingredient categories"""
    check = require_db()
    if check:
        return check
    
    try:
        categories = db.get_categories()
        return jsonify({'categories': categories})
    except Exception as error:
        print(f'Error reading categories: {error}')
        return jsonify({'error': 'Failed to read categories'}), 500


# ============= RECIPES API =============

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes"""
    check = require_db()
    if check:
        return check
    
    try:
        recipes = db.get_all_recipes()
        return jsonify(recipes)
    except Exception as error:
        print(f'Error reading recipes: {error}')
        return jsonify({'error': 'Failed to read recipes'}), 500


@app.route('/api/recipes', methods=['POST'])
def add_recipe():
    """Add a new recipe"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        recipe_key = data.get('recipeKey')
        recipe_data = data.get('recipeData')
        
        if not recipe_key or not recipe_data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not recipe_data.get('name') or not recipe_data.get('total_per_serving'):
            return jsonify({'error': 'Invalid recipe data'}), 400
        
        db.add_recipe(recipe_key, recipe_data)
        
        return jsonify({
            'success': True,
            'message': f'Recipe "{recipe_data["name"]}" added successfully'
        })
    except Exception as error:
        print(f'Error adding recipe: {error}')
        return jsonify({'error': 'Failed to add recipe'}), 500


@app.route('/api/recipes/<key>', methods=['PUT'])
def update_recipe(key):
    """Update an existing recipe"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        recipe_data = data.get('recipeData')
        
        if not recipe_data or not recipe_data.get('name') or not recipe_data.get('total_per_serving'):
            return jsonify({'error': 'Invalid recipe data'}), 400
        
        db.update_recipe(key, recipe_data)
        
        return jsonify({
            'success': True,
            'message': f'Recipe "{recipe_data["name"]}" updated successfully'
        })
    except Exception as error:
        print(f'Error updating recipe: {error}')
        return jsonify({'error': str(error) or 'Failed to update recipe'}), 500


@app.route('/api/recipes/<key>', methods=['DELETE'])
def delete_recipe(key):
    """Delete a recipe"""
    check = require_db()
    if check:
        return check
    
    try:
        result = db.delete_recipe(key)
        
        return jsonify({
            'success': True,
            'message': f'Recipe "{result["name"]}" deleted successfully'
        })
    except Exception as error:
        print(f'Error deleting recipe: {error}')
        return jsonify({'error': str(error) or 'Failed to delete recipe'}), 500


# ============= MEALS API =============

@app.route('/api/meals', methods=['GET'])
def get_meals():
    """Get meals by date or date range"""
    check = require_db()
    if check:
        return check
    
    try:
        date = request.args.get('date')
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        if date:
            meals = db.get_meals_by_date(date)
            return jsonify(meals)
        elif start_date and end_date:
            meals = db.get_meals_by_date_range(start_date, end_date)
            return jsonify(meals)
        else:
            # Return recent meals (last 30 days)
            from datetime import date as dt, timedelta
            end = dt.today()
            start = end - timedelta(days=30)
            meals = db.get_meals_by_date_range(start.isoformat(), end.isoformat())
            return jsonify(meals)
    except Exception as error:
        print(f'Error reading meals: {error}')
        return jsonify({'error': 'Failed to read meals'}), 500


@app.route('/api/meals', methods=['POST'])
def add_meal():
    """Add a new meal"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        date = data.get('date')
        meal = data.get('meal')
        
        if not date or not meal:
            return jsonify({'error': 'Missing required fields: date, meal'}), 400
        
        if not meal.get('id') or not meal.get('description') or not meal.get('nutrition'):
            return jsonify({'error': 'Invalid meal data'}), 400
        
        meal['date'] = date
        if not meal.get('timestamp'):
            meal['timestamp'] = datetime.now().isoformat()
        
        # Try to add meal, but if it already exists (duplicate ID), skip it silently
        try:
            db.add_meal(meal)
            return jsonify({
                'success': True,
                'message': f'Meal "{meal["description"]}" added successfully',
                'meal': meal,
                'date': date
            })
        except Exception as db_error:
            # If it's a UNIQUE constraint error, the meal already exists - return success
            if 'UNIQUE constraint failed' in str(db_error):
                return jsonify({
                    'success': True,
                    'message': f'Meal "{meal["description"]}" already exists',
                    'meal': meal,
                    'date': date,
                    'alreadyExists': True
                })
            else:
                raise db_error
    except Exception as error:
        print(f'Error adding meal: {error}')
        return jsonify({'error': 'Failed to add meal'}), 500


@app.route('/api/meals/<int:meal_id>', methods=['PUT'])
def update_meal(meal_id):
    """Update an existing meal"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        date = data.get('date')
        meal = data.get('meal')
        
        if not date or not meal:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not meal.get('description') or not meal.get('nutrition'):
            return jsonify({'error': 'Invalid meal data'}), 400
        
        meal['date'] = date
        meal['id'] = meal_id
        
        db.update_meal(meal_id, meal)
        
        return jsonify({
            'success': True,
            'message': f'Meal "{meal["description"]}" updated successfully',
            'meal': meal,
            'date': date
        })
    except Exception as error:
        print(f'Error updating meal: {error}')
        return jsonify({'error': 'Failed to update meal'}), 500


@app.route('/api/meals/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    """Delete a meal"""
    check = require_db()
    if check:
        return check
    
    try:
        db.delete_meal(meal_id)
        
        return jsonify({
            'success': True,
            'message': 'Meal deleted successfully'
        })
    except Exception as error:
        print(f'Error deleting meal: {error}')
        return jsonify({'error': 'Failed to delete meal'}), 500


@app.route('/api/meals/bulk', methods=['POST'])
def bulk_meals():
    """Bulk import or sync meals"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        operation = data.get('operation')
        meals_data = data.get('meals')
        
        if not operation or not meals_data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        processed_count = 0
        
        if operation in ['import', 'sync']:
            for date, date_meals in meals_data.items():
                for meal in date_meals:
                    meal['date'] = date
                    try:
                        db.add_meal(meal)
                        processed_count += 1
                    except Exception as error:
                        print(f'Error importing meal {meal.get("id")}: {error}')
            
            return jsonify({
                'success': True,
                'message': f'{operation} completed',
                'processedCount': processed_count
            })
        else:
            return jsonify({'error': 'Invalid operation'}), 400
    except Exception as error:
        print(f'Error in bulk operation: {error}')
        return jsonify({'error': 'Bulk operation failed'}), 500


@app.route('/api/meals/copy', methods=['POST'])
def copy_meals():
    """Copy all meals from one date to another"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        source_date = data.get('sourceDate')
        target_date = data.get('targetDate')
        
        if not source_date or not target_date:
            return jsonify({'error': 'Missing required fields: sourceDate, targetDate'}), 400
        
        if source_date == target_date:
            return jsonify({'error': 'sourceDate and targetDate must differ'}), 400
        
        source_meals = db.get_meals_by_date(source_date)
        copied = 0
        
        for meal in source_meals:
            new_meal = {
                'description': meal['description'],
                'mealType': meal['mealType'],
                'date': target_date,
                'timestamp': datetime.now().isoformat(),
                'source': meal.get('source', ''),
                'nutrition': meal['nutrition'],
                'ingredient_data': meal.get('ingredient_data')
            }
            try:
                db.add_meal(new_meal)
                copied += 1
            except Exception as err:
                print(f'Error copying meal id={meal["id"]} to {target_date}: {err}')
        
        return jsonify({
            'success': True,
            'sourceDate': source_date,
            'targetDate': target_date,
            'copied': copied,
            'total': len(source_meals)
        })
    except Exception as error:
        print(f'Error copying meals: {error}')
        return jsonify({'error': 'Failed to copy meals'}), 500


@app.route('/api/meals/by-date/<date>', methods=['DELETE'])
def delete_meals_by_date(date):
    """Delete all meals for a given date"""
    check = require_db()
    if check:
        return check
    
    try:
        if not date:
            return jsonify({'error': 'Missing required field: date'}), 400
        
        meals = db.get_meals_by_date(date)
        deleted = 0
        
        for meal in meals:
            try:
                db.delete_meal(meal['id'])
                deleted += 1
            except Exception as err:
                print(f'Error deleting meal id={meal["id"]} for {date}: {err}')
        
        return jsonify({
            'success': True,
            'date': date,
            'deleted': deleted
        })
    except Exception as error:
        print(f'Error deleting meals by date: {error}')
        return jsonify({'error': 'Failed to delete meals by date'}), 500


# ============= ANALYTICS API =============

@app.route('/api/analytics/daily/<date>', methods=['GET'])
def get_daily_analytics(date):
    """Get daily nutrition summary"""
    check = require_db()
    if check:
        return check
    
    try:
        summary = db.get_daily_summary(date)
        return jsonify(summary)
    except Exception as error:
        print(f'Error getting daily summary: {error}')
        return jsonify({'error': 'Failed to get daily summary'}), 500


@app.route('/api/analytics/weekly', methods=['GET'])
def get_weekly_analytics():
    """Get weekly nutrition summary"""
    check = require_db()
    if check:
        return check
    
    try:
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Missing startDate or endDate'}), 400
        
        summaries = db.get_weekly_summary(start_date, end_date)
        return jsonify(summaries)
    except Exception as error:
        print(f'Error getting weekly summary: {error}')
        return jsonify({'error': 'Failed to get weekly summary'}), 500


# ============= AI ASSISTANT API =============

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI Chat endpoint with Gemini"""
    try:
        data = request.get_json()
        message = data.get('message')
        date = data.get('date')
        nutrition_data = data.get('nutritionData')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # If Gemini is not available, use fallback
        if not gemini_model:
            return jsonify({
                'response': "I'm currently unavailable. Please set the GEMINI_API_KEY environment variable to enable AI chat. In the meantime, use the quick action buttons above for nutrition analysis.",
                'fallback': True
            })
        
        # Build context from user's nutrition data
        context = 'You are a helpful nutrition assistant. '
        
        if nutrition_data and nutrition_data.get('summary'):
            s = nutrition_data['summary']
            context += f"The user has logged {s.get('meal_count', 0)} meals today ({date or 'today'}) with {round(s.get('total_calories', 0))} calories, {round(s.get('total_protein', 0))}g protein, {round(s.get('total_carbs', 0))}g carbs, {round(s.get('total_fat', 0))}g fat, and {round(s.get('total_fiber', 0))}g fiber. "
        
        context += 'Provide concise, helpful nutrition advice. Keep responses under 100 words unless detailed analysis is requested. Use a friendly, encouraging tone.'
        
        prompt = f"{context}\n\nUser question: {message}\n\nResponse:"
        
        response = gemini_model.generate_content(prompt)
        text = response.text
        
        return jsonify({
            'response': text,
            'fallback': False
        })
    except Exception as error:
        print(f'Error in AI chat: {error}')
        
        # Friendly error response
        return jsonify({
            'response': "I'm having trouble processing your request right now. Please try asking in a different way or use the quick action buttons above!",
            'error': True,
            'fallback': True
        })


@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """Generate AI nutrition analysis"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        date = data.get('date')
        
        if not date:
            return jsonify({'error': 'Date is required'}), 400
        
        analysis = ai_assistant.generate_suggestions(date)
        return jsonify(analysis)
    except Exception as error:
        print(f'Error generating AI analysis: {error}')
        return jsonify({'error': 'Failed to generate analysis'}), 500


@app.route('/api/ai/weekly-progress', methods=['POST'])
def ai_weekly_progress():
    """Get weekly progress report"""
    check = require_db()
    if check:
        return check
    
    try:
        progress = ai_assistant.get_weekly_progress()
        return jsonify(progress)
    except Exception as error:
        print(f'Error getting weekly progress: {error}')
        return jsonify({'error': 'Failed to get weekly progress'}), 500


@app.route('/api/ai/compare', methods=['POST'])
def ai_compare():
    """Compare current week with previous week"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        current_start_date = data.get('currentStartDate')
        current_end_date = data.get('currentEndDate')
        
        if not current_start_date or not current_end_date:
            return jsonify({'error': 'Date range is required'}), 400
        
        comparison = ai_assistant.compare_with_previous_week(current_start_date, current_end_date)
        return jsonify(comparison)
    except Exception as error:
        print(f'Error comparing periods: {error}')
        return jsonify({'error': 'Failed to compare periods'}), 500


@app.route('/api/ai/recommendations', methods=['POST'])
def ai_recommendations():
    """Get food recommendations for deficient nutrients"""
    check = require_db()
    if check:
        return check
    
    try:
        data = request.get_json()
        deficient_nutrients = data.get('deficientNutrients')
        
        if not isinstance(deficient_nutrients, list):
            return jsonify({'error': 'deficientNutrients must be an array'}), 400
        
        recommendations = ai_assistant.get_food_recommendations(deficient_nutrients)
        return jsonify(recommendations)
    except Exception as error:
        print(f'Error getting recommendations: {error}')
        return jsonify({'error': 'Failed to get recommendations'}), 500


# ============= HEALTH CHECK =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'database': 'connected' if db_connected else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })


# ============= ERROR HANDLING =============

@app.errorhandler(Exception)
def handle_error(error):
    """Error handling middleware"""
    print(f'Unhandled error: {error}')
    return jsonify({'error': 'Internal server error'}), 500


# ============= SERVER STARTUP =============

# Initialize database on startup (but don't exit on failure in production)
try:
    initialize_database()
except Exception as e:
    print(f'⚠️  Database initialization error: {e}')
    print('Server will start but database features may not work')

if __name__ == '__main__':
    # For local development only
    port = int(os.getenv('PORT', 3000))
    
    print(f'\n🚀 Food Tracker Server running on http://localhost:{port}')
    print(f'📊 Database: {"Connected" if db_connected else "Disconnected"}')
    print(f'🤖 AI Assistant: Ready\n')
    
    app.run(host='0.0.0.0', port=port, debug=False)
