# Windows Setup Guide - Food Diary

## Quick Checklist

- [ ] Node.js installed (check: `node --version`)
- [ ] npm working (check: `npm --version`)
- [ ] Git installed (check: `git --version`)
- [ ] Port 3000 available
- [ ] File permissions correct

## Step-by-Step Windows Setup

### Step 1: Install Node.js

1. Download from https://nodejs.org/
   - **Recommended**: LTS (Long Term Support) version
   - Download the Windows installer (.msi)

2. Run the installer:
   - Click "Next" through all steps
   - ✅ Check "Add to PATH" (important!)
   - ✅ Check "Automatically install necessary tools"
   - Complete installation

3. Verify installation in Command Prompt or PowerShell:
   ```cmd
   node --version
   npm --version
   ```
   Should show version numbers, not "command not found"

### Step 2: Install Git (Optional but Recommended)

1. Download from https://git-scm.com/download/win
2. Run installer and accept defaults
3. Verify:
   ```cmd
   git --version
   ```

### Step 3: Clone the Repository

```cmd
cd Desktop
git clone https://github.com/alekhyasain/ai_food_tracker.git
cd ai_food_tracker
```

Or manually:
1. Download ZIP from GitHub
2. Extract to Desktop
3. Open Command Prompt in that folder

### Step 4: Install Dependencies

```cmd
npm install
```

**If this fails**, try:
```cmd
npm install --legacy-peer-deps
```

Or clear cache and retry:
```cmd
npm cache clean --force
npm install
```

### Step 5: Start the Server

```cmd
npm start
```

You should see:
```
Server running on http://localhost:3000
```

### Step 6: Open in Browser

- Open your browser
- Go to: `http://localhost:3000`
- You're done! 🎉

## Troubleshooting Windows-Specific Issues

### Error: "npm: command not found"

**Solution**: Node.js PATH not set correctly

1. **Restart Command Prompt** after installing Node.js
2. **Try PowerShell** instead of Command Prompt
3. **Reinstall Node.js**:
   - Uninstall Node.js from Control Panel
   - Download fresh copy
   - ✅ Make sure "Add to PATH" is checked
   - Restart computer after install

4. **Manual PATH fix**:
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables", find "Path"
   - Click Edit, then New
   - Add: `C:\Program Files\nodejs`
   - Click OK repeatedly to close dialogs
   - Restart Command Prompt

### Error: "npm ERR! EACCES: permission denied"

**Solution**: Run as Administrator

```cmd
# Right-click Command Prompt or PowerShell
# Select "Run as administrator"
npm install
```

Or fix permissions:
```cmd
npm config set prefix C:\Users\YourUsername\AppData\Roaming\npm
```

### Error: "Port 3000 already in use"

**Solution**: Find and kill the process

```cmd
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

Or use a different port:
```cmd
set PORT=3001
npm start
```

### Error: "npm ERR! code ENOENT"

**Solution**: File/folder not found

```cmd
# Make sure you're in the right folder
cd path\to\ai_food_tracker
dir

# Should show: package.json, food_tracker.html, server.js, etc.
npm install
```

### Error: "npm ERR! ERESOLVE unable to resolve dependency tree"

**Solution**: Use legacy dependency resolver

```cmd
npm install --legacy-peer-deps
```

### Error: Module not found after npm install

**Solution**: Rebuild dependencies

```cmd
# Delete node_modules folder
rmdir /s /q node_modules

# Clear npm cache
npm cache clean --force

# Reinstall
npm install
```

### Git credentials issues

If git commits fail:

```cmd
# Configure git
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# For HTTPS (easier on Windows)
git config --global credential.helper wincred

# Or use personal access token
git config --global credential.helper manager
```

## PowerShell vs Command Prompt

**PowerShell** (Recommended for Windows 10+):
- Better error messages
- More features
- Included in Windows 10+

**Command Prompt** (Classic):
- Works fine too
- Simpler interface

Either works with npm.

## Windows Firewall

If you get errors about network:

1. Open "Windows Defender Firewall"
2. Click "Allow an app through firewall"
3. Find "Node.js" or your Node installation
4. Check both "Private" and "Public"
5. Click OK

## Running in Background

To keep the server running when you close the terminal:

### Option 1: Use Screen or tmux
Windows doesn't have built-in support, so use:
```cmd
npm install -g concurrently
concurrently "npm start"
```

### Option 2: Use Windows Task Scheduler
1. Create a batch file `start-server.bat`:
   ```batch
   @echo off
   cd C:\path\to\ai_food_tracker
   npm start
   ```
2. Schedule it to run at startup via Task Scheduler

### Option 3: Keep Command Prompt window open
Just minimize the window, leave it running.

## Using on Phone from Windows

### Local WiFi:
1. Find your Windows IP:
   ```cmd
   ipconfig
   ```
   Look for IPv4 Address (e.g., 192.168.1.100)

2. On phone browser:
   ```
   http://192.168.1.100:3000
   ```

### Public Tunnel (ngrok):

1. Download ngrok: https://ngrok.com/download
2. Extract and add to PATH
3. Start server:
   ```cmd
   npm start
   ```
4. In another Command Prompt:
   ```cmd
   ngrok http 3000
   ```
5. Copy the HTTPS URL from ngrok
6. Use on phone

## Quick Commands Summary

| Command | What it does |
|---------|------------|
| `node --version` | Check if Node.js installed |
| `npm --version` | Check if npm installed |
| `npm install` | Install dependencies |
| `npm start` | Start the server |
| `cd folder_name` | Change folder |
| `dir` | List files in folder |
| `cls` | Clear screen |
| `ipconfig` | Find your Windows IP address |
| `netstat -ano \| findstr :3000` | Find what's using port 3000 |

## Still Having Issues?

1. **Screenshot the error** - Post exact error message
2. **Check Node/npm versions** - Run `node --version` and `npm --version`
3. **Verify folder** - Make sure you're in the ai_food_tracker folder
4. **Try fresh install**:
   ```cmd
   rmdir /s /q node_modules
   npm cache clean --force
   npm install
   npm start
   ```

## Getting Help

If `npm start` still fails:
- Share the exact error message
- Include output of:
  - `node --version`
  - `npm --version`
  - `dir` (to verify files are there)
  - First few lines of the error

---

**Windows 10/11**: Full support ✅
**Node.js 14+**: Recommended
**npm 6+**: Comes with Node.js
