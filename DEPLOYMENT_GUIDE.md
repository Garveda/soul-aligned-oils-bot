# 🌸 Soul Aligned Oils - Cloud Deployment Guide

This guide will help you deploy your Soul Aligned Oils bot to the cloud so it runs automatically every day without needing your local computer.

---

## 📋 Prerequisites

Before deploying, make sure you have:

1. ✅ **OpenAI API Key** - Get from [platform.openai.com](https://platform.openai.com/api-keys)
2. ✅ **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather) on Telegram
3. ✅ **Telegram Chat IDs** - The user IDs who will receive messages
4. ✅ **Git installed** on your computer
5. ✅ **GitHub account** (free) - [github.com](https://github.com)

---

## 🚀 Option 1: Deploy to Railway.app (Recommended - Easiest)

Railway offers a generous free tier and is very easy to use.

### Step 1: Prepare Git Repository

```bash
# Navigate to your project folder
cd C:\Users\admin\Desktop\Sonstiges\HMS_PROJEKT\soul_aligned_oils

# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit - Soul Aligned Oils Bot"
```

### Step 2: Push to GitHub

1. Go to [github.com](https://github.com) and create a new repository
2. Name it: `soul-aligned-oils-bot`
3. Keep it **Private** (recommended for security)
4. Don't initialize with README (we already have files)
5. Copy the repository URL

```bash
# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/soul-aligned-oils-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Login with GitHub
4. Click **"Deploy from GitHub repo"**
5. Select your `soul-aligned-oils-bot` repository
6. Railway will automatically detect the Procfile and start deploying

### Step 4: Configure Environment Variables

In Railway dashboard:

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add each of these:

```
OPENAI_API_KEY=your_actual_key_here
OPENAI_MODEL=gpt-4
TELEGRAM_BOT_TOKEN=your_actual_token_here
TELEGRAM_CHAT_IDS=1234567890,0987654321
CHAT_LANGUAGES=de,de
SEND_TIME=08:00
TIMEZONE=Europe/Berlin
TESTING_MODE=False
LOG_LEVEL=INFO
```

4. Click **"Deploy"** to restart with new variables

### Step 5: Verify Deployment

1. Go to **"Deployments"** tab
2. Check the logs - you should see:
   ```
   🌸 Soul Aligned Oils Bot - Cloud Mode 🌸
   Configuration validated successfully
   ✓ Scheduler configured successfully
   ✓ Bot is now running in the cloud...
   ```

### ✨ Done! Your bot is now running 24/7 in the cloud!

**Railway Free Tier:**
- $5 credit per month
- ~500 hours of runtime (more than enough for this bot)
- No credit card required initially

---

## 🚀 Option 2: Deploy to Render.com

Render is another excellent option with a generous free tier.

### Step 1-2: Same as Railway (Git & GitHub)

Follow Steps 1-2 from Railway guide above.

### Step 3: Deploy to Render

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Background Worker"**
3. Connect your GitHub account
4. Select your `soul-aligned-oils-bot` repository
5. Configure:
   - **Name**: soul-aligned-oils-bot
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main_scheduler.py`

### Step 4: Configure Environment Variables

In Render dashboard:

1. Scroll to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add each variable (same as Railway list above)

### Step 5: Click "Create Background Worker"

Render will build and deploy your bot. Check logs to verify it's running.

**Render Free Tier:**
- 750 hours/month (enough for 24/7 operation)
- Automatic deploys from GitHub
- Free SSL

---

## 🚀 Option 3: Deploy to Fly.io

Fly.io offers great performance with a generous free tier.

### Step 1-2: Same as Railway (Git & GitHub)

Follow Steps 1-2 from Railway guide above.

### Step 3: Install Fly CLI

```bash
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### Step 4: Deploy

```bash
# Navigate to project
cd C:\Users\admin\Desktop\Sonstiges\HMS_PROJEKT\soul_aligned_oils

# Login to Fly.io
fly auth login

# Launch app
fly launch

# Follow prompts:
# - App name: soul-aligned-oils-bot
# - Region: Choose closest to Europe/Berlin
# - Don't deploy yet (we need to set env vars first)
```

### Step 5: Set Environment Variables

```bash
fly secrets set OPENAI_API_KEY="your_key_here"
fly secrets set OPENAI_MODEL="gpt-4"
fly secrets set TELEGRAM_BOT_TOKEN="your_token_here"
fly secrets set TELEGRAM_CHAT_IDS="1234567890,0987654321"
fly secrets set CHAT_LANGUAGES="de,de"
fly secrets set SEND_TIME="08:00"
fly secrets set TIMEZONE="Europe/Berlin"
fly secrets set TESTING_MODE="False"
fly secrets set LOG_LEVEL="INFO"
```

### Step 6: Deploy

```bash
fly deploy
```

**Fly.io Free Tier:**
- 3 shared-cpu VMs
- 160GB outbound traffic
- Plenty for this bot

---

## 🔧 Managing Your Cloud Bot

### View Logs

**Railway:**
- Dashboard → Your Service → Logs tab

**Render:**
- Dashboard → Your Service → Logs tab

**Fly.io:**
```bash
fly logs
```

### Stop the Bot

**Railway/Render:**
- Dashboard → Delete Service

**Fly.io:**
```bash
fly apps destroy soul-aligned-oils-bot
```

### Update the Bot

1. Make changes to your local code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update bot"
   git push
   ```
3. Railway/Render will auto-deploy
4. For Fly.io: `fly deploy`

### Test Manually

To send a test message immediately:

**Railway/Render:**
- Not easily possible with Background Workers

**Fly.io:**
```bash
fly ssh console
python -c "from main import send_now, setup_logging; setup_logging(); send_now()"
```

---

## 🎯 Recommended Choice

**For beginners**: Railway.app
- Easiest to set up
- Best UI
- Automatic deployments from GitHub

**For advanced users**: Fly.io
- More control
- Better performance
- CLI-based management

---

## 🔒 Security Tips

1. ✅ **Never commit `.env` file** - It's in `.gitignore`
2. ✅ **Use environment variables** on the platform
3. ✅ **Keep repository private** on GitHub
4. ✅ **Rotate API keys** periodically
5. ✅ **Monitor logs** regularly

---

## ❓ Troubleshooting

### Bot not sending messages

1. Check environment variables are set correctly
2. Verify timezone is correct
3. Check logs for errors
4. Test Telegram bot token with BotFather

### "Configuration validation failed"

- One or more required environment variables are missing
- Check Railway/Render/Fly.io dashboard for environment variables

### Wrong send time

- Verify `SEND_TIME` format: `HH:MM` (24-hour format)
- Verify `TIMEZONE` is correct: `Europe/Berlin`
- Check platform's timezone settings

### Need help?

Check the logs first - they contain detailed error messages.

---

## 🎉 Congratulations!

Your Soul Aligned Oils bot is now running in the cloud and will send daily affirmations automatically every morning! 🌸

No need to keep your computer on anymore! ✨

