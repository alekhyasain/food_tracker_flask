"""
AI Assistant Service for Food Tracker
Provides nutrition analysis, suggestions, and recommendations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from db_service import DatabaseService


class AIAssistantService:
    """AI-powered nutrition assistant"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    def analyze_nutrition_pattern(self, start_date: str, end_date: str) -> Dict:
        """Analyze user's nutrition patterns over a date range"""
        summaries = self.db.get_weekly_summary(start_date, end_date)
        
        if not summaries:
            return {
                'message': "No data available for the selected date range.",
                'hasData': False
            }
        
        # Calculate averages
        totals = {
            'calories': sum(day['total_calories'] for day in summaries),
            'protein': sum(day['total_protein'] for day in summaries),
            'carbs': sum(day['total_carbs'] for day in summaries),
            'fat': sum(day['total_fat'] for day in summaries),
            'fiber': sum(day['total_fiber'] for day in summaries)
        }
        
        days = len(summaries)
        averages = {
            'calories': round(totals['calories'] / days),
            'protein': round(totals['protein'] / days),
            'carbs': round(totals['carbs'] / days),
            'fat': round(totals['fat'] / days),
            'fiber': round(totals['fiber'] / days)
        }
        
        return {
            'hasData': True,
            'period': {'startDate': start_date, 'endDate': end_date, 'days': days},
            'averages': averages,
            'totals': totals,
            'dailyData': summaries
        }
    
    def generate_suggestions(self, date: str) -> Dict:
        """Generate nutrition suggestions based on WHO/USDA guidelines"""
        summary = self.db.get_daily_summary(date)
        meals = self.db.get_meals_by_date(date)
        
        suggestions = []
        insights = []
        
        # Recommended daily values (approximate for average adult)
        targets = {
            'calories': {'min': 1800, 'max': 2400},
            'protein': {'min': 50, 'max': 175},  # 10-35% of calories
            'carbs': {'min': 225, 'max': 325},   # 45-65% of calories
            'fat': {'min': 44, 'max': 78},       # 20-35% of calories
            'fiber': {'min': 25, 'max': 38}      # 25g women, 38g men
        }
        
        # Analyze calories
        if summary['total_calories'] < targets['calories']['min']:
            suggestions.append({
                'type': 'warning',
                'category': 'calories',
                'message': f'Your calorie intake ({round(summary["total_calories"])} kcal) is below the recommended minimum of {targets["calories"]["min"]} kcal.',
                'recommendation': 'Consider adding nutrient-dense foods like nuts, avocados, or whole grains to meet your energy needs.'
            })
        elif summary['total_calories'] > targets['calories']['max']:
            suggestions.append({
                'type': 'info',
                'category': 'calories',
                'message': f'Your calorie intake ({round(summary["total_calories"])} kcal) exceeds the typical recommendation of {targets["calories"]["max"]} kcal.',
                'recommendation': 'Monitor portion sizes and consider reducing high-calorie processed foods if weight management is a goal.'
            })
        else:
            insights.append({
                'type': 'success',
                'category': 'calories',
                'message': f'Great! Your calorie intake ({round(summary["total_calories"])} kcal) is within the recommended range.'
            })
        
        # Analyze protein
        if summary['total_protein'] < targets['protein']['min']:
            suggestions.append({
                'type': 'warning',
                'category': 'protein',
                'message': f'Your protein intake ({round(summary["total_protein"])}g) is below the recommended minimum.',
                'recommendation': 'Add protein-rich foods like lentils, chickpeas, tofu, eggs, or Greek yogurt to your meals.'
            })
        elif summary['total_protein'] >= targets['protein']['min']:
            insights.append({
                'type': 'success',
                'category': 'protein',
                'message': f'Excellent protein intake ({round(summary["total_protein"])}g)! Protein helps with muscle maintenance and satiety.'
            })
        
        # Analyze fiber
        if summary['total_fiber'] < targets['fiber']['min']:
            suggestions.append({
                'type': 'warning',
                'category': 'fiber',
                'message': f'Your fiber intake ({round(summary["total_fiber"])}g) is below the recommended {targets["fiber"]["min"]}g.',
                'recommendation': 'Increase fiber by eating more vegetables, fruits, whole grains, and legumes. Fiber aids digestion and heart health.'
            })
        else:
            insights.append({
                'type': 'success',
                'category': 'fiber',
                'message': f'Great fiber intake ({round(summary["total_fiber"])}g)! This supports digestive health.'
            })
        
        # Analyze macronutrient balance
        total_cals = summary['total_calories'] or 1
        protein_percent = (summary['total_protein'] * 4 / total_cals) * 100
        carbs_percent = (summary['total_carbs'] * 4 / total_cals) * 100
        fat_percent = (summary['total_fat'] * 9 / total_cals) * 100
        
        if carbs_percent > 70:
            suggestions.append({
                'type': 'info',
                'category': 'balance',
                'message': f'Your diet is high in carbohydrates ({round(carbs_percent)}% of calories).',
                'recommendation': 'Consider balancing with more protein and healthy fats for sustained energy.'
            })
        
        if fat_percent < 20:
            suggestions.append({
                'type': 'info',
                'category': 'balance',
                'message': f'Your fat intake is relatively low ({round(fat_percent)}% of calories).',
                'recommendation': 'Include healthy fats from sources like nuts, seeds, olive oil, and avocados for better nutrient absorption.'
            })
        
        # Meal frequency analysis
        if summary['meal_count'] < 2:
            suggestions.append({
                'type': 'info',
                'category': 'frequency',
                'message': 'You logged fewer than 2 meals today.',
                'recommendation': 'Regular meals help maintain stable energy levels. Aim for 3 balanced meals or 2-3 main meals with healthy snacks.'
            })
        
        # Variety analysis
        meal_types = list(set(meal['mealType'] for meal in meals))
        insights.append({
            'type': 'info',
            'category': 'variety',
            'message': f'You logged {summary["meal_count"]} meal(s) across {len(meal_types)} meal type(s): {", ".join(meal_types)}.'
        })
        
        return {
            'date': date,
            'summary': summary,
            'suggestions': suggestions,
            'insights': insights,
            'macroBreakdown': {
                'protein': {'grams': round(summary['total_protein']), 'percent': round(protein_percent)},
                'carbs': {'grams': round(summary['total_carbs']), 'percent': round(carbs_percent)},
                'fat': {'grams': round(summary['total_fat']), 'percent': round(fat_percent)}
            }
        }
    
    def get_food_recommendations(self, deficient_nutrients: List[str]) -> Dict:
        """Get specific food recommendations for deficient nutrients"""
        recommendations = {
            'protein': [
                'Lentils (toor dal, moong dal) - excellent protein source',
                'Chickpeas (chana) - versatile and protein-rich',
                'Paneer - Indian cottage cheese, high in protein',
                'Greek yogurt or hung curd - probiotic-rich protein',
                'Eggs - complete protein with all essential amino acids',
                'Tofu or soy products - plant-based complete protein'
            ],
            'fiber': [
                'Whole wheat chapati instead of white rice',
                'Oats upma or dalia for breakfast',
                'Mixed vegetable sabzi with leafy greens',
                'Fresh fruits like apple, pear, or guava',
                'Brown rice or quinoa instead of white rice',
                'Sprouts (moong, chana) - fiber and protein rich'
            ],
            'calories': [
                'Nuts and seeds (almonds, walnuts, pumpkin seeds)',
                'Ghee or coconut oil in moderation',
                'Banana or dates for natural energy',
                'Whole grain bread with nut butter',
                'Smoothie with banana, oats, and milk',
                'Energy balls made with dates and nuts'
            ],
            'fat': [
                'Avocado or avocado toast',
                'Nuts (almonds, cashews, walnuts)',
                'Seeds (chia, flax, pumpkin)',
                'Olive oil or coconut oil for cooking',
                'Fatty fish like salmon (if non-vegetarian)',
                'Nut butters (peanut, almond)'
            ],
            'carbs': [
                'Whole grains (brown rice, quinoa, oats)',
                'Sweet potato or regular potato',
                'Whole wheat bread or chapati',
                'Fruits (banana, mango, apple)',
                'Legumes (rajma, chole)',
                'Idli or dosa made from whole grains'
            ]
        }
        
        result = {}
        for nutrient in deficient_nutrients:
            if nutrient in recommendations:
                result[nutrient] = recommendations[nutrient]
        
        return result
    
    def get_weekly_progress(self) -> Dict:
        """Weekly progress analysis"""
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        
        start_date = seven_days_ago.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        analysis = self.analyze_nutrition_pattern(start_date, end_date)
        
        if not analysis['hasData']:
            return {
                'message': "No data available for the past week.",
                'hasData': False
            }
        
        suggestions = []
        
        # Consistency check
        if len(analysis['dailyData']) < 5:
            suggestions.append({
                'type': 'info',
                'message': f'You\'ve logged meals on {len(analysis["dailyData"])} out of 7 days.',
                'recommendation': 'Try to log meals consistently for better tracking and insights.'
            })
        
        # Average calories trend
        if analysis['averages']['calories'] < 1800:
            suggestions.append({
                'type': 'warning',
                'message': 'Your average daily calorie intake is below recommendations.',
                'recommendation': 'Focus on regular, balanced meals to meet your energy needs.'
            })
        
        # Fiber trend
        if analysis['averages']['fiber'] < 25:
            suggestions.append({
                'type': 'warning',
                'message': 'Your average fiber intake could be improved.',
                'recommendation': 'Incorporate more vegetables, fruits, and whole grains throughout the week.'
            })
        
        return {
            'hasData': True,
            'period': '7 days',
            'averages': analysis['averages'],
            'suggestions': suggestions,
            'dailyData': analysis['dailyData']
        }
    
    def compare_with_previous_week(self, current_start_date: str, current_end_date: str) -> Dict:
        """Comparative analysis between current and previous week"""
        current = self.analyze_nutrition_pattern(current_start_date, current_end_date)
        
        if not current['hasData']:
            return {'message': "Insufficient data for comparison", 'hasData': False}
        
        # Calculate previous week dates
        start = datetime.strptime(current_start_date, '%Y-%m-%d')
        end = datetime.strptime(current_end_date, '%Y-%m-%d')
        days_diff = (end - start).days
        
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days_diff)
        
        previous = self.analyze_nutrition_pattern(
            prev_start.strftime('%Y-%m-%d'),
            prev_end.strftime('%Y-%m-%d')
        )
        
        if not previous['hasData']:
            return {
                'message': "No previous period data for comparison",
                'current': current,
                'hasComparison': False
            }
        
        changes = {
            'calories': current['averages']['calories'] - previous['averages']['calories'],
            'protein': current['averages']['protein'] - previous['averages']['protein'],
            'carbs': current['averages']['carbs'] - previous['averages']['carbs'],
            'fat': current['averages']['fat'] - previous['averages']['fat'],
            'fiber': current['averages']['fiber'] - previous['averages']['fiber']
        }
        
        insights = []
        
        if abs(changes['calories']) > 100:
            direction = 'increased' if changes['calories'] > 0 else 'decreased'
            insights.append({
                'type': 'increase' if changes['calories'] > 0 else 'decrease',
                'category': 'calories',
                'message': f'Your average daily calories {direction} by {abs(round(changes["calories"]))} kcal compared to the previous period.'
            })
        
        if changes['protein'] > 10:
            insights.append({
                'type': 'increase',
                'category': 'protein',
                'message': f'Great! Your protein intake increased by {round(changes["protein"])}g per day.'
            })
        elif changes['protein'] < -10:
            insights.append({
                'type': 'decrease',
                'category': 'protein',
                'message': f'Your protein intake decreased by {abs(round(changes["protein"]))}g per day. Consider adding protein-rich foods.'
            })
        
        if changes['fiber'] > 5:
            insights.append({
                'type': 'increase',
                'category': 'fiber',
                'message': f'Excellent! Your fiber intake increased by {round(changes["fiber"])}g per day.'
            })
        
        return {
            'hasComparison': True,
            'current': current,
            'previous': previous,
            'changes': changes,
            'insights': insights
        }
