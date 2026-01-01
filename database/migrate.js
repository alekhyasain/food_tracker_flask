const sqlite3 = require('sqlite3').verbose();
const fs = require('fs').promises;
const path = require('path');

class DatabaseMigration {
    constructor(dbPath = './database/food_tracker.db') {
        this.dbPath = dbPath;
        this.db = null;
    }

    // Initialize database connection
    async connect() {
        return new Promise((resolve, reject) => {
            this.db = new sqlite3.Database(this.dbPath, (err) => {
                if (err) {
                    console.error('❌ Error connecting to database:', err);
                    reject(err);
                } else {
                    console.log('✅ Connected to SQLite database');
                    resolve();
                }
            });
        });
    }

    // Run SQL query
    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, params, function(err) {
                if (err) reject(err);
                else resolve(this);
            });
        });
    }

    // Get all rows
    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }

    // Create tables from schema
    async createTables() {
        console.log('📋 Creating database tables...');
        const schemaPath = path.join(__dirname, 'schema.sql');
        const schema = await fs.readFile(schemaPath, 'utf8');
        
        // Split schema by semicolons but handle triggers (which have semicolons inside)
        // Use a more sophisticated split that respects BEGIN...END blocks
        const statements = [];
        let currentStatement = '';
        let insideTrigger = false;
        
        const lines = schema.split('\n');
        for (const line of lines) {
            currentStatement += line + '\n';
            
            // Check if we're entering a trigger
            if (line.trim().match(/^CREATE TRIGGER/i)) {
                insideTrigger = true;
            }
            
            // Check if we're exiting a trigger
            if (insideTrigger && line.trim().match(/^END;/i)) {
                insideTrigger = false;
                statements.push(currentStatement.trim());
                currentStatement = '';
                continue;
            }
            
            // For non-trigger statements, split on semicolon
            if (!insideTrigger && line.includes(';') && !line.trim().startsWith('--')) {
                statements.push(currentStatement.trim());
                currentStatement = '';
            }
        }
        
        // Add any remaining statement
        if (currentStatement.trim()) {
            statements.push(currentStatement.trim());
        }
        
        // Execute each statement
        for (const statement of statements) {
            if (statement && statement.length > 5) { // Ignore very short statements
                try {
                    await this.run(statement);
                } catch (error) {
                    console.error(`Error executing statement: ${statement.substring(0, 50)}...`);
                    throw error;
                }
            }
        }
        
        console.log('✅ Tables created successfully');
    }

    // Migrate ingredients from rawingredients.json
    async migrateIngredients() {
        console.log('🥦 Migrating ingredients...');
        
        const data = await fs.readFile('./rawingredients.json', 'utf8');
        const ingredientsData = JSON.parse(data);
        
        let totalIngredients = 0;
        let totalMeasurements = 0;

        for (const [categoryName, ingredients] of Object.entries(ingredientsData.basic_ingredients)) {
            // Insert category
            const categoryResult = await this.run(
                'INSERT OR IGNORE INTO categories (name) VALUES (?)',
                [categoryName]
            );
            
            // Get category ID
            const category = await this.all(
                'SELECT id FROM categories WHERE name = ?',
                [categoryName]
            );
            const categoryId = category[0].id;

            // Insert ingredients
            for (const [key, ingredient] of Object.entries(ingredients)) {
                const ingredientResult = await this.run(
                    'INSERT OR IGNORE INTO ingredients (category_id, key, name) VALUES (?, ?, ?)',
                    [categoryId, key, ingredient.name]
                );
                
                // Get ingredient ID
                const ing = await this.all(
                    'SELECT id FROM ingredients WHERE category_id = ? AND key = ?',
                    [categoryId, key]
                );
                const ingredientId = ing[0].id;
                totalIngredients++;

                // Insert measurements
                if (ingredient.measurements) {
                    for (const [measureKey, nutrition] of Object.entries(ingredient.measurements)) {
                        await this.run(
                            `INSERT OR REPLACE INTO ingredient_measurements 
                            (ingredient_id, measurement_key, calories, protein, carbs, fat, fiber) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)`,
                            [
                                ingredientId,
                                measureKey,
                                nutrition.calories || 0,
                                nutrition.protein || 0,
                                nutrition.carbs || 0,
                                nutrition.fat || 0,
                                nutrition.fiber || 0
                            ]
                        );
                        totalMeasurements++;
                    }
                }
            }
        }
        
        console.log(`✅ Migrated ${totalIngredients} ingredients with ${totalMeasurements} measurements`);
    }

    // Migrate recipes from recipes.json
    async migrateRecipes() {
        console.log('🍳 Migrating recipes...');
        
        const data = await fs.readFile('./recipes.json', 'utf8');
        const recipesData = JSON.parse(data);
        
        let totalRecipes = 0;
        let totalRecipeIngredients = 0;

        if (recipesData.dishes) {
            for (const [key, recipe] of Object.entries(recipesData.dishes)) {
                // Insert recipe
                const recipeResult = await this.run(
                    `INSERT OR REPLACE INTO recipes (key, name, category, servings) 
                    VALUES (?, ?, ?, ?)`,
                    [key, recipe.name, recipe.category || null, recipe.servings || 1]
                );
                
                // Get recipe ID
                const rec = await this.all('SELECT id FROM recipes WHERE key = ?', [key]);
                const recipeId = rec[0].id;
                totalRecipes++;

                // Insert recipe nutrition (total per serving)
                if (recipe.total_per_serving) {
                    await this.run(
                        `INSERT OR REPLACE INTO recipe_nutrition 
                        (recipe_id, calories, protein, carbs, fat, fiber) 
                        VALUES (?, ?, ?, ?, ?, ?)`,
                        [
                            recipeId,
                            recipe.total_per_serving.calories || 0,
                            recipe.total_per_serving.protein || 0,
                            recipe.total_per_serving.carbs || 0,
                            recipe.total_per_serving.fat || 0,
                            recipe.total_per_serving.fiber || 0
                        ]
                    );
                }

                // Insert recipe ingredients
                if (recipe.ingredients && Array.isArray(recipe.ingredients)) {
                    for (const ingredient of recipe.ingredients) {
                        await this.run(
                            `INSERT INTO recipe_ingredients 
                            (recipe_id, ingredient_key, ingredient_name, amount, calories, protein, carbs, fat, fiber) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                            [
                                recipeId,
                                ingredient.key || '',
                                ingredient.name || '',
                                ingredient.amount || '',
                                ingredient.nutrition?.calories || 0,
                                ingredient.nutrition?.protein || 0,
                                ingredient.nutrition?.carbs || 0,
                                ingredient.nutrition?.fat || 0,
                                ingredient.nutrition?.fiber || 0
                            ]
                        );
                        totalRecipeIngredients++;
                    }
                }
            }
        }
        
        console.log(`✅ Migrated ${totalRecipes} recipes with ${totalRecipeIngredients} ingredients`);
    }

    // Migrate meals from meals.json
    async migrateMeals() {
        console.log('🍽️  Migrating meals...');
        
        const data = await fs.readFile('./meals.json', 'utf8');
        const mealsData = JSON.parse(data);
        
        let totalMeals = 0;

        for (const [date, meals] of Object.entries(mealsData)) {
            if (Array.isArray(meals)) {
                for (const meal of meals) {
                    const ingredientData = meal.ingredient_data ? JSON.stringify(meal.ingredient_data) : null;
                    
                    await this.run(
                        `INSERT OR REPLACE INTO meals 
                        (id, description, meal_type, date, timestamp, source, 
                         calories, protein, carbs, fat, fiber, ingredient_data) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                        [
                            meal.id,
                            meal.description || '',
                            meal.mealType || '',
                            meal.date || date,
                            meal.timestamp || new Date().toISOString(),
                            meal.source || '',
                            meal.nutrition?.calories || 0,
                            meal.nutrition?.protein || 0,
                            meal.nutrition?.carbs || 0,
                            meal.nutrition?.fat || 0,
                            meal.nutrition?.fiber || 0,
                            ingredientData
                        ]
                    );
                    totalMeals++;
                }
            }
        }
        
        console.log(`✅ Migrated ${totalMeals} meals`);
    }

    // Migrate tracker JSON files
    async migrateTrackerFiles() {
        console.log('📊 Migrating tracker JSON files...');
        
        const trackerDir = './tracker_json';
        const files = await fs.readdir(trackerDir);
        const jsonFiles = files.filter(f => f.endsWith('.json') && f !== '.gitkeep');
        
        let totalEntries = 0;

        for (const file of jsonFiles) {
            const filePath = path.join(trackerDir, file);
            const data = await fs.readFile(filePath, 'utf8');
            
            try {
                const trackerData = JSON.parse(data);
                
                // Check if it has meals array or is organized by date
                if (Array.isArray(trackerData)) {
                    for (const meal of trackerData) {
                        const ingredientData = meal.ingredient_data ? JSON.stringify(meal.ingredient_data) : null;
                        
                        await this.run(
                            `INSERT OR REPLACE INTO meals 
                            (id, description, meal_type, date, timestamp, source, 
                             calories, protein, carbs, fat, fiber, ingredient_data) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                            [
                                meal.id,
                                meal.description || '',
                                meal.mealType || '',
                                meal.date || '',
                                meal.timestamp || new Date().toISOString(),
                                meal.source || '',
                                meal.nutrition?.calories || 0,
                                meal.nutrition?.protein || 0,
                                meal.nutrition?.carbs || 0,
                                meal.nutrition?.fat || 0,
                                meal.nutrition?.fiber || 0,
                                ingredientData
                            ]
                        );
                        totalEntries++;
                    }
                } else if (typeof trackerData === 'object') {
                    // Handle object format with date keys
                    for (const [date, meals] of Object.entries(trackerData)) {
                        if (Array.isArray(meals)) {
                            for (const meal of meals) {
                                const ingredientData = meal.ingredient_data ? JSON.stringify(meal.ingredient_data) : null;
                                
                                await this.run(
                                    `INSERT OR REPLACE INTO meals 
                                    (id, description, meal_type, date, timestamp, source, 
                                     calories, protein, carbs, fat, fiber, ingredient_data) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                                    [
                                        meal.id,
                                        meal.description || '',
                                        meal.mealType || '',
                                        meal.date || date,
                                        meal.timestamp || new Date().toISOString(),
                                        meal.source || '',
                                        meal.nutrition?.calories || 0,
                                        meal.nutrition?.protein || 0,
                                        meal.nutrition?.carbs || 0,
                                        meal.nutrition?.fat || 0,
                                        meal.nutrition?.fiber || 0,
                                        ingredientData
                                    ]
                                );
                                totalEntries++;
                            }
                        }
                    }
                }
            } catch (error) {
                console.error(`⚠️  Error processing ${file}:`, error.message);
            }
        }
        
        console.log(`✅ Migrated ${totalEntries} entries from tracker files`);
    }

    // Close database connection
    close() {
        return new Promise((resolve, reject) => {
            this.db.close((err) => {
                if (err) reject(err);
                else {
                    console.log('✅ Database connection closed');
                    resolve();
                }
            });
        });
    }

    // Run full migration
    async migrate() {
        try {
            console.log('🚀 Starting database migration...\n');
            
            await this.connect();
            await this.createTables();
            await this.migrateIngredients();
            await this.migrateRecipes();
            await this.migrateMeals();
            await this.migrateTrackerFiles();
            await this.close();
            
            console.log('\n✨ Migration completed successfully!');
            console.log('📁 Database created at:', this.dbPath);
        } catch (error) {
            console.error('❌ Migration failed:', error);
            if (this.db) {
                await this.close();
            }
            throw error;
        }
    }
}

// Run migration if executed directly
if (require.main === module) {
    const migration = new DatabaseMigration();
    migration.migrate()
        .then(() => process.exit(0))
        .catch((err) => {
            console.error(err);
            process.exit(1);
        });
}

module.exports = DatabaseMigration;
