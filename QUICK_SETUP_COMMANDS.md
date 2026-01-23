# ⚡ Quick Setup Commands

Copy and paste these commands in order. Replace `YOUR_USERNAME` with your actual GitHub username.

---

## 🐙 GitHub Setup (5 minutes)

### 1. Initialize Git
```powershell
cd C:\Users\ahirs\Desktop\sonstiges\soul_aligned_oils
git init
git add .
git commit -m "Initial commit - Soul Aligned Oils Bot"
```

### 2. Create GitHub Repository
1. Go to: https://github.com/new
2. Repository name: `soul-aligned-oils-bot`
3. Choose: **Private** (recommended)
4. **DO NOT** check "Add a README file"
5. Click: **Create repository**

### 3. Connect and Push
```powershell
git remote add origin https://github.com/YOUR_USERNAME/soul-aligned-oils-bot.git
git branch -M main
git push -u origin main
```

**If asked for password:** Use a GitHub Personal Access Token instead:
- Get token: https://github.com/settings/tokens
- Generate new token (classic) with `repo` scope
- Use token as password when pushing

---

## 🚂 Railway Setup (5 minutes)

### 1. Sign Up
- Go to: https://railway.app
- Click: **"Start a New Project"**
- Sign in with: **GitHub** (recommended)

### 2. Deploy
1. Click: **"New Project"**
2. Select: **"Deploy from GitHub repo"**
3. Authorize Railway (if first time)
4. Select: `soul-aligned-oils-bot`
5. Railway auto-detects Python project ✅

### 3. Add Environment Variables
In Railway → Your Project → **Variables** tab, add:

```
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4
TELEGRAM_BOT_TOKEN=your_telegram_token_here
TELEGRAM_CHAT_IDS=5700477215,1626046234,6228197533,6537608925
CHAT_LANGUAGES=de,de,de,de
SEND_TIME=08:00
TIMEZONE=Europe/Berlin
TESTING_MODE=False
LOG_LEVEL=INFO
```

### 4. Deploy!
- Railway automatically starts deploying
- Check **Logs** tab for status
- Look for: `✓ Bot is now running in the cloud...`

---

## ✅ Done!

Your bot is now:
- ✅ Backed up on GitHub
- ✅ Running 24/7 on Railway
- ✅ Auto-deploying on every git push

**Next message:** Tomorrow at 08:00 Berlin time! 🌸

---

## 🔄 Update Bot (Future)

```powershell
git add .
git commit -m "Your update message"
git push
```

Railway auto-deploys! ✨
