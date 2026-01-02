#!/usr/bin/env python3
"""
Food Tracker CLI
Command-line interface for managing food intake, nutrition, and recipes
"""

import sys
import argparse
import json
from datetime import datetime, timedelta
from typing import Optional
import os

from db_service import DatabaseService
from ai_assistant import AIAssistantService


class FoodTrackerCLI:
    """Command-line interface for food tracker"""
    
    def __init__(self):
        self.db = DatabaseService()
        self.db.connect()
        self.ai = AIAssistantService(self.db)
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
    
    # ============= MEALS COMMANDS =============
    
    def add_meal(self, description: str, meal_type: str, date: Optional[str] = None,
                 calories: float = 0, protein: float = 0, carbs: float = 0,
                 fat: float = 0, fiber: float = 0):
        """Add a new meal"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        meal_data = {
            'id': int(datetime.now().timestamp() * 1000),
            'description': description,
            'mealType': meal_type,
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'source': 'cli',
            'nutrition': {
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'fiber': fiber
            }
        }
        
        try:
            self.db.add_meal(meal_data)
            print(f"✅ Meal '{description}' added successfully for {date}")
            print(f"   Nutrition: {calories} kcal, {protein}g protein, {carbs}g carbs, {fat}g fat, {fiber}g fiber")
        except Exception as e:
            print(f"❌ Error adding meal: {e}")
            sys.exit(1)
    
    def list_meals(self, date: Optional[str] = None, days: int = 1):
        """List meals for a date or date range"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            if days == 1:
                meals = self.db.get_meals_by_date(date)
                print(f"\n📋 Meals for {date}:\n")
                
                if not meals:
                    print("No meals logged for this date.")
                    return
                
                for meal in meals:
                    n = meal['nutrition']
                    print(f"[{meal['mealType']}] {meal['description']}")
                    print(f"  ID: {meal['id']} | Time: {meal['timestamp'][:19]}")
                    print(f"  {n['calories']:.0f} kcal | {n['protein']:.1f}g protein | {n['carbs']:.1f}g carbs | {n['fat']:.1f}g fat | {n['fiber']:.1f}g fiber\n")
            else:
                start_date = datetime.strptime(date, '%Y-%m-%d')
                end_date = start_date + timedelta(days=days-1)
                meals_by_date = self.db.get_meals_by_date_range(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                print(f"\n📋 Meals from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}:\n")
                
                if not meals_by_date:
                    print("No meals logged for this date range.")
                    return
                
                for date_str in sorted(meals_by_date.keys()):
                    print(f"\n📅 {date_str}:")
                    for meal in meals_by_date[date_str]:
                        n = meal['nutrition']
                        print(f"  [{meal['mealType']}] {meal['description']}")
                        print(f"    {n['calories']:.0f} kcal | {n['protein']:.1f}g protein")
        
        except Exception as e:
            print(f"❌ Error listing meals: {e}")
            sys.exit(1)
    
    def delete_meal(self, meal_id: int):
        """Delete a meal by ID"""
        try:
            self.db.delete_meal(meal_id)
            print(f"✅ Meal {meal_id} deleted successfully")
        except Exception as e:
            print(f"❌ Error deleting meal: {e}")
            sys.exit(1)
    
    def copy_meals(self, source_date: str, target_date: str):
        """Copy all meals from one date to another"""
        try:
            source_meals = self.db.get_meals_by_date(source_date)
            
            if not source_meals:
                print(f"No meals found for {source_date}")
                return
            
            copied = 0
            for meal in source_meals:
                new_meal = {
                    'description': meal['description'],
                    'mealType': meal['mealType'],
                    'date': target_date,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'cli_copy',
                    'nutrition': meal['nutrition'],
                    'ingredient_data': meal.get('ingredient_data')
                }
                try:
                    self.db.add_meal(new_meal)
                    copied += 1
                except Exception as err:
                    print(f"⚠️  Error copying meal: {err}")
            
            print(f"✅ Copied {copied}/{len(source_meals)} meals from {source_date} to {target_date}")
        except Exception as e:
            print(f"❌ Error copying meals: {e}")
            sys.exit(1)
    
    # ============= ANALYTICS COMMANDS =============
    
    def show_summary(self, date: Optional[str] = None):
        """Show daily nutrition summary"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            summary = self.db.get_daily_summary(date)
            
            print(f"\n📊 Daily Summary for {date}\n")
            print(f"{'='*50}")
            print(f"Meals logged:    {summary['meal_count']}")
            print(f"Total calories:  {summary['total_calories']:.0f} kcal")
            print(f"Protein:         {summary['total_protein']:.1f} g")
            print(f"Carbohydrates:   {summary['total_carbs']:.1f} g")
            print(f"Fat:             {summary['total_fat']:.1f} g")
            print(f"Fiber:           {summary['total_fiber']:.1f} g")
            print(f"{'='*50}\n")
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
            sys.exit(1)
    
    def show_weekly(self, start_date: Optional[str] = None):
        """Show weekly nutrition summary"""
        if not start_date:
            today = datetime.now()
            start = today - timedelta(days=6)
            start_date = start.strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        else:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = (start + timedelta(days=6)).strftime('%Y-%m-%d')
        
        try:
            summaries = self.db.get_weekly_summary(start_date, end_date)
            
            print(f"\n📈 Weekly Summary ({start_date} to {end_date})\n")
            print(f"{'Date':<12} {'Meals':<7} {'Calories':<10} {'Protein':<9} {'Carbs':<9} {'Fat':<8} {'Fiber':<8}")
            print(f"{'-'*70}")
            
            total_cals = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            total_fiber = 0
            
            for day in summaries:
                print(f"{day['date']:<12} {day['meal_count']:<7} {day['total_calories']:<10.0f} "
                      f"{day['total_protein']:<9.1f} {day['total_carbs']:<9.1f} "
                      f"{day['total_fat']:<8.1f} {day['total_fiber']:<8.1f}")
                total_cals += day['total_calories']
                total_protein += day['total_protein']
                total_carbs += day['total_carbs']
                total_fat += day['total_fat']
                total_fiber += day['total_fiber']
            
            if summaries:
                days = len(summaries)
                print(f"{'-'*70}")
                print(f"{'Averages:':<12} {'':<7} {total_cals/days:<10.0f} "
                      f"{total_protein/days:<9.1f} {total_carbs/days:<9.1f} "
                      f"{total_fat/days:<8.1f} {total_fiber/days:<8.1f}\n")
        except Exception as e:
            print(f"❌ Error getting weekly summary: {e}")
            sys.exit(1)
    
    def analyze(self, date: Optional[str] = None):
        """Get AI nutrition analysis and suggestions"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            analysis = self.ai.generate_suggestions(date)
            
            print(f"\n🤖 AI Nutrition Analysis for {date}\n")
            print(f"{'='*70}")
            
            # Show summary
            s = analysis['summary']
            print(f"\n📊 Summary:")
            print(f"  {s['meal_count']} meals | {s['total_calories']:.0f} kcal | "
                  f"{s['total_protein']:.1f}g protein | {s['total_carbs']:.1f}g carbs | "
                  f"{s['total_fat']:.1f}g fat | {s['total_fiber']:.1f}g fiber")
            
            # Show macro breakdown
            if 'macroBreakdown' in analysis:
                mb = analysis['macroBreakdown']
                print(f"\n💪 Macronutrient Breakdown:")
                print(f"  Protein: {mb['protein']['grams']}g ({mb['protein']['percent']}%)")
                print(f"  Carbs:   {mb['carbs']['grams']}g ({mb['carbs']['percent']}%)")
                print(f"  Fat:     {mb['fat']['grams']}g ({mb['fat']['percent']}%)")
            
            # Show insights
            if analysis.get('insights'):
                print(f"\n✨ Insights:")
                for insight in analysis['insights']:
                    icon = '✅' if insight['type'] == 'success' else 'ℹ️'
                    print(f"  {icon} {insight['message']}")
            
            # Show suggestions
            if analysis.get('suggestions'):
                print(f"\n💡 Suggestions:")
                for suggestion in analysis['suggestions']:
                    icon = '⚠️' if suggestion['type'] == 'warning' else 'ℹ️'
                    print(f"\n  {icon} {suggestion['message']}")
                    print(f"     → {suggestion['recommendation']}")
            
            print(f"\n{'='*70}\n")
        except Exception as e:
            print(f"❌ Error analyzing nutrition: {e}")
            sys.exit(1)
    
    def get_recommendations(self, nutrients: str):
        """Get food recommendations for deficient nutrients"""
        nutrient_list = [n.strip() for n in nutrients.split(',')]
        
        try:
            recommendations = self.ai.get_food_recommendations(nutrient_list)
            
            print(f"\n🍽️  Food Recommendations\n")
            print(f"{'='*70}")
            
            for nutrient, foods in recommendations.items():
                print(f"\n📌 {nutrient.upper()}:")
                for food in foods:
                    print(f"  • {food}")
            
            print(f"\n{'='*70}\n")
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
            sys.exit(1)
    
    # ============= INGREDIENTS COMMANDS =============
    
    def list_ingredients(self, category: Optional[str] = None):
        """List all ingredients or ingredients in a category"""
        try:
            ingredients = self.db.get_all_ingredients()
            
            print(f"\n🥗 Ingredients\n")
            
            for cat, items in ingredients['basic_ingredients'].items():
                if category and cat.lower() != category.lower():
                    continue
                
                print(f"\n📂 {cat}:")
                for key, data in items.items():
                    print(f"  • {data['name']} ({key})")
                    print(f"    Measurements: {', '.join(data['measurements'].keys())}")
            
            print()
        except Exception as e:
            print(f"❌ Error listing ingredients: {e}")
            sys.exit(1)
    
    def add_ingredient(self, category: str, key: str, name: str, 
                      measurement: str, calories: float, protein: float,
                      carbs: float, fat: float, fiber: float):
        """Add a new ingredient"""
        try:
            ingredient_data = {
                'name': name,
                'measurements': {
                    measurement: {
                        'calories': calories,
                        'protein': protein,
                        'carbs': carbs,
                        'fat': fat,
                        'fiber': fiber
                    }
                }
            }
            
            self.db.add_ingredient(category, key, ingredient_data)
            print(f"✅ Ingredient '{name}' added to category '{category}'")
        except Exception as e:
            print(f"❌ Error adding ingredient: {e}")
            sys.exit(1)
    
    # ============= RECIPES COMMANDS =============
    
    def list_recipes(self):
        """List all recipes"""
        try:
            recipes = self.db.get_all_recipes()
            
            print(f"\n🍳 Recipes\n")
            
            for key, data in recipes['dishes'].items():
                print(f"\n📖 {data['name']} ({key})")
                n = data['total_per_serving']
                print(f"   Servings: {data['servings']}")
                print(f"   Per serving: {n['calories']:.0f} kcal, {n['protein']:.1f}g protein, "
                      f"{n['carbs']:.1f}g carbs, {n['fat']:.1f}g fat, {n['fiber']:.1f}g fiber")
                
                if data.get('ingredients'):
                    print(f"   Ingredients:")
                    for ing in data['ingredients']:
                        print(f"     • {ing['name']} - {ing['amount']}")
            
            print()
        except Exception as e:
            print(f"❌ Error listing recipes: {e}")
            sys.exit(1)
    
    # ============= EXPORT/IMPORT COMMANDS =============
    
    def export_data(self, output_file: str, data_type: str = 'all'):
        """Export data to JSON file"""
        try:
            data = {}
            
            if data_type in ['all', 'ingredients']:
                data['ingredients'] = self.db.get_all_ingredients()
            
            if data_type in ['all', 'recipes']:
                data['recipes'] = self.db.get_all_recipes()
            
            if data_type in ['all', 'meals']:
                # Export last 90 days of meals
                end = datetime.now()
                start = end - timedelta(days=90)
                data['meals'] = self.db.get_meals_by_date_range(
                    start.strftime('%Y-%m-%d'),
                    end.strftime('%Y-%m-%d')
                )
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Data exported to {output_file}")
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            sys.exit(1)
    
    def import_data(self, input_file: str):
        """Import data from JSON file"""
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Import ingredients
            if 'ingredients' in data and 'basic_ingredients' in data['ingredients']:
                for category, items in data['ingredients']['basic_ingredients'].items():
                    for key, item_data in items.items():
                        try:
                            self.db.add_ingredient(category, key, item_data)
                            print(f"✅ Imported ingredient: {item_data['name']}")
                        except Exception as e:
                            print(f"⚠️  Skipped ingredient {item_data.get('name', key)}: {e}")
            
            # Import recipes
            if 'recipes' in data and 'dishes' in data['recipes']:
                for key, recipe_data in data['recipes']['dishes'].items():
                    try:
                        self.db.add_recipe(key, recipe_data)
                        print(f"✅ Imported recipe: {recipe_data['name']}")
                    except Exception as e:
                        print(f"⚠️  Skipped recipe {recipe_data.get('name', key)}: {e}")
            
            # Import meals
            if 'meals' in data:
                for date, meals in data['meals'].items():
                    for meal in meals:
                        try:
                            self.db.add_meal(meal)
                        except Exception as e:
                            pass  # Skip duplicates silently
            
            print(f"✅ Data import completed from {input_file}")
        except Exception as e:
            print(f"❌ Error importing data: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Food Tracker CLI - Manage your food intake and nutrition',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Meal commands
    add_meal_parser = subparsers.add_parser('add-meal', help='Add a new meal')
    add_meal_parser.add_argument('description', help='Meal description')
    add_meal_parser.add_argument('meal_type', help='Meal type (breakfast, lunch, dinner, snack)')
    add_meal_parser.add_argument('--date', help='Date (YYYY-MM-DD, default: today)')
    add_meal_parser.add_argument('--calories', type=float, default=0, help='Calories')
    add_meal_parser.add_argument('--protein', type=float, default=0, help='Protein (g)')
    add_meal_parser.add_argument('--carbs', type=float, default=0, help='Carbohydrates (g)')
    add_meal_parser.add_argument('--fat', type=float, default=0, help='Fat (g)')
    add_meal_parser.add_argument('--fiber', type=float, default=0, help='Fiber (g)')
    
    list_meals_parser = subparsers.add_parser('list-meals', help='List meals')
    list_meals_parser.add_argument('--date', help='Date (YYYY-MM-DD, default: today)')
    list_meals_parser.add_argument('--days', type=int, default=1, help='Number of days to show')
    
    delete_meal_parser = subparsers.add_parser('delete-meal', help='Delete a meal')
    delete_meal_parser.add_argument('meal_id', type=int, help='Meal ID')
    
    copy_meals_parser = subparsers.add_parser('copy-meals', help='Copy meals from one date to another')
    copy_meals_parser.add_argument('source_date', help='Source date (YYYY-MM-DD)')
    copy_meals_parser.add_argument('target_date', help='Target date (YYYY-MM-DD)')
    
    # Analytics commands
    summary_parser = subparsers.add_parser('summary', help='Show daily nutrition summary')
    summary_parser.add_argument('--date', help='Date (YYYY-MM-DD, default: today)')
    
    weekly_parser = subparsers.add_parser('weekly', help='Show weekly nutrition summary')
    weekly_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD, default: 7 days ago)')
    
    analyze_parser = subparsers.add_parser('analyze', help='Get AI nutrition analysis')
    analyze_parser.add_argument('--date', help='Date (YYYY-MM-DD, default: today)')
    
    recommend_parser = subparsers.add_parser('recommend', help='Get food recommendations')
    recommend_parser.add_argument('nutrients', help='Comma-separated nutrients (e.g., protein,fiber)')
    
    # Ingredient commands
    subparsers.add_parser('list-ingredients', help='List all ingredients')
    
    add_ingredient_parser = subparsers.add_parser('add-ingredient', help='Add a new ingredient')
    add_ingredient_parser.add_argument('category', help='Category name')
    add_ingredient_parser.add_argument('key', help='Ingredient key')
    add_ingredient_parser.add_argument('name', help='Ingredient name')
    add_ingredient_parser.add_argument('measurement', help='Measurement unit')
    add_ingredient_parser.add_argument('calories', type=float, help='Calories')
    add_ingredient_parser.add_argument('protein', type=float, help='Protein (g)')
    add_ingredient_parser.add_argument('carbs', type=float, help='Carbohydrates (g)')
    add_ingredient_parser.add_argument('fat', type=float, help='Fat (g)')
    add_ingredient_parser.add_argument('fiber', type=float, help='Fiber (g)')
    
    # Recipe commands
    subparsers.add_parser('list-recipes', help='List all recipes')
    
    # Export/Import commands
    export_parser = subparsers.add_parser('export', help='Export data to JSON')
    export_parser.add_argument('output_file', help='Output file path')
    export_parser.add_argument('--type', default='all', choices=['all', 'ingredients', 'recipes', 'meals'],
                              help='Data type to export')
    
    import_parser = subparsers.add_parser('import', help='Import data from JSON')
    import_parser.add_argument('input_file', help='Input file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Initialize CLI
    cli = FoodTrackerCLI()
    
    # Execute command
    if args.command == 'add-meal':
        cli.add_meal(args.description, args.meal_type, args.date,
                    args.calories, args.protein, args.carbs, args.fat, args.fiber)
    elif args.command == 'list-meals':
        cli.list_meals(args.date, args.days)
    elif args.command == 'delete-meal':
        cli.delete_meal(args.meal_id)
    elif args.command == 'copy-meals':
        cli.copy_meals(args.source_date, args.target_date)
    elif args.command == 'summary':
        cli.show_summary(args.date)
    elif args.command == 'weekly':
        cli.show_weekly(args.start_date)
    elif args.command == 'analyze':
        cli.analyze(args.date)
    elif args.command == 'recommend':
        cli.get_recommendations(args.nutrients)
    elif args.command == 'list-ingredients':
        cli.list_ingredients()
    elif args.command == 'add-ingredient':
        cli.add_ingredient(args.category, args.key, args.name, args.measurement,
                          args.calories, args.protein, args.carbs, args.fat, args.fiber)
    elif args.command == 'list-recipes':
        cli.list_recipes()
    elif args.command == 'export':
        cli.export_data(args.output_file, args.type)
    elif args.command == 'import':
        cli.import_data(args.input_file)


if __name__ == '__main__':
    main()
