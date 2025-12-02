// Frontend Testing Script for Food Diary Application
// This script tests all major frontend functionality

console.log('🧪 Starting Frontend Testing Suite...');

// Test 1: Check if all required elements exist
function testElementsExist() {
    console.log('\n📋 Test 1: Checking if all required elements exist...');
    
    const requiredElements = [
        'dateSelector',
        'selectedDateDisplay',
        'dailySummaryTitle',
        'totalCalories',
        'mealCount',
        'totalProtein',
        'totalFiber',
        'foodLog',
        'quickDishes',
        'customDish',
        'customServings',
        'customCalories',
        'recipeModal',
        'ingredientModal',
        'mealModal',
        'exportModal'
    ];
    
    let missingElements = [];
    requiredElements.forEach(id => {
        const element = document.getElementById(id);
        if (!element) {
            missingElements.push(id);
        }
    });
    
    if (missingElements.length === 0) {
        console.log('✅ All required elements found');
        return true;
    } else {
        console.log('❌ Missing elements:', missingElements);
        return false;
    }
}

// Test 2: Test date navigation functionality
function testDateNavigation() {
    console.log('\n📅 Test 2: Testing date navigation...');
    
    try {
        // Test date selector
        const dateSelector = document.getElementById('dateSelector');
        const today = new Date();
        const todayString = today.toISOString().split('T')[0];
        
        if (dateSelector.value === todayString) {
            console.log('✅ Date selector initialized to today');
        } else {
            console.log('⚠️ Date selector not set to today:', dateSelector.value);
        }
        
        // Test date display
        const dateDisplay = document.getElementById('selectedDateDisplay');
        if (dateDisplay.textContent.length > 0) {
            console.log('✅ Date display showing:', dateDisplay.textContent);
        } else {
            console.log('❌ Date display is empty');
        }
        
        return true;
    } catch (error) {
        console.log('❌ Date navigation test failed:', error.message);
        return false;
    }
}

// Test 3: Test modal functionality
function testModals() {
    console.log('\n🪟 Test 3: Testing modal functionality...');
    
    const modals = [
        { id: 'recipeModal', openFunction: 'openRecipeBuilder', closeFunction: 'closeRecipeBuilder' },
        { id: 'ingredientModal', openFunction: 'openIngredientModal', closeFunction: 'closeIngredientModal' },
        { id: 'mealModal', openFunction: 'openMealBuilder', closeFunction: 'closeMealBuilder' },
        { id: 'exportModal', openFunction: 'openExportModal', closeFunction: 'closeExportModal' }
    ];
    
    let allModalsPassed = true;
    
    modals.forEach(modal => {
        try {
            const modalElement = document.getElementById(modal.id);
            
            // Test if modal exists
            if (!modalElement) {
                console.log(`❌ Modal ${modal.id} not found`);
                allModalsPassed = false;
                return;
            }
            
            // Test if modal has correct classes
            if (modalElement.classList.contains('modal')) {
                console.log(`✅ Modal ${modal.id} has correct structure`);
            } else {
                console.log(`⚠️ Modal ${modal.id} missing 'modal' class`);
            }
            
            // Test if open/close functions exist
            if (typeof window[modal.openFunction] === 'function') {
                console.log(`✅ ${modal.openFunction} function exists`);
            } else {
                console.log(`❌ ${modal.openFunction} function missing`);
                allModalsPassed = false;
            }
            
            if (typeof window[modal.closeFunction] === 'function') {
                console.log(`✅ ${modal.closeFunction} function exists`);
            } else {
                console.log(`❌ ${modal.closeFunction} function missing`);
                allModalsPassed = false;
            }
            
        } catch (error) {
            console.log(`❌ Error testing modal ${modal.id}:`, error.message);
            allModalsPassed = false;
        }
    });
    
    return allModalsPassed;
}

// Test 4: Test data loading and ingredient population
function testDataLoading() {
    console.log('\n📊 Test 4: Testing data loading...');
    
    try {
        // Check if rawIngredients is loaded
        if (typeof rawIngredients !== 'undefined' && rawIngredients) {
            const categories = Object.keys(rawIngredients);
            console.log('✅ Raw ingredients loaded with categories:', categories);
            
            // Count total ingredients
            let totalIngredients = 0;
            categories.forEach(category => {
                totalIngredients += Object.keys(rawIngredients[category]).length;
            });
            console.log(`✅ Total ingredients loaded: ${totalIngredients}`);
            
            // Check if lauki is present (specific test case)
            if (rawIngredients.vegetables && rawIngredients.vegetables.lauki) {
                console.log('✅ Lauki ingredient found in vegetables');
            } else {
                console.log('⚠️ Lauki ingredient not found');
            }
            
        } else {
            console.log('❌ Raw ingredients not loaded');
            return false;
        }
        
        // Check if foodDatabase is loaded
        if (typeof foodDatabase !== 'undefined' && foodDatabase) {
            console.log('✅ Food database loaded');
        } else {
            console.log('⚠️ Food database not loaded or using fallback');
        }
        
        return true;
    } catch (error) {
        console.log('❌ Data loading test failed:', error.message);
        return false;
    }
}

