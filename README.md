# Indian Food Diary - Ingredient Management System

A comprehensive food tracking application with ingredient management capabilities for Indian cuisine.

## Features

### Core Functionality
- **Volume-Based Tracking**: Track food using simple measurements like cups, tablespoons, etc.
- **Pre-made Dishes**: Quick add popular Indian dishes with accurate nutritional data
- **Custom Entries**: Add custom meals with automatic calorie estimation
- **Recipe Builder**: Create custom recipes with precise nutritional calculations
- **Daily Summary**: Track calories, protein, fiber, and meal count

### New Ingredient Management
- **Add New Ingredients**: Add ingredients with multiple measurement options
- **Edit Existing Ingredients**: Modify ingredient data and nutritional information
- **Delete Ingredients**: Remove ingredients from the database
- **Category Management**: Organize ingredients by categories (grains, vegetables, spices, etc.)
- **Real-time Updates**: Changes are immediately reflected in the recipe builder

## Installation & Setup

### Prerequisites
- Node.js (version 14 or higher)
- npm (comes with Node.js)

### Installation Steps

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start the Server**
   ```bash
   npm start
   ```
   
   Or for development with auto-restart:
   ```bash
   npm run dev
   ```

3. **Access the Application**
   - Open your browser and go to: `http://localhost:3000`
   - The application will serve the HTML file and provide API endpoints

## Usage Guide

### Basic Food Tracking
1. **Quick Add Dishes**: Use the pre-made dishes section to quickly add common Indian foods
2. **Custom Entries**: Add custom meals with descriptions and optional calorie counts
3. **Recipe Builder**: Create detailed recipes with specific ingredients and measurements

### Ingredient Management

#### Adding New Ingredients
1. Click the **"🥬 Manage Ingredients"** button in the header
2. Fill in the ingredient details:
   - **Name**: Enter the ingredient name (e.g., "Bitter Gourd")
   - **Category**: Select appropriate category
   - **Measurements**: Add one or more measurement options with nutritional data
3. Click **"Save Ingredient"** to add to the database

#### Editing Ingredients
1. Open the ingredient management modal
2. Use the category filter to find ingredients
3. Click **"Edit"** on any ingredient
4. Modify the data and click **"Update Ingredient"**

#### Deleting Ingredients
1. Find the ingredient in the management modal
2. Click **"Delete"** and confirm the action
3. The ingredient will be removed from the database

### Measurement Format
When adding measurements, use the following format:
- **Measurement Key**: `1_cup_chopped`, `1_tbsp`, `1_medium`, etc.
- **Display Name**: Human-readable format like "1 cup chopped"

### Nutritional Data
For each measurement, provide:
- **Calories**: Total calories for that measurement
- **Protein**: Protein content in grams
- **Carbs**: Carbohydrate content in grams
- **Fat**: Fat content in grams
- **Fiber**: Fiber content in grams

## API Endpoints

The server provides the following REST API endpoints:

### Ingredients
- `GET /api/ingredients` - Get all ingredients
- `POST /api/ingredients` - Add new ingredient
- `PUT /api/ingredients/:category/:key` - Update existing ingredient
- `DELETE /api/ingredients/:category/:key` - Delete ingredient
- `GET /api/categories` - Get available categories

### Request Format for Adding Ingredients
```json
{
  "category": "vegetables",
  "ingredientKey": "bitter_gourd",
  "ingredientData": {
    "name": "Bitter Gourd",
    "measurements": {
      "1_cup_chopped": {
        "calories": 17,
        "protein": 1,
        "carbs": 3.7,
        "fat": 0.2,
        "fiber": 2.6
      }
    }
  }
}
```

## File Structure

```
food_diary/
├── server.js                 # Express server with API endpoints
├── package.json              # Node.js dependencies and scripts
├── indian_food_tracker.html  # Main application interface
├── rawingredients.json       # Ingredient database
├── recipes.json              # Recipe database
└── README.md                 # This file
```

## Data Storage

- **Ingredients**: Stored in `rawingredients.json` with hierarchical structure
- **Recipes**: Pre-made dishes stored in `recipes.json`
- **Custom Recipes**: Saved in browser localStorage
- **Daily Meals**: Saved in browser localStorage

## Categories

The system supports the following ingredient categories:
- **Grains**: Rice, wheat flour, quinoa, etc.
- **Dals & Legumes**: Toor dal, moong dal, chickpeas, etc.
- **Vegetables**: Onions, tomatoes, leafy greens, etc.
- **Spices & Seasonings**: Turmeric, cumin, garam masala, etc.
- **Oils & Fats**: Cooking oil, ghee, etc.
- **Other**: Miscellaneous ingredients

## Error Handling

The system includes comprehensive error handling:
- **Server Connectivity**: Checks if server is running before allowing ingredient management
- **Validation**: Ensures all required fields are filled
- **User Feedback**: Shows success/error messages for all operations
- **Fallback Data**: Uses embedded data if server is unavailable

## Development

### Adding New Features
1. **Backend**: Add new API endpoints in `server.js`
2. **Frontend**: Add corresponding JavaScript functions in the HTML file
3. **UI**: Use existing Tailwind CSS classes for consistent styling

### Database Schema
The ingredient database follows this structure:
```json
{
  "basic_ingredients": {
    "category_name": {
      "ingredient_key": {
        "name": "Display Name",
        "measurements": {
          "measurement_key": {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0
          }
        }
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **"Ingredient management requires the server to be running"**
   - Make sure you've run `npm start` to start the server
   - Check that the server is running on port 3000

2. **Changes not reflecting**
   - Click the "🔄 Reload Ingredients" button to refresh the data
   - Check the browser console for any error messages

3. **Server won't start**
   - Ensure Node.js is installed: `node --version`
   - Install dependencies: `npm install`
   - Check if port 3000 is already in use

### Browser Compatibility
- Modern browsers with ES6+ support
- JavaScript must be enabled
- Local storage must be available

## Contributing

When adding new ingredients or features:
1. Follow the existing naming conventions
2. Use consistent measurement formats
3. Provide accurate nutritional data
4. Test thoroughly before committing changes

## License

MIT License - Feel free to use and modify as needed.