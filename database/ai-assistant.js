const DatabaseService = require('./db-service');

class AIAssistantService {
    constructor(dbService) {
        this.db = dbService;
    }

    // Analyze user's nutrition patterns
    async analyzeNutritionPattern(startDate, endDate) {
        const summaries = await this.db.getWeeklySummary(startDate, endDate);
        
        if (summaries.length === 0) {
            return {
                message: "No data available for the selected date range.",
                hasData: false
            };
        }

        // Calculate averages
        const totals = summaries.reduce((acc, day) => ({
            calories: acc.calories + day.total_calories,
            protein: acc.protein + day.total_protein,
            carbs: acc.carbs + day.total_carbs,
            fat: acc.fat + day.total_fat,
            fiber: acc.fiber + day.total_fiber
        }), { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 });

        const days = summaries.length;
        const averages = {
            calories: Math.round(totals.calories / days),
            protein: Math.round(totals.protein / days),
            carbs: Math.round(totals.carbs / days),
            fat: Math.round(totals.fat / days),
            fiber: Math.round(totals.fiber / days)
        };

        return {
            hasData: true,
            period: { startDate, endDate, days },
            averages,
            totals,
            dailyData: summaries
        };
    }

    // Generate nutrition suggestions based on WHO/USDA guidelines
    async generateSuggestions(date) {
        const summary = await this.db.getDailySummary(date);
        const meals = await this.db.getMealsByDate(date);
        
        const suggestions = [];
        const insights = [];

        // Recommended daily values (approximate for average adult)
        const targets = {
            calories: { min: 1800, max: 2400 },
            protein: { min: 50, max: 175 },  // 10-35% of calories
            carbs: { min: 225, max: 325 },   // 45-65% of calories
            fat: { min: 44, max: 78 },       // 20-35% of calories
            fiber: { min: 25, max: 38 }      // 25g women, 38g men
        };

        // Analyze calories
        if (summary.total_calories < targets.calories.min) {
            suggestions.push({
                type: 'warning',
                category: 'calories',
                message: `Your calorie intake (${Math.round(summary.total_calories)} kcal) is below the recommended minimum of ${targets.calories.min} kcal.`,
                recommendation: 'Consider adding nutrient-dense foods like nuts, avocados, or whole grains to meet your energy needs.'
            });
        } else if (summary.total_calories > targets.calories.max) {
            suggestions.push({
                type: 'info',
                category: 'calories',
                message: `Your calorie intake (${Math.round(summary.total_calories)} kcal) exceeds the typical recommendation of ${targets.calories.max} kcal.`,
                recommendation: 'Monitor portion sizes and consider reducing high-calorie processed foods if weight management is a goal.'
            });
        } else {
            insights.push({
                type: 'success',
                category: 'calories',
                message: `Great! Your calorie intake (${Math.round(summary.total_calories)} kcal) is within the recommended range.`
            });
        }

        // Analyze protein
        if (summary.total_protein < targets.protein.min) {
            suggestions.push({
                type: 'warning',
                category: 'protein',
                message: `Your protein intake (${Math.round(summary.total_protein)}g) is below the recommended minimum.`,
                recommendation: 'Add protein-rich foods like lentils, chickpeas, tofu, eggs, or Greek yogurt to your meals.'
            });
        } else if (summary.total_protein >= targets.protein.min) {
            insights.push({
                type: 'success',
                category: 'protein',
                message: `Excellent protein intake (${Math.round(summary.total_protein)}g)! Protein helps with muscle maintenance and satiety.`
            });
        }

        // Analyze fiber
        if (summary.total_fiber < targets.fiber.min) {
            suggestions.push({
                type: 'warning',
                category: 'fiber',
                message: `Your fiber intake (${Math.round(summary.total_fiber)}g) is below the recommended ${targets.fiber.min}g.`,
                recommendation: 'Increase fiber by eating more vegetables, fruits, whole grains, and legumes. Fiber aids digestion and heart health.'
            });
        } else {
            insights.push({
                type: 'success',
                category: 'fiber',
                message: `Great fiber intake (${Math.round(summary.total_fiber)}g)! This supports digestive health.`
            });
        }

        // Analyze macronutrient balance
        const totalCals = summary.total_calories || 1;
        const proteinPercent = (summary.total_protein * 4 / totalCals) * 100;
        const carbsPercent = (summary.total_carbs * 4 / totalCals) * 100;
        const fatPercent = (summary.total_fat * 9 / totalCals) * 100;

        if (carbsPercent > 70) {
            suggestions.push({
                type: 'info',
                category: 'balance',
                message: `Your diet is high in carbohydrates (${Math.round(carbsPercent)}% of calories).`,
                recommendation: 'Consider balancing with more protein and healthy fats for sustained energy.'
            });
        }

        if (fatPercent < 20) {
            suggestions.push({
                type: 'info',
                category: 'balance',
                message: `Your fat intake is relatively low (${Math.round(fatPercent)}% of calories).`,
                recommendation: 'Include healthy fats from sources like nuts, seeds, olive oil, and avocados for better nutrient absorption.'
            });
        }

        // Meal frequency analysis
        if (summary.meal_count < 2) {
            suggestions.push({
                type: 'info',
                category: 'frequency',
                message: 'You logged fewer than 2 meals today.',
                recommendation: 'Regular meals help maintain stable energy levels. Aim for 3 balanced meals or 2-3 main meals with healthy snacks.'
            });
        }

        // Variety analysis
        const mealTypes = [...new Set(meals.map(m => m.mealType))];
        insights.push({
            type: 'info',
            category: 'variety',
            message: `You logged ${summary.meal_count} meal(s) across ${mealTypes.length} meal type(s): ${mealTypes.join(', ')}.`
        });

        return {
            date,
            summary,
            suggestions,
            insights,
            macroBreakdown: {
                protein: { grams: Math.round(summary.total_protein), percent: Math.round(proteinPercent) },
                carbs: { grams: Math.round(summary.total_carbs), percent: Math.round(carbsPercent) },
                fat: { grams: Math.round(summary.total_fat), percent: Math.round(fatPercent) }
            }
        };
    }

