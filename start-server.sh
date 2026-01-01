#!/bin/bash

# Food Tracker Startup Script with Gemini AI

echo "🚀 Starting Food Tracker with AI Assistant..."
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not found in environment"
    echo ""
    echo "To enable AI chat with Gemini:"
    echo "1. Get your API key from: https://makersuite.google.com/app/apikey"
    echo "2. Run: export GEMINI_API_KEY='your_key_here'"
    echo "3. Or create a .env file with your key"
    echo ""
    echo "Starting server without Gemini (fallback mode)..."
    echo ""
else
    echo "✅ GEMINI_API_KEY found - AI chat enabled!"
    echo ""
fi

# Start the server
node server-db.js
