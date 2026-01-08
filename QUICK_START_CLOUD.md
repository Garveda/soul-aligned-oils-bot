# 🚀 Quick Start - Deploy to Cloud in 10 Minutes

## Railway.app - Fastest Method

### 1️⃣ Push to GitHub (5 minutes)

```bash
cd C:\Users\admin\Desktop\Sonstiges\HMS_PROJEKT\soul_aligned_oils
git init
git add .
git commit -m "Initial commit"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/soul-aligned-oils-bot.git
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy to Railway (3 minutes)

1. Go to **railway.app**
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

### 3️⃣ Set Environment Variables (2 minutes)

In Railway dashboard → Variables tab, add:

```
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_IDS=5700477215,1626046234
CHAT_LANGUAGES=de,de
SEND_TIME=08:00
TIMEZONE=Europe/Berlin
OPENAI_MODEL=gpt-4
LOG_LEVEL=INFO
```

### ✅ Done!

Your bot is now running 24/7 in the cloud! 🎉

Check logs to verify:
```
🌸 Soul Aligned Oils Bot - Cloud Mode 🌸
✓ Scheduler configured successfully
✓ Bot is now running in the cloud...
```

---

## 📝 Your Current Settings

- **Chat IDs**: 5700477215, 1626046234
- **Language**: German (de)
- **Send Time**: 08:00 Europe/Berlin
- **Model**: GPT-4

---

## 💡 Need More Details?

See `DEPLOYMENT_GUIDE.md` for:
- Alternative platforms (Render.com, Fly.io)
- Troubleshooting
- Security tips
- Management commands



