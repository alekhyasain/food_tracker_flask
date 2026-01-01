#!/bin/bash

# Food Tracker Database Setup Script
# This script automates the database migration process

echo "🚀 Food Tracker Database Setup"
echo "=============================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js detected: $(node --version)"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    exit 1
fi

echo "✅ npm detected: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

# Check if database already exists
if [ -f "database/food_tracker.db" ]; then
    echo "⚠️  Database already exists at database/food_tracker.db"
    echo ""
    read -p "Do you want to recreate the database? This will overwrite existing data (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Backing up existing database..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        cp database/food_tracker.db "database/food_tracker_backup_${timestamp}.db"
        echo "✅ Backup created: database/food_tracker_backup_${timestamp}.db"
        echo ""
        
        echo "🗑️  Removing old database..."
        rm database/food_tracker.db
    else
        echo "ℹ️  Skipping database recreation"
        echo ""
        echo "🎉 Setup complete! To start the server:"
        echo "   node server-db.js"
        exit 0
    fi
fi

# Run migration
echo "🔄 Running database migration..."
echo ""
node database/migrate.js 2>&1

migration_status=$?
if [ $migration_status -ne 0 ]; then
    echo ""
    echo "❌ Migration failed with exit code $migration_status"
    echo ""
    echo "💡 Troubleshooting tips:"
    echo "  1. Make sure JSON files exist (meals.json, rawingredients.json, recipes.json)"
    echo "  2. Check that sqlite3 package is installed: npm list sqlite3"
    echo "  3. Try running manually: node database/migrate.js"
    echo "  4. Check console output above for specific error"
    exit 1
fi

echo ""
echo "✨ Setup Complete!"
echo "=================="
echo ""
echo "Your Food Tracker is now using a SQLite database with AI assistant features!"
echo ""
echo "📋 What was done:"
echo "  ✅ Installed dependencies (including sqlite3)"
echo "  ✅ Created database at database/food_tracker.db"
echo "  ✅ Migrated all ingredients, recipes, and meals"
echo "  ✅ Set up AI assistant backend"
echo ""
echo "🚀 To start the server:"
echo "   node server-db.js"
echo ""
echo "🌐 Then open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "🤖 AI Assistant Features:"
echo "  • Click the purple button (bottom-right) to open AI assistant"
echo "  • Get daily nutrition analysis"
echo "  • Track weekly progress"
echo "  • Receive personalized recommendations"
echo ""
echo "📖 For more information, see database/README.md"
echo ""
