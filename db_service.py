"""
Database Service for Food Tracker
SQLite database operations for ingredients, recipes, meals, and analytics
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class DatabaseService:
    """Database service for managing food tracker data"""
    
    def __init__(self, db_path='./database/food_tracker.db'):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print('Connected to SQLite database')
        except Exception as e:
            print(f'Error connecting to database: {e}')
            raise
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL statement and return cursor"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one row as dictionary"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows as list of dictionaries"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # ============= INGREDIENTS METHODS =============
    
    def get_all_ingredients(self) -> Dict:
        """Get all ingredients organized by category"""
        query = """
            SELECT 
                c.name as category_name,
                i.key as ingredient_key,
                i.name as ingredient_name,
                i.id as ingredient_id
            FROM ingredients i
            JOIN categories c ON i.category_id = c.id
            ORDER BY c.name, i.name
        """
        
        rows = self.fetch_all(query)
        result = {'basic_ingredients': {}}
        
        for row in rows:
            category_name = row['category_name']
            if category_name not in result['basic_ingredients']:
                result['basic_ingredients'][category_name] = {}
            
            # Get measurements for this ingredient
            measurements = self.fetch_all(
                """SELECT measurement_key, calories, protein, carbs, fat, fiber 
                   FROM ingredient_measurements 
                   WHERE ingredient_id = ?""",
                (row['ingredient_id'],)
            )
            
            measurements_obj = {}
            for m in measurements:
                measurements_obj[m['measurement_key']] = {
                    'calories': m['calories'],
                    'protein': m['protein'],
                    'carbs': m['carbs'],
                    'fat': m['fat'],
                    'fiber': m['fiber']
                }
            
            result['basic_ingredients'][category_name][row['ingredient_key']] = {
                'name': row['ingredient_name'],
                'measurements': measurements_obj
            }
        
        return result
    
    def add_ingredient(self, category: str, ingredient_key: str, ingredient_data: Dict):
        """Add a new ingredient"""
        # Get or create category
        category_row = self.fetch_one('SELECT id FROM categories WHERE name = ?', (category,))
        
        if not category_row:
            cursor = self.execute('INSERT INTO categories (name) VALUES (?)', (category,))
            category_id = cursor.lastrowid
        else:
            category_id = category_row['id']
        
        # Insert ingredient
        try:
            cursor = self.execute(
                'INSERT INTO ingredients (category_id, key, name) VALUES (?, ?, ?)',
                (category_id, ingredient_key, ingredient_data['name'])
            )
            ingredient_id = cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                raise Exception('Ingredient already exists in this category')
            raise
        
        # Insert measurements
        if 'measurements' in ingredient_data:
            for measure_key, nutrition in ingredient_data['measurements'].items():
                try:
                    self.execute(
                        """INSERT INTO ingredient_measurements 
                        (ingredient_id, measurement_key, calories, protein, carbs, fat, fiber) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            ingredient_id,
                            measure_key,
                            nutrition.get('calories', 0),
                            nutrition.get('protein', 0),
                            nutrition.get('carbs', 0),
                            nutrition.get('fat', 0),
                            nutrition.get('fiber', 0)
                        )
                    )
                except sqlite3.IntegrityError as e:
                    if 'UNIQUE constraint failed' in str(e):
                        raise Exception('Measurement key already exists for this ingredient')
                    raise
        
        return {'success': True, 'ingredientId': ingredient_id}
    
    def update_ingredient(self, category: str, ingredient_key: str, ingredient_data: Dict):
        """Update an existing ingredient"""
        # Get category ID
        category_row = self.fetch_one('SELECT id FROM categories WHERE name = ?', (category,))
        if not category_row:
            raise Exception('Category not found')
        
        # Get ingredient
        ingredient = self.fetch_one(
            'SELECT id FROM ingredients WHERE category_id = ? AND key = ?',
            (category_row['id'], ingredient_key)
        )
        
        if not ingredient:
            raise Exception('Ingredient not found')
        
        # Update ingredient name
        self.execute(
            'UPDATE ingredients SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (ingredient_data['name'], ingredient['id'])
        )
        
        # Delete old measurements
        self.execute('DELETE FROM ingredient_measurements WHERE ingredient_id = ?', (ingredient['id'],))
        
        # Insert new measurements
        if 'measurements' in ingredient_data:
            for measure_key, nutrition in ingredient_data['measurements'].items():
                self.execute(
                    """INSERT INTO ingredient_measurements 
                    (ingredient_id, measurement_key, calories, protein, carbs, fat, fiber) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ingredient['id'],
                        measure_key,
                        nutrition.get('calories', 0),
                        nutrition.get('protein', 0),
                        nutrition.get('carbs', 0),
                        nutrition.get('fat', 0),
                        nutrition.get('fiber', 0)
                    )
                )
        
        return {'success': True}
    
    def delete_ingredient(self, category: str, ingredient_key: str) -> Dict:
        """Delete an ingredient"""
        category_row = self.fetch_one('SELECT id FROM categories WHERE name = ?', (category,))
        if not category_row:
            raise Exception('Category not found')
        
        ingredient = self.fetch_one(
            'SELECT id, name FROM ingredients WHERE category_id = ? AND key = ?',
            (category_row['id'], ingredient_key)
        )
        
        if not ingredient:
            raise Exception('Ingredient not found')
        
        self.execute('DELETE FROM ingredients WHERE id = ?', (ingredient['id'],))
        
        return {'success': True, 'name': ingredient['name']}
    
    def get_ingredient(self, category: str, ingredient_key: str) -> Optional[Dict]:
        """Get a single ingredient with its measurements"""
        category_row = self.fetch_one('SELECT id FROM categories WHERE name = ?', (category,))
        if not category_row:
            return None
        
        ingredient = self.fetch_one(
            'SELECT id, name FROM ingredients WHERE category_id = ? AND key = ?',
            (category_row['id'], ingredient_key)
        )
        
        if not ingredient:
            return None
        
        measurements = self.fetch_all(
            """SELECT measurement_key, calories, protein, carbs, fat, fiber 
               FROM ingredient_measurements WHERE ingredient_id = ?""",
            (ingredient['id'],)
        )
        
        measurements_obj = {}
        for m in measurements:
            measurements_obj[m['measurement_key']] = {
                'calories': m['calories'],
                'protein': m['protein'],
                'carbs': m['carbs'],
                'fat': m['fat'],
                'fiber': m['fiber']
            }
        
        return {
            'id': ingredient['id'],
            'name': ingredient['name'],
            'key': ingredient_key,
            'measurements': measurements_obj
        }
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        rows = self.fetch_all('SELECT name FROM categories ORDER BY name')
        return [row['name'] for row in rows]
    
    # ============= RECIPES METHODS =============
    
    def get_all_recipes(self) -> Dict:
        """Get all recipes"""
        recipes = self.fetch_all("""
            SELECT r.*, 
                   rn.calories, rn.protein, rn.carbs, rn.fat, rn.fiber
            FROM recipes r
            LEFT JOIN recipe_nutrition rn ON r.id = rn.recipe_id
            ORDER BY r.name
        """)
        
        result = {'dishes': {}}
        
        for recipe in recipes:
            # Get recipe ingredients
            ingredients = self.fetch_all(
                """SELECT ingredient_key, ingredient_name, amount, 
                          calories, protein, carbs, fat, fiber
                   FROM recipe_ingredients 
                   WHERE recipe_id = ?""",
                (recipe['id'],)
            )
            
            result['dishes'][recipe['key']] = {
                'name': recipe['name'],
                'category': recipe['category'],
                'servings': recipe['servings'],
                'total_per_serving': {
                    'calories': recipe['calories'] or 0,
                    'protein': recipe['protein'] or 0,
                    'carbs': recipe['carbs'] or 0,
                    'fat': recipe['fat'] or 0,
                    'fiber': recipe['fiber'] or 0
                },
                'ingredients': [
                    {
                        'key': ing['ingredient_key'],
                        'name': ing['ingredient_name'],
                        'amount': ing['amount'],
                        'nutrition': {
                            'calories': ing['calories'],
                            'protein': ing['protein'],
                            'carbs': ing['carbs'],
                            'fat': ing['fat'],
                            'fiber': ing['fiber']
                        }
                    }
                    for ing in ingredients
                ]
            }
        
        return result
    
    def add_recipe(self, recipe_key: str, recipe_data: Dict):
        """Add a new recipe"""
        cursor = self.execute(
            'INSERT INTO recipes (key, name, category, servings) VALUES (?, ?, ?, ?)',
            (recipe_key, recipe_data['name'], recipe_data.get('category'), recipe_data.get('servings', 1))
        )
        
        recipe_id = cursor.lastrowid
        
        # Add nutrition
        if 'total_per_serving' in recipe_data:
            nutrition = recipe_data['total_per_serving']
            self.execute(
                """INSERT INTO recipe_nutrition 
                (recipe_id, calories, protein, carbs, fat, fiber) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    recipe_id,
                    nutrition.get('calories', 0),
                    nutrition.get('protein', 0),
                    nutrition.get('carbs', 0),
                    nutrition.get('fat', 0),
                    nutrition.get('fiber', 0)
                )
            )
        
        # Add ingredients
        if 'ingredients' in recipe_data and isinstance(recipe_data['ingredients'], list):
            for ingredient in recipe_data['ingredients']:
                nutrition = ingredient.get('nutrition', {})
                self.execute(
                    """INSERT INTO recipe_ingredients 
                    (recipe_id, ingredient_key, ingredient_name, amount, 
                     calories, protein, carbs, fat, fiber) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        recipe_id,
                        ingredient.get('key', ''),
                        ingredient.get('name', ''),
                        ingredient.get('amount', ''),
                        nutrition.get('calories', 0),
                        nutrition.get('protein', 0),
                        nutrition.get('carbs', 0),
                        nutrition.get('fat', 0),
                        nutrition.get('fiber', 0)
                    )
                )
        
        return {'success': True, 'recipeId': recipe_id}
    
    def update_recipe(self, recipe_key: str, recipe_data: Dict):
        """Update an existing recipe"""
        recipe = self.fetch_one('SELECT id FROM recipes WHERE key = ?', (recipe_key,))
        
        if not recipe:
            raise Exception('Recipe not found')
        
        # Update recipe
        self.execute(
            'UPDATE recipes SET name = ?, category = ?, servings = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (recipe_data['name'], recipe_data.get('category'), recipe_data.get('servings', 1), recipe['id'])
        )
        
        # Update nutrition
        self.execute('DELETE FROM recipe_nutrition WHERE recipe_id = ?', (recipe['id'],))
        if 'total_per_serving' in recipe_data:
            nutrition = recipe_data['total_per_serving']
            self.execute(
                """INSERT INTO recipe_nutrition 
                (recipe_id, calories, protein, carbs, fat, fiber) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    recipe['id'],
                    nutrition.get('calories', 0),
                    nutrition.get('protein', 0),
                    nutrition.get('carbs', 0),
                    nutrition.get('fat', 0),
                    nutrition.get('fiber', 0)
                )
            )
        
        # Update ingredients
        self.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe['id'],))
        if 'ingredients' in recipe_data and isinstance(recipe_data['ingredients'], list):
            for ingredient in recipe_data['ingredients']:
                nutrition = ingredient.get('nutrition', {})
                self.execute(
                    """INSERT INTO recipe_ingredients 
                    (recipe_id, ingredient_key, ingredient_name, amount, 
                     calories, protein, carbs, fat, fiber) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        recipe['id'],
                        ingredient.get('key', ''),
                        ingredient.get('name', ''),
                        ingredient.get('amount', ''),
                        nutrition.get('calories', 0),
                        nutrition.get('protein', 0),
                        nutrition.get('carbs', 0),
                        nutrition.get('fat', 0),
                        nutrition.get('fiber', 0)
                    )
                )
        
        return {'success': True}
    
    def delete_recipe(self, recipe_key: str) -> Dict:
        """Delete a recipe"""
        recipe = self.fetch_one('SELECT id, name FROM recipes WHERE key = ?', (recipe_key,))
        
        if not recipe:
            raise Exception('Recipe not found')
        
        self.execute('DELETE FROM recipes WHERE id = ?', (recipe['id'],))
        
        return {'success': True, 'name': recipe['name']}
    
    # ============= MEALS METHODS =============
    
    def get_meals_by_date(self, date: str) -> List[Dict]:
        """Get all meals for a specific date"""
        meals = self.fetch_all(
            """SELECT id, description, meal_type, date, timestamp, source,
                      calories, protein, carbs, fat, fiber, ingredient_data
               FROM meals 
               WHERE date = ? 
               ORDER BY timestamp""",
            (date,)
        )
        
        return [
            {
                'id': meal['id'],
                'description': meal['description'],
                'mealType': meal['meal_type'],
                'date': meal['date'],
                'timestamp': meal['timestamp'],
                'source': meal['source'],
                'nutrition': {
                    'calories': meal['calories'],
                    'protein': meal['protein'],
                    'carbs': meal['carbs'],
                    'fat': meal['fat'],
                    'fiber': meal['fiber']
                },
                'ingredient_data': json.loads(meal['ingredient_data']) if meal['ingredient_data'] else None
            }
            for meal in meals
        ]
    
    def get_meals_by_date_range(self, start_date: str, end_date: str) -> Dict:
        """Get all meals within a date range"""
        meals = self.fetch_all(
            """SELECT * FROM meals
               WHERE date >= ? AND date <= ?
               ORDER BY date, timestamp""",
            (start_date, end_date)
        )
        
        result = {}
        for meal in meals:
            date = meal['date']
            if date not in result:
                result[date] = []
            
            result[date].append({
                'id': meal['id'],
                'description': meal['description'],
                'mealType': meal['meal_type'],
                'date': meal['date'],
                'timestamp': meal['timestamp'],
                'source': meal['source'],
                'nutrition': {
                    'calories': meal['calories'],
                    'protein': meal['protein'],
                    'carbs': meal['carbs'],
                    'fat': meal['fat'],
                    'fiber': meal['fiber']
                },
                'ingredient_data': json.loads(meal['ingredient_data']) if meal['ingredient_data'] else None
            })
        
        return result
    
    def add_meal(self, meal_data: Dict):
        """Add a new meal"""
        ingredient_data = json.dumps(meal_data.get('ingredient_data')) if meal_data.get('ingredient_data') else None
        nutrition = meal_data.get('nutrition', {})
        
        cursor = self.execute(
            """INSERT INTO meals 
            (id, description, meal_type, date, timestamp, source, 
             calories, protein, carbs, fat, fiber, ingredient_data) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                meal_data.get('id', int(datetime.now().timestamp() * 1000)),
                meal_data.get('description', ''),
                meal_data.get('mealType', ''),
                meal_data.get('date', ''),
                meal_data.get('timestamp', datetime.now().isoformat()),
                meal_data.get('source', ''),
                nutrition.get('calories', 0),
                nutrition.get('protein', 0),
                nutrition.get('carbs', 0),
                nutrition.get('fat', 0),
                nutrition.get('fiber', 0),
                ingredient_data
            )
        )
        
        return {'success': True, 'mealId': cursor.lastrowid}
    
    def update_meal(self, meal_id: int, meal_data: Dict):
        """Update an existing meal"""
        ingredient_data = json.dumps(meal_data.get('ingredient_data')) if meal_data.get('ingredient_data') else None
        nutrition = meal_data.get('nutrition', {})
        
        self.execute(
            """UPDATE meals 
            SET description = ?, meal_type = ?, date = ?, timestamp = ?, source = ?,
                calories = ?, protein = ?, carbs = ?, fat = ?, fiber = ?, ingredient_data = ?
            WHERE id = ?""",
            (
                meal_data.get('description', ''),
                meal_data.get('mealType', ''),
                meal_data.get('date', ''),
                meal_data.get('timestamp', datetime.now().isoformat()),
                meal_data.get('source', ''),
                nutrition.get('calories', 0),
                nutrition.get('protein', 0),
                nutrition.get('carbs', 0),
                nutrition.get('fat', 0),
                nutrition.get('fiber', 0),
                ingredient_data,
                meal_id
            )
        )
        
        return {'success': True}
    
    def delete_meal(self, meal_id: int):
        """Delete a meal"""
        self.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
        return {'success': True}
    
    def get_daily_summary(self, date: str) -> Dict:
        """Get daily nutrition summary"""
        summary = self.fetch_one('SELECT * FROM daily_summary WHERE date = ?', (date,))
        
        if not summary:
            return {
                'date': date,
                'total_calories': 0,
                'total_protein': 0,
                'total_carbs': 0,
                'total_fat': 0,
                'total_fiber': 0,
                'meal_count': 0
            }
        
        return dict(summary)
    
    def get_weekly_summary(self, start_date: str, end_date: str) -> List[Dict]:
        """Get weekly nutrition summary"""
        summaries = self.fetch_all(
            """SELECT * FROM daily_summary 
               WHERE date >= ? AND date <= ? 
               ORDER BY date""",
            (start_date, end_date)
        )
        
        return summaries
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
