# Food Tracker - Deployment Guide

This guide covers multiple options for deploying your Food Tracker Flask app publicly.

## Prerequisites

1. GitHub repository: `https://github.com/alekhyasain/food_tracker_flask`
2. Gemini API key from Google AI Studio
3. SQLite database will be created automatically

---

## Option 1: Render.com (Recommended - Free Tier Available)

### Steps:

1. **Sign up at [Render.com](https://render.com)**

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `alekhyasain/food_tracker_flask`
   - Configure:
     - Name: `food-tracker-flask`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app`

3. **Add Environment Variable**
   - Go to "Environment" tab
   - Add: `GEMINI_API_KEY` = `your_actual_api_key`

4. **Deploy**
   - Click "Create Web Service"
   - Your app will be live at: `https://food-tracker-flask.onrender.com`

### Pros:
- ✅ Free tier available
- ✅ Auto-deploys on git push
- ✅ Persistent storage for SQLite
- ✅ Easy setup

### Cons:
- ⚠️ Free tier spins down after inactivity (30-60s cold start)

---

## Option 2: PythonAnywhere (Good for Simple Apps)

### Steps:

1. **Sign up at [PythonAnywhere](https://www.pythonanywhere.com)**

2. **Upload Code**
   - Go to "Files" tab
   - Upload your project files or clone from GitHub

3. **Create Web App**
   - Go to "Web" tab → "Add a new web app"
   - Choose "Flask"
   - Python version: 3.11

4. **Configure WSGI**
   - Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
   ```python
   import sys
   path = '/home/yourusername/food_tracker_flask'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

5. **Set Environment Variable**
   - In bash console: `export GEMINI_API_KEY='your_key'`
   - Or add to `.env` file

6. **Reload Web App**

### Pros:
- ✅ Simple interface
- ✅ Always-on (no cold starts)
- ✅ Free tier for beginners

### Cons:
- ⚠️ Limited resources on free tier
- ⚠️ Manual deployments

---

## Option 3: Railway.app (Modern Platform)

### Steps:

1. **Sign up at [Railway.app](https://railway.app)**

2. **New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `alekhyasain/food_tracker_flask`

3. **Add Variables**
   - Go to "Variables" tab
   - Add: `GEMINI_API_KEY`
   - Railway auto-detects Python and runs your app

4. **Generate Domain**
   - Go to "Settings" → "Generate Domain"
   - Your app will be live at: `https://food-tracker-flask.up.railway.app`

### Pros:
- ✅ $5 free credit/month
- ✅ Fast deployments
- ✅ Modern interface
- ✅ Database support

### Cons:
- ⚠️ Requires credit card after trial

---

## Option 4: Vercel (Serverless)

### Steps:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd /path/to/food_tracker_flask
   vercel
   ```

3. **Add Environment Variable**
   ```bash
   vercel env add GEMINI_API_KEY
   ```
   Enter your API key when prompted.

4. **Production Deploy**
   ```bash
   vercel --prod
   ```

### Pros:
- ✅ Fast edge network
- ✅ Auto-scaling
- ✅ Free tier generous

### Cons:
- ⚠️ Serverless (10s function timeout on free tier)
- ⚠️ SQLite doesn't persist (need to use external DB)

---

## Option 5: Heroku (Classic Choice)

### Steps:

1. **Install Heroku CLI**
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create food-tracker-flask
   ```

3. **Set Environment Variable**
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Open App**
   ```bash
   heroku open
   ```

### Pros:
- ✅ Reliable platform
- ✅ Good documentation
- ✅ Add-ons available

### Cons:
- ⚠️ No free tier anymore ($5/month minimum)
- ⚠️ Requires credit card

---

## Required Changes for Production

### 1. Update requirements.txt
Add `gunicorn` for production server:

```bash
echo "gunicorn>=21.0.0" >> requirements.txt
```

### 2. Install gunicorn locally (optional, for testing)
```bash
pip install gunicorn
gunicorn app:app
```

### 3. Database Considerations

**For SQLite (simple apps):**
- Works on Render, PythonAnywhere, Railway
- Data persists between deployments

**For serverless (Vercel):**
- Use PostgreSQL, MySQL, or MongoDB
- Add database connection in `db_service.py`

---

## My Recommendation

For your food tracker app, I recommend **Render.com** because:

1. ✅ **Free tier** - No credit card needed to start
2. ✅ **Persistent storage** - SQLite database stays between deployments
3. ✅ **Auto-deploy** - Push to GitHub → automatically deploys
4. ✅ **Easy setup** - No complex configuration
5. ✅ **Good for demos** - Perfect for portfolio projects

### Quick Start with Render:

1. Push code to GitHub (already done ✅)
2. Sign up at render.com
3. Connect GitHub repo
4. Add `GEMINI_API_KEY` environment variable
5. Deploy!

**Your app will be live in 5 minutes!**

---

## Testing Locally Before Deploy

```bash
# Install gunicorn
pip install gunicorn

# Test production server locally
gunicorn app:app

# Visit http://localhost:8000
```

---

## Security Notes

⚠️ **Never commit your GEMINI_API_KEY to git!**
- Always use environment variables
- The key is already in `.gitignore`
- Add it through the hosting platform's dashboard

---

## Need Help?

- **Render Issues**: Check logs in dashboard
- **Database Issues**: Verify SQLite file permissions
- **API Key Issues**: Check environment variables are set correctly

Good luck with your deployment! 🚀
