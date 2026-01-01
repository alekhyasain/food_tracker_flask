# Setting Up Gemini AI Chat

Your food tracker now has an AI-powered chatbot using Google's Gemini API!

## Quick Setup

### 1. Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure the API Key

**Option A: Using Environment Variable (Recommended)**

```bash
# On macOS/Linux:
export GEMINI_API_KEY="your_api_key_here"
node server-db.js

# Or create a .env file:
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

**Option B: Direct Configuration**

Edit `server-db.js` line 11 and replace `YOUR_API_KEY_HERE` with your actual key:
```javascript
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || 'your_actual_key_here';
```

### 3. Restart the Server

```bash
# Stop the current server (Ctrl+C if running)
# Then start with API key:
GEMINI_API_KEY="your_key" node server-db.js
```

You should see: `✅ Gemini AI initialized`

### 4. Start Chatting!

Open your food tracker, click the AI assistant button (bottom right), and start asking questions naturally:

- "How's my protein intake today?"
- "Should I eat more fiber?"
- "Give me suggestions for a healthy snack"
- "What does my nutrition look like this week?"
- "How can I improve my diet?"

## Features

✅ **Natural Conversations** - Ask questions in plain English  
✅ **Context-Aware** - Gemini knows your current nutrition data  
✅ **Personalized Advice** - Get suggestions based on your actual meals  
✅ **Smart Fallback** - Works without API key using pattern matching  

## Troubleshooting

**"I'm currently unavailable" message?**
- Your API key isn't set or is invalid
- Check that GEMINI_API_KEY environment variable is set
- Verify your API key is active at [Google AI Studio](https://makersuite.google.com/app/apikey)

**Rate limits?**
- Free tier: 60 requests per minute
- If you hit limits, wait a minute or upgrade your API plan

**Chat not responding?**
- Check browser console (F12) for errors
- Ensure server is running on port 3000
- Verify internet connection

## API Key Security

⚠️ **Never commit your API key to Git!**

The `.gitignore` file should already exclude `.env` files. If setting the key directly in code, make sure to:
1. Never push to public repositories
2. Use environment variables for production
3. Rotate keys if accidentally exposed

## Cost

Gemini API is **FREE** for:
- 60 requests per minute
- 1,500 requests per day
- Perfect for personal use!

For higher limits, check [Google AI pricing](https://ai.google.dev/pricing).

---

Need help? The chatbot now understands natural language, so just ask! 🤖✨