    // Get specific food recommendations
    async getFoodRecommendations(deficientNutrients) {
        const recommendations = {
            protein: [
                'Lentils (toor dal, moong dal) - excellent protein source',
                'Chickpeas (chana) - versatile and protein-rich',
                'Paneer - Indian cottage cheese, high in protein',
                'Greek yogurt or hung curd - probiotic-rich protein',
                'Eggs - complete protein with all essential amino acids',
                'Tofu or soy products - plant-based complete protein'
            ],
            fiber: [
                'Whole wheat chapati instead of white rice',
                'Oats upma or dalia for breakfast',
                'Mixed vegetable sabzi with leafy greens',
                'Fresh fruits like apple, pear, or guava',
                'Brown rice or quinoa instead of white rice',
                'Sprouts (moong, chana) - fiber and protein rich'
            ],
            calories: [
                'Nuts and seeds (almonds, walnuts, pumpkin seeds)',
                'Ghee or coconut oil in moderation',
                'Banana or dates for natural energy',
                'Whole grain bread with nut butter',
                'Smoothie with banana, oats, and milk',
                'Energy balls made with dates and nuts'
            ],
            fat: [
                'Avocado or avocado toast',
                'Nuts (almonds, cashews, walnuts)',
                'Seeds (chia, flax, pumpkin)',
                'Olive oil or coconut oil for cooking',
                'Fatty fish like salmon (if non-vegetarian)',
                'Nut butters (peanut, almond)'
            ],
            carbs: [
                'Whole grains (brown rice, quinoa, oats)',
                'Sweet potato or regular potato',
                'Whole wheat bread or chapati',
                'Fruits (banana, mango, apple)',
                'Legumes (rajma, chole)',
                'Idli or dosa made from whole grains'
            ]
        };

        const result = {};
        for (const nutrient of deficientNutrients) {
            if (recommendations[nutrient]) {
                result[nutrient] = recommendations[nutrient];
            }
        }

        return result;
    }

