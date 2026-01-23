# 🚀 GitHub & Railway Setup Guide

Complete step-by-step guide to connect your Soul Aligned Oils project to GitHub and Railway.

---

## 📋 Prerequisites Checklist

- [x] Git installed (you confirmed this)
- [x] GitHub account (create at https://github.com if needed)
- [x] Railway account (create at https://railway.app if needed)
- [x] Project files ready (✅ all files in place)
- [x] `.gitignore` configured (✅ already set up)

---

## Part 1: Connect to GitHub

### Step 1: Initialize Git Repository

Open **Git Bash** or **PowerShell** (restart if needed to refresh PATH) and navigate to your project:

```powershell
cd C:\Users\ahirs\Desktop\sonstiges\soul_aligned_oils
```

**Option A: Using Git Bash (Recommended)**
```bash
git init
git add .
git commit -m "Initial commit - Soul Aligned Oils Bot"
```

**Option B: Using PowerShell**
```powershell
# If git is in PATH after restart
git init
git add .
git commit -m "Initial commit - Soul Aligned Oils Bot"

# OR if git is not in PATH, use full path:
& "C:\Program Files\Git\bin\git.exe" init
& "C:\Program Files\Git\bin\git.exe" add .
& "C:\Program Files\Git\bin\git.exe" commit -m "Initial commit - Soul Aligned Oils Bot"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Repository settings:
   - **Name:** `soul-aligned-oils-bot` (or your preferred name)
   - **Description:** "Daily affirmation bot with doTerra essential oil recommendations"
   - **Visibility:** 
     - ✅ **Private** (recommended - keeps your API keys safer)
     - ⚠️ Public (if you want to share)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

### Step 3: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/soul-aligned-oils-bot.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**If you get authentication errors:**
- GitHub no longer accepts passwords for HTTPS
- Use a **Personal Access Token** instead:
  1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token (classic)
  3. Select scopes: `repo` (full control)
  4. Copy the token
  5. When prompted for password, paste the token instead

**Alternative: Use GitHub Desktop or GitHub CLI**
- Download GitHub Desktop: https://desktop.github.com
- Or install GitHub CLI: `winget install GitHub.cli`

---

## Part 2: Connect to Railway

### Step 1: Sign Up / Sign In to Railway

1. Go to https://railway.app
2. Click **"Start a New Project"** or **"Login"**
3. Sign in with **GitHub** (recommended - easiest integration)

### Step 2: Deploy from GitHub

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub (if first time)
4. Select your repository: `soul-aligned-oils-bot`
5. Railway will automatically detect it's a Python project

### Step 3: Configure Environment Variables

In Railway dashboard, go to your project → **Variables** tab, and add:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_IDS=5700477215,1626046234,6228197533,6537608925
CHAT_LANGUAGES=de,de,de,de
SEND_TIME=08:00
TIMEZONE=Europe/Berlin
TESTING_MODE=False
LOG_LEVEL=INFO
```

**Where to find these values:**
- **OPENAI_API_KEY**: https://platform.openai.com/api-keys
- **TELEGRAM_BOT_TOKEN**: Message @BotFather on Telegram → `/mybots` → Select your bot → API Token
- **TELEGRAM_CHAT_IDS**: Already configured (4 users)
- **CHAT_LANGUAGES**: All German (de)

### Step 4: Configure Build Settings

Railway should auto-detect, but verify:

1. Go to **Settings** tab in Railway
2. **Root Directory**: Leave empty (or set to `/` if needed)
3. **Build Command**: Leave empty (Railway auto-detects Python)
4. **Start Command**: Should be `python main_scheduler.py` (from Procfile)

**Verify Procfile exists:**
- Railway reads `Procfile` which contains: `worker: python main_scheduler.py`
- This tells Railway how to run your bot

### Step 5: Deploy

1. Railway will automatically start deploying
2. Check the **Deployments** tab to see progress
3. Watch the **Logs** tab for any errors
4. Once deployed, your bot will run 24/7!

---

## Part 3: Verify Everything Works

### Check Railway Logs

1. Go to Railway dashboard → Your project → **Logs** tab
2. Look for:
   ```
   🌸 Soul Aligned Oils Bot - Cloud Mode 🌸
   ✓ Configuration validated successfully
   ✓ Scheduler configured successfully
   ✓ Bot is now running in the cloud...
   ```

### Test the Bot

1. Wait for the scheduled time (08:00 Berlin time)
2. Or trigger manually by:
   - Going to Railway → **Deployments** → Click the three dots → **Redeploy**
   - This will restart and send immediately if you modify the code

### Check GitHub

1. Go to your GitHub repository
2. Verify all files are there (except `.env` - should be ignored)
3. Check that `.gitignore` is working (no sensitive files committed)

---

## 🔄 Future Updates

After initial setup, updating is easy:

```powershell
# Make your changes locally
# Then commit and push:
git add .
git commit -m "Your update message"
git push
```

Railway will **automatically detect** the push and redeploy! ✨

---

## 🛠️ Troubleshooting

### Git Not Found
- **Solution**: Restart PowerShell/terminal
- **Or**: Use Git Bash instead
- **Or**: Add Git to PATH manually

### GitHub Authentication Failed
- **Solution**: Use Personal Access Token instead of password
- **Or**: Use GitHub Desktop for easier authentication

### Railway Deployment Failed
- **Check**: Environment variables are all set
- **Check**: Procfile exists and is correct
- **Check**: Logs tab for specific error messages
- **Check**: Python version in `runtime.txt` (3.11.9)

### Bot Not Sending Messages
- **Check**: Railway logs for errors
- **Verify**: All environment variables are correct
- **Verify**: Telegram bot token is valid
- **Verify**: Chat IDs are correct

### Database Issues
- Railway creates its own database instance
- Local `data/bot_database.db` is ignored (in .gitignore)
- Database will auto-initialize on first Railway run

---

## 📝 Quick Reference Commands

```powershell
# Initialize git (first time only)
git init
git add .
git commit -m "Initial commit"

# Connect to GitHub (first time only)
git remote add origin https://github.com/YOUR_USERNAME/soul-aligned-oils-bot.git
git branch -M main
git push -u origin main

# Future updates
git add .
git commit -m "Update message"
git push

# Check status
git status
git log --oneline
```

---

## ✅ Success Checklist

- [ ] Git repository initialized locally
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Railway connected to GitHub repo
- [ ] Environment variables set in Railway
- [ ] Deployment successful
- [ ] Bot running in Railway logs
- [ ] Test message received (at scheduled time or after redeploy)

---

## 🎉 You're Done!

Once all steps are complete:
- ✅ Your code is backed up on GitHub
- ✅ Your bot runs 24/7 on Railway
- ✅ Updates auto-deploy when you push to GitHub
- ✅ No need to keep your computer on!

**Next send:** Tomorrow at 08:00 Berlin time (or immediately after redeploy)

---

**Need help?** Check:
- Railway logs for deployment issues
- GitHub repository for code issues
- This guide for setup questions
