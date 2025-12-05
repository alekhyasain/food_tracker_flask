I've updated the food_tracker.html file with the changes to allow editing recipe ingredients. This involves modifying how ingredients are stored (to keep the raw data needed for the form) and adding "Edit" buttons to the ingredient list.

Here are the specific updates:

addRecipeIngredient: Now saves measurementKey, quantity, and key along with the display text.

updateRecipePreview: Now renders an Edit (✏️) button and uses array indices for safer removal/editing.

New Functions: Added editRecipeIngredientLine(index) and removeRecipeIngredientLine(index) to handle the logic of pulling data back into the form.

food_tracker.html
HTML

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian Food Diary - Volume Based Tracking</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .modal {
            display: none;
        }
        .modal.active {
            display: flex;
        }
        
        /* Tab styling */
        .add-tab-btn, .log-tab-btn {
            transition: all 0.2s ease;
        }
        
        .add-tab-btn:hover, .log-tab-btn:hover {
            border-color: #fb923c !important;
            color: #ea580c !important;
        }
        
        /* Responsive tab navigation */
        @media (max-width: 640px) {
            .add-tab-btn, .log-tab-btn {
                font-size: 0.75rem;
                padding: 0.5rem 0.25rem;
            }
        }
        
        /* Modal content animations */
        .add-tab-content, .log-tab-content {
            animation: fadeInTab 0.3s ease-in-out;
        }
        
        @keyframes fadeInTab {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Enhanced button styling */
        .unified-btn {
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .unified-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body class="bg-gradient-to-br from-orange-50 to-red-100 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-800 mb-2">🍛 Indian Food Diary</h1>
            <p class="text-lg text-gray-600">Volume-Based Tracking - Cups, Tablespoons & More!</p>
            
            <div class="bg-white rounded-lg shadow-lg p-4 mt-4 mb-4">
                <div class="flex items-center justify-center space-x-4 mb-3">
                    <button onclick="navigateDate(-1)" class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition duration-200">
                        ← Previous Day
                    </button>
                    <div class="text-center">
                        <input type="date" id="dateSelector" class="text-lg font-semibold text-gray-800 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500" onchange="selectDate()">
                        <div id="selectedDateDisplay" class="text-sm text-gray-600 mt-1"></div>
                    </div>
                    <button onclick="navigateDate(1)" class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition duration-200">
                        Next Day →
                    </button>
                </div>
                <div class="flex justify-center space-x-2">
                    <button onclick="goToToday()" class="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded text-sm transition duration-200">
                        Today
                    </button>
                    <button onclick="goToYesterday()" class="bg-gray-400 hover:bg-gray-500 text-white px-3 py-1 rounded text-sm transition duration-200">
                        Yesterday
                    </button>
                </div>
            </div>
            
            <div class="bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 mt-4 rounded">
                <p class="font-semibold">📏 Easy Volume Measurements</p>
                <p>Track with simple measurements like "1 cup rice" or "2 tbsp oil" - no weighing required!</p>
            </div>
            <div class="mt-6 space-y-4">
                <div class="flex flex-col sm:flex-row gap-4 justify-center max-w-3xl mx-auto">
                    <button onclick="openUnifiedAddModal()" class="unified-btn flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white px-8 py-4 rounded-xl">
                        <div class="text-center">
                            <div class="text-2xl mb-1">➕</div>
                            <div class="font-semibold text-lg">Add Meal or Ingredient</div>
                            <div class="text-sm opacity-90">Create meals, manage ingredients, or add recipes</div>
                        </div>
                    </button>
                    <button onclick="startDirectExport()" class="unified-btn flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white px-8 py-4 rounded-xl" id="mainExportButton">
                        <div class="text-center">
                            <div class="text-2xl mb-1">📊</div>
                            <div class="font-semibold text-lg">Export to Excel</div>
                            <div class="text-sm opacity-90">Download your food diary data</div>
                        </div>
                    </button>
                </div>
                <p class="text-sm text-gray-500 text-center">Everything you need in two simple buttons - add meals and export data!</p>
                
                <div id="exportStatusDisplay" class="hidden mt-4 max-w-md mx-auto">
                    <div id="exportStatusContent" class="p-4 rounded-lg border text-center">
                        <div id="exportStatusIcon" class="text-2xl mb-2"></div>
                        <div id="exportStatusMessage" class="font-medium"></div>
                        <div id="exportStatusDetails" class="text-sm mt-1 opacity-75"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4" id="dailySummaryTitle">📊 Daily Summary</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-orange-50 rounded-lg">
                    <div class="text-2xl font-bold text-orange-600" id="totalCalories">0</div>
                    <div class="text-sm text-gray-600">Total Calories</div>
                </div>
                <div class="text-center p-4 bg-green-50 rounded-lg">
                    <div class="text-2xl font-bold text-green-600" id="mealCount">0</div>
                    <div class="text-sm text-gray-600">Meals Logged</div>
                </div>
                <div class="text-center p-4 bg-blue-50 rounded-lg">
                    <div class="text-2xl font-bold text-blue-600" id="totalProtein">0g</div>
                    <div class="text-sm text-gray-600">Protein</div>
                </div>
                <div class="text-center p-4 bg-purple-50 rounded-lg">
                    <div class="text-2xl font-bold text-purple-600" id="totalFiber">0g</div>
                    <div class="text-sm text-gray-600">Fiber</div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-2xl font-semibold text-gray-800" id="weightTrackingTitle">⚖️ Weight Tracking & Goals</h2>
                <div class="flex space-x-2">
                    <button onclick="openGoalSettingModal()" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition duration-200">
                        🎯 Set Goals
                    </button>
                    <button onclick="openWeightEntryModal()" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition duration-200">
                        📊 Log Weight
                    </button>
                </div>
            </div>
            
            <div class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 mb-6">
                <div class="flex justify-between items-center mb-3">
                    <h3 class="text-lg font-semibold text-gray-800">📈 Weekly Deficit Progress</h3>
                    <div class="text-sm text-gray-600" id="weeklyDeficitDate">Current Week</div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div class="text-center p-3 bg-white rounded-lg">
                        <div class="text-xl font-bold text-green-600" id="weeklyDeficitCurrent">0</div>
                        <div class="text-sm text-gray-600">Weekly Deficit</div>
                        <div class="text-xs text-gray-500">calories</div>
                    </div>
                    <div class="text-center p-3 bg-white rounded-lg">
                        <div class="text-xl font-bold text-blue-600" id="weeklyDeficitGoal">3,500</div>
                        <div class="text-sm text-gray-600">Weekly Goal</div>
                        <div class="text-xs text-gray-500">1 lb loss</div>
                    </div>
                    <div class="text-center p-3 bg-white rounded-lg">
                        <div class="text-xl font-bold text-purple-600" id="dailyDeficitAvg">500</div>
                        <div class="text-sm text-gray-600">Daily Target</div>
                        <div class="text-xs text-gray-500">avg needed</div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <div class="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Progress to Weekly Goal</span>
                        <span id="weeklyDeficitPercent">0%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3">
                        <div class="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-500"
                             style="width: 0%" id="weeklyDeficitProgressBar"></div>
                    </div>
                </div>
                
                <div class="grid grid-cols-7 gap-1 text-xs">
                    <div class="text-center p-2 bg-white rounded" id="dayDeficit0">
                        <div class="font-semibold">Mon</div>
                        <div class="text-gray-600" id="dayDeficitValue0">--</div>
                    </div>
                    <div class="text-center p-2 bg-white rounded" id="dayDeficit1">
                        <div class="font-semibold">Tue</div>
                        <div class="text-gray-600" id="dayDeficitValue1">--</div>
                    </div>
                    <div class="text-center p-2 bg-white rounded" id="dayDeficit2">
                        <div class="font-semibold">Wed</div>
                        <div class="text-gray-600" id="dayDeficitValue2">--</div>
                    </div>
                    <div class="text-center p-2 bg-white rounded" id="dayDeficit3">
                        <div class="font-semibold">Thu</div>
                        <div class="text-gray-600" id="dayDeficitValue3">--</div>
                    </div>
                    <div class="text-center p-2 bg-white rounded" id="dayDeficit4">
                        <div class="font-semibold">Fri</div>
                        <div class="text-gray-600" id="dayDeficitValue4">--</div>
                    </div>
                    <div class="text-center p-2 bg-white rounded" id="dayDeficit5">
                        <div class="font-semibold">Sat</div>
                        <div class="text-gray-600" id="dayDeficitValue5">--</div>
                    </div>
                    <div class="text-center p-2 bg-white rounded" id="dayDeficit6">
                        <div class="font-semibold">Sun</div>
                        <div class="text-gray-600" id="dayDeficitValue6">--</div>
                    </div>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div class="text-center p-4 bg-purple-50 rounded-lg">
                    <div class="text-2xl font-bold text-purple-600" id="currentWeight">--</div>
                    <div class="text-sm text-gray-600">Current Weight (lbs)</div>
                    <div class="text-xs text-gray-500 mt-1" id="weightDate">No data</div>
                </div>
                
                <div class="text-center p-4 bg-indigo-50 rounded-lg">
                    <div class="text-2xl font-bold text-indigo-600" id="currentBMI">--</div>
                    <div class="text-sm text-gray-600">BMI</div>
                    <div class="text-xs mt-1" id="bmiCategory">No data</div>
                </div>
                
                <div class="text-center p-4 bg-orange-50 rounded-lg relative">
                    <div class="flex items-center justify-center mb-1">
                        <div class="text-2xl font-bold text-orange-600" id="currentBMR">--</div>
                        <button onclick="showBMRExplanation()" class="ml-2 text-orange-500 hover:text-orange-700 text-sm" title="Click for BMR explanation" id="bmrInfoButton" style="display: none;">
                            ℹ️
                        </button>
                    </div>
                    <div class="text-sm text-gray-600">BMR</div>
                    <div class="text-xs text-gray-500 mt-1" id="bmrMethod">No data</div>
                </div>
                
                <div class="text-center p-4 bg-blue-50 rounded-lg relative">
                    <div class="flex items-center justify-center mb-1">
                        <div class="text-2xl font-bold text-blue-600" id="calorieGoal">--</div>
                        <button onclick="showGoalExplanation()" class="ml-2 text-blue-500 hover:text-blue-700 text-sm" title="Click for explanation">
                            ℹ️
                        </button>
                    </div>
                    <div class="text-sm text-gray-600">Daily Goal</div>
                    <div class="text-xs text-gray-500 mt-1" id="calorieDeficit">Deficit: --</div>
                    <div class="text-xs text-blue-600 mt-1" id="goalSource">--</div>
                    <div class="text-xs text-green-600 mt-1" id="exerciseAdjustmentStatus">--</div>
                </div>
                
                <div class="text-center p-4 bg-green-50 rounded-lg">
                    <div class="text-2xl font-bold text-green-600" id="caloriesBurned">0</div>
                    <div class="text-sm text-gray-600">Calories Burned</div>
                    <div class="text-xs text-gray-500 mt-1">
                        <button onclick="openExerciseModal()" class="text-green-600 hover:text-green-800 underline">
                            + Add Exercise
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6 mb-8" id="exercisesSection">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-2xl font-semibold text-gray-800" id="exercisesSectionTitle">🏃‍♂️ Today's Exercises</h2>
                    <div class="flex space-x-2">
                        <button onclick="openExerciseModal()" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition duration-200">
                            💪 Add Exercise
                        </button>
                        <button onclick="clearAllExercises()" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition duration-200">
                            🗑️ Clear All
                        </button>
                    </div>
                </div>
                
                <div id="exercisesList" class="space-y-3">
                    <div class="text-center text-gray-500 py-8">
                        <p>No exercises logged yet. Add an exercise to get started!</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4">📋 Your Food Log</h2>
            <div id="foodLog" class="space-y-4">
                <div class="text-center text-gray-500 py-8">
                    <p>No meals logged yet. Try adding a dish above!</p>
                </div>
            </div>
        </div>
    </div>

    <div id="recipeModal" class="modal fixed inset-0 bg-black bg-opacity-50 items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-semibold text-gray-800">Create New Recipe</h3>
                <button onclick="closeRecipeBuilder()" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Recipe Name:</label>
                            <input type="text" id="recipeName" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g., My Special Dal">
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Category:</label>
                                <select id="recipeCategory" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <option value="dal">Dal</option>
                                    <option value="sabji">Sabji</option>
                                    <option value="sambar">Sambar</option>
                                    <option value="rice">Rice Dish</option>
                                    <option value="bread">Bread</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Total Servings:</label>
                                <input type="number" id="recipeServings" value="4" min="1" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                            </div>
                        </div>
                    </div>

                    <div class="mt-6">
                        <div class="flex justify-between items-center mb-3">
                            <h4 class="text-lg font-semibold text-gray-800">Add Ingredients:</h4>
                            <button onclick="reloadIngredientsInModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition duration-200" title="Reload ingredients if you need to refresh the list">
                                🔄 Reload Ingredients
                            </button>
                        </div>
                        <div class="space-y-3">
                            <div class="grid grid-cols-3 gap-2">
                                <select id="recipeIngredientSelect" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <option value="">Select ingredient...</option>
                                </select>
                                <select id="recipeMeasurementSelect" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" disabled>
                                    <option value="">Select ingredient first...</option>
                                </select>
                                <input type="number" id="recipeQuantity" placeholder="Qty" value="1" min="0.25" step="0.25" class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <button onclick="addRecipeIngredient()" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition duration-200">Add</button>
                            </div>
                        </div>
                    </div>

                    <div class="mt-6 space-y-3">
                        <button onclick="saveRecipe()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200">
                            Save Recipe
                        </button>
                        <button onclick="addRecipeToLog()" class="w-full bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200">
                            Save & Add to Today's Log
                        </button>
                    </div>
                </div>

                <div>
                    <h4 class="text-lg font-semibold text-gray-800 mb-3">Recipe Preview:</h4>
                    <div class="bg-gray-50 rounded-lg p-4">
                        <div id="recipePreview" class="space-y-2">
                            <p class="text-gray-500">Add ingredients to see nutritional breakdown...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // ... (Existing variables and initialization code) ...
        // Global variables
        let foodDatabase = {};
        let rawIngredients = {};
        let mealsByDate = {}; 
        let selectedDate = new Date(); 
        selectedDate.setDate(selectedDate.getDate() - 1); 
        let customRecipes = JSON.parse(localStorage.getItem('customRecipes') || '{}');
        let currentRecipeIngredients = [];
        let currentMealIngredients = [];
        let selectedMealIngredient = null;
        let databaseLoadingPromise = null; 

        // ... (Other global variables) ...

        // ... (Utility functions, Date management, Weight tracking functions etc.) ...

        // ... (populateIngredientSelect function remains same) ...

        function onRecipeIngredientChange() {
            const select = document.getElementById('recipeIngredientSelect');
            const measurementSelect = document.getElementById('recipeMeasurementSelect');
            
            if (!select.value) {
                measurementSelect.innerHTML = '<option value="">Select ingredient first...</option>';
                measurementSelect.disabled = true;
                return;
            }

            const [category, ingredientKey] = select.value.split('.');
            const ingredient = rawIngredients[category][ingredientKey];
            
            let options = '<option value="">Choose measurement...</option>';
            Object.entries(ingredient.measurements).forEach(([measurementKey, nutrition]) => {
                const displayName = measurementKey.replace(/_/g, ' ').replace(/(\d+)/, '$1 ');
                options += `<option value="${measurementKey}">${displayName}</option>`;
            });
            
            measurementSelect.innerHTML = options;
            measurementSelect.disabled = false;
        }

        // --- UPDATED FUNCTIONS START HERE ---

        function addRecipeIngredient() {
            const ingredientSelect = document.getElementById('recipeIngredientSelect');
            const measurementSelect = document.getElementById('recipeMeasurementSelect');
            const quantityInput = document.getElementById('recipeQuantity');
            
            if (!ingredientSelect.value || !measurementSelect.value || !quantityInput.value) {
                alert('Please select ingredient, measurement, and quantity');
                return;
            }

            const quantity = parseFloat(quantityInput.value);
            const [category, ingredientKey] = ingredientSelect.value.split('.');
            const ingredient = rawIngredients[category][ingredientKey];
            const measurement = ingredient.measurements[measurementSelect.value];
            
            const ingredientEntry = {
                // SAVE RAW DATA FOR EDITING
                key: ingredientSelect.value,                // e.g. "vegetables.onion"
                measurementKey: measurementSelect.value,    // e.g. "1_medium"
                quantity: quantity,                         // e.g. 2
                
                // Display data
                name: ingredient.name,
                amount: `${quantity}x ${measurementSelect.options[measurementSelect.selectedIndex].text}`,
                nutrition: {
                    calories: measurement.calories * quantity,
                    protein: measurement.protein * quantity,
                    carbs: measurement.carbs * quantity,
                    fat: measurement.fat * quantity,
                    fiber: measurement.fiber * quantity
                }
            };

            currentRecipeIngredients.push(ingredientEntry);
            
            // Clear inputs
            ingredientSelect.value = '';
            measurementSelect.innerHTML = '<option value="">Select ingredient first...</option>';
            measurementSelect.disabled = true;
            quantityInput.value = 1;
            
            updateRecipePreview();
        }

        function updateRecipePreview() {
            const preview = document.getElementById('recipePreview');
            const servings = parseInt(document.getElementById('recipeServings').value) || 4;
            
            if (currentRecipeIngredients.length === 0) {
                preview.innerHTML = '<p class="text-gray-500">Add ingredients to see nutritional breakdown...</p>';
                return;
            }
            
            // Calculate totals
            const totals = currentRecipeIngredients.reduce((acc, ing) => {
                acc.calories += ing.nutrition.calories;
                acc.protein += ing.nutrition.protein;
                acc.carbs += ing.nutrition.carbs;
                acc.fat += ing.nutrition.fat;
                acc.fiber += ing.nutrition.fiber;
                return acc;
            }, {calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0});
            
            // Per serving
            const perServing = {
                calories: Math.round(totals.calories / servings),
                protein: Math.round(totals.protein / servings * 10) / 10,
                carbs: Math.round(totals.carbs / servings * 10) / 10,
                fat: Math.round(totals.fat / servings * 10) / 10,
                fiber: Math.round(totals.fiber / servings * 10) / 10
            };
            
            preview.innerHTML = `
                <div class="space-y-3">
                    <h5 class="font-semibold text-gray-800">Ingredients:</h5>
                    ${currentRecipeIngredients.map((ing, index) => `
                        <div class="flex justify-between items-center text-sm bg-gray-50 p-2 rounded border border-gray-100">
                            <span>${ing.name} (${ing.amount})</span>
                            <div class="flex space-x-2">
                                ${/* Only show edit button if we have the raw data */ 
                                  ing.key && ing.measurementKey ? 
                                  `<button onclick="editRecipeIngredientLine(${index})" class="text-blue-500 hover:text-blue-700 font-bold" title="Edit">✏️</button>` : 
                                  ''}
                                <button onclick="removeRecipeIngredientLine(${index})" class="text-red-500 hover:text-red-700 font-bold" title="Remove">&times;</button>
                            </div>
                        </div>
                    `).join('')}
                    
                    <div class="border-t pt-3 mt-3">
                        <h5 class="font-semibold text-gray-800 mb-2">Per Serving (${servings} total):</h5>
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            <div>Calories: <span class="font-semibold">${perServing.calories}</span></div>
                            <div>Protein: <span class="font-semibold">${perServing.protein}g</span></div>
                            <div>Carbs: <span class="font-semibold">${perServing.carbs}g</span></div>
                            <div>Fat: <span class="font-semibold">${perServing.fat}g</span></div>
                            <div>Fiber: <span class="font-semibold">${perServing.fiber}g</span></div>
                        </div>
                    </div>
                </div>
            `;
        }

        // New helper functions for editing and removing ingredients by index
        function editRecipeIngredientLine(index) {
            const ing = currentRecipeIngredients[index];
            
            if (!ing.key || !ing.measurementKey) {
                alert('Cannot edit this ingredient (legacy data). Please remove and add it again.');
                return;
            }
            
            // 1. Remove from the list (it will be re-added when you click Add)
            currentRecipeIngredients.splice(index, 1);
            updateRecipePreview();
            
            // 2. Populate the Input Fields
            const ingredientSelect = document.getElementById('recipeIngredientSelect');
            const measurementSelect = document.getElementById('recipeMeasurementSelect');
            const quantityInput = document.getElementById('recipeQuantity');
            
            // Set Ingredient Dropdown
            ingredientSelect.value = ing.key;
            
            // Trigger the change event manually to load the measurements for this ingredient
            onRecipeIngredientChange(); 
            
            // Set Measurement Dropdown (must be done AFTER onRecipeIngredientChange runs)
            measurementSelect.value = ing.measurementKey;
            measurementSelect.disabled = false;
            
            // Set Quantity
            quantityInput.value = ing.quantity;
            
            // Focus the quantity box so user can quickly type
            quantityInput.focus();
        }

        function removeRecipeIngredientLine(index) {
            currentRecipeIngredients.splice(index, 1);
            updateRecipePreview();
        }

        // Legacy function kept for compatibility if needed elsewhere, though updated logic uses index
        function removeIngredient(key) {
            // Find index of first ingredient with this key (not ideal but fallback)
            const index = currentRecipeIngredients.findIndex(ing => ing.key === key);
            if(index !== -1) {
                removeRecipeIngredientLine(index);
            }
        }

        // --- UPDATED FUNCTIONS END ---

        // ... (Rest of the script continues) ...
        
        // ... (Previous addQuickDish function) ...
        function addQuickDish(dishKey) {
            // ... (Implementation same as before) ...
            console.log('🍽️ QUICKDISH: addQuickDish() called for:', dishKey);
            // ...
            const servingsElement = document.getElementById(`servings_${dishKey}`);
            // ... logic to add meal ...
            
            // (Include existing implementation here)
            // ...
            const servings = parseFloat(servingsElement.value);
            // ... database checks ...
            const allDishes = {...foodDatabase.dishes, ...customRecipes};
            const dish = allDishes[dishKey];
            if (!dish) return;

            const nutrition = dish.total_per_serving;
            const meal = {
                id: Date.now(),
                description: `${dish.name} (${servings} serving${servings !== 1 ? 's' : ''})`,
                timestamp: new Date().toISOString(),
                mealType: getSelectedMealType(), // Ensure meal type is captured if in modal
                nutrition: {
                    calories: Math.round(nutrition.calories * servings),
                    protein: Math.round(nutrition.protein * servings * 10) / 10,
                    carbs: Math.round(nutrition.carbs * servings * 10) / 10,
                    fat: Math.round(nutrition.fat * servings * 10) / 10,
                    fiber: Math.round(nutrition.fiber * servings * 10) / 10
                },
                source: 'database'
            };
            
            addMealToDate(meal);
            updateDailySummary();
            displayMeals();
            
            document.getElementById(`servings_${dishKey}`).value = 1;
            showSuccessMessage(`Added ${dish.name}!`);
        }

        // ... (Rest of existing functions: addCustomEntry, estimateCalories, etc.) ...
    </script>
</body>
</html>