// Test 5: Test meal storage system
function testMealStorage() {
    console.log('\n💾 Test 5: Testing meal storage system...');
    
    try {
        // Check if mealsByDate is initialized
        if (typeof mealsByDate !== 'undefined') {
            console.log('✅ mealsByDate storage initialized');
            console.log('📊 Current meal data keys:', Object.keys(mealsByDate));
        } else {
            console.log('❌ mealsByDate not initialized');
            return false;
        }
        
        // Check localStorage functionality
        try {
            const testKey = 'test_storage_' + Date.now();
            const testData = { test: true };
            localStorage.setItem(testKey, JSON.stringify(testData));
            const retrieved = JSON.parse(localStorage.getItem(testKey));
            localStorage.removeItem(testKey);
            
            if (retrieved && retrieved.test === true) {
                console.log('✅ localStorage functionality working');
            } else {
                console.log('❌ localStorage test failed');
                return false;
            }
        } catch (error) {
            console.log('❌ localStorage not available:', error.message);
            return false;
        }
        
        return true;
    } catch (error) {
        console.log('❌ Meal storage test failed:', error.message);
        return false;
    }
}

// Test 6: Test server connectivity
async function testServerConnectivity() {
    console.log('\n🌐 Test 6: Testing server connectivity...');
    
    try {
        // Test ingredients endpoint
        const response = await fetch('/api/ingredients');
        if (response.ok) {
            console.log('✅ Server ingredients endpoint accessible');
            const data = await response.json();
            if (data.basic_ingredients) {
                console.log('✅ Ingredients data structure correct');
            } else {
                console.log('❌ Ingredients data structure incorrect');
                return false;
            }
        } else {
            console.log('❌ Server ingredients endpoint failed:', response.status);
            return false;
        }
        
        // Test categories endpoint
        const categoriesResponse = await fetch('/api/categories');
        if (categoriesResponse.ok) {
            console.log('✅ Server categories endpoint accessible');
            const categoriesData = await categoriesResponse.json();
            if (categoriesData.categories && Array.isArray(categoriesData.categories)) {
                console.log('✅ Categories data structure correct:', categoriesData.categories);
            } else {
                console.log('❌ Categories data structure incorrect');
                return false;
            }
        } else {
            console.log('❌ Server categories endpoint failed:', categoriesResponse.status);
            return false;
        }
        
        return true;
    } catch (error) {
        console.log('❌ Server connectivity test failed:', error.message);
        return false;
    }
}

// Test 7: Test utility functions
function testUtilityFunctions() {
    console.log('\n🔧 Test 7: Testing utility functions...');
    
    const utilityFunctions = [
        'formatDateKey',
        'formatDateDisplay',
        'updateDateDisplay',
        'updateDailySummary',
        'displayMeals',
        'addMealToDate',
        'getCurrentDateMeals',
        'showSuccessMessage'
    ];
    
    let allFunctionsPassed = true;
    
    utilityFunctions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`✅ ${funcName} function exists`);
        } else {
            console.log(`❌ ${funcName} function missing`);
            allFunctionsPassed = false;
        }
    });
    
    // Test formatDateKey function
    try {
        const testDate = new Date('2025-12-03');
        const formatted = formatDateKey(testDate);
        if (formatted === '2025-12-03') {
            console.log('✅ formatDateKey working correctly');
        } else {
            console.log('❌ formatDateKey incorrect output:', formatted);
            allFunctionsPassed = false;
        }
    } catch (error) {
        console.log('❌ formatDateKey test failed:', error.message);
        allFunctionsPassed = false;
    }
    
    return allFunctionsPassed;
}

// Main test runner
async function runAllTests() {
    console.log('🚀 Running comprehensive frontend test suite...\n');
    
    const tests = [
        { name: 'Elements Exist', func: testElementsExist },
        { name: 'Date Navigation', func: testDateNavigation },
        { name: 'Modals', func: testModals },
        { name: 'Data Loading', func: testDataLoading },
        { name: 'Meal Storage', func: testMealStorage },
        { name: 'Server Connectivity', func: testServerConnectivity },
        { name: 'Utility Functions', func: testUtilityFunctions }
    ];
    
    let passedTests = 0;
    let totalTests = tests.length;
    
    for (const test of tests) {
        try {
            const result = await test.func();
            if (result) {
                passedTests++;
                console.log(`\n✅ ${test.name} test PASSED`);
            } else {
                console.log(`\n❌ ${test.name} test FAILED`);
            }
        } catch (error) {
            console.log(`\n💥 ${test.name} test ERROR:`, error.message);
        }
    }
    
    console.log('\n' + '='.repeat(50));
    console.log(`📊 TEST SUMMARY: ${passedTests}/${totalTests} tests passed`);
    console.log('='.repeat(50));
    
    if (passedTests === totalTests) {
        console.log('🎉 ALL TESTS PASSED! Frontend is working correctly.');
    } else {
        console.log(`⚠️ ${totalTests - passedTests} test(s) failed. Review the issues above.`);
    }
    
    return { passed: passedTests, total: totalTests };
}

// Auto-run tests when script loads
if (typeof window !== 'undefined') {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runAllTests);
    } else {
        // DOM is already ready
        setTimeout(runAllTests, 1000); // Give app time to initialize
    }
}

// Export for manual testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runAllTests };
}