    // Weekly progress analysis
    async getWeeklyProgress() {
        const today = new Date();
        const sevenDaysAgo = new Date(today);
        sevenDaysAgo.setDate(today.getDate() - 7);

        const startDate = sevenDaysAgo.toISOString().split('T')[0];
        const endDate = today.toISOString().split('T')[0];

        const analysis = await this.analyzeNutritionPattern(startDate, endDate);
        
        if (!analysis.hasData) {
            return {
                message: "No data available for the past week.",
                hasData: false
            };
        }

        const suggestions = [];
        
        // Consistency check
        if (analysis.dailyData.length < 5) {
            suggestions.push({
                type: 'info',
                message: `You've logged meals on ${analysis.dailyData.length} out of 7 days.`,
                recommendation: 'Try to log meals consistently for better tracking and insights.'
            });
        }

        // Average calories trend
        if (analysis.averages.calories < 1800) {
            suggestions.push({
                type: 'warning',
                message: 'Your average daily calorie intake is below recommendations.',
                recommendation: 'Focus on regular, balanced meals to meet your energy needs.'
            });
        }

        // Fiber trend
        if (analysis.averages.fiber < 25) {
            suggestions.push({
                type: 'warning',
                message: 'Your average fiber intake could be improved.',
                recommendation: 'Incorporate more vegetables, fruits, and whole grains throughout the week.'
            });
        }

        return {
            hasData: true,
            period: '7 days',
            averages: analysis.averages,
            suggestions,
            dailyData: analysis.dailyData
        };
    }

    // Comparative analysis
    async compareWithPreviousWeek(currentStartDate, currentEndDate) {
        const current = await this.analyzeNutritionPattern(currentStartDate, currentEndDate);
        
        if (!current.hasData) {
            return { message: "Insufficient data for comparison", hasData: false };
        }

        // Calculate previous week dates
        const start = new Date(currentStartDate);
        const end = new Date(currentEndDate);
        const daysDiff = Math.floor((end - start) / (1000 * 60 * 60 * 24));
        
        const prevEnd = new Date(start);
        prevEnd.setDate(prevEnd.getDate() - 1);
        const prevStart = new Date(prevEnd);
        prevStart.setDate(prevStart.getDate() - daysDiff);

        const previous = await this.analyzeNutritionPattern(
            prevStart.toISOString().split('T')[0],
            prevEnd.toISOString().split('T')[0]
        );

        if (!previous.hasData) {
            return {
                message: "No previous period data for comparison",
                current,
                hasComparison: false
            };
        }

        const changes = {
            calories: current.averages.calories - previous.averages.calories,
            protein: current.averages.protein - previous.averages.protein,
            carbs: current.averages.carbs - previous.averages.carbs,
            fat: current.averages.fat - previous.averages.fat,
            fiber: current.averages.fiber - previous.averages.fiber
        };

        const insights = [];
        
        if (Math.abs(changes.calories) > 100) {
            insights.push({
                type: changes.calories > 0 ? 'increase' : 'decrease',
                category: 'calories',
                message: `Your average daily calories ${changes.calories > 0 ? 'increased' : 'decreased'} by ${Math.abs(Math.round(changes.calories))} kcal compared to the previous period.`
            });
        }

        if (changes.protein > 10) {
            insights.push({
                type: 'increase',
                category: 'protein',
                message: `Great! Your protein intake increased by ${Math.round(changes.protein)}g per day.`
            });
        } else if (changes.protein < -10) {
            insights.push({
                type: 'decrease',
                category: 'protein',
                message: `Your protein intake decreased by ${Math.abs(Math.round(changes.protein))}g per day. Consider adding protein-rich foods.`
            });
        }

        if (changes.fiber > 5) {
            insights.push({
                type: 'increase',
                category: 'fiber',
                message: `Excellent! Your fiber intake increased by ${Math.round(changes.fiber)}g per day.`
            });
        }

        return {
            hasComparison: true,
            current,
            previous,
            changes,
            insights
        };
    }
}

module.exports = AIAssistantService;
