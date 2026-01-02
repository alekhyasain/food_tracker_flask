#!/bin/bash

# Food Tracker Python Setup Script

echo "🍽️  Food Tracker - Python Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup completed!"
echo ""
echo "To use the Food Tracker:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your Gemini API key (optional but recommended):"
echo "   export GEMINI_API_KEY='your_api_key_here'"
echo ""
echo "3. Start the Flask API server:"
echo "   python app.py"
echo ""
echo "4. Or use the CLI tool:"
echo "   python cli.py --help"
echo ""
echo "Examples:"
echo "  python cli.py add-meal 'Breakfast smoothie' breakfast --calories 350 --protein 15"
echo "  python cli.py list-meals"
echo "  python cli.py summary"
echo "  python cli.py analyze"
echo ""
