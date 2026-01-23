# 🔄 Refresh GitHub Repository

Your repository: **https://github.com/Garveda/soul-aligned-oils-bot**

Here are your options to sync your local project with GitHub.

---

## Option 1: Force Push (Replace Everything on GitHub) ⚠️

**Use this if:** You want your local files to completely replace what's on GitHub.

**⚠️ Warning:** This will overwrite everything on GitHub with your local version.

```powershell
cd C:\Users\ahirs\Desktop\sonstiges\soul_aligned_oils

# Connect to GitHub (if not already connected)
git remote add origin https://github.com/Garveda/soul-aligned-oils-bot.git
# OR if already connected, update it:
# git remote set-url origin https://github.com/Garveda/soul-aligned-oils-bot.git

# Stage all your local files
git add .

# Commit everything
git commit -m "Refresh project - complete update"

# Force push to GitHub (overwrites remote)
git branch -M main
git push -u origin main --force
```

---

## Option 2: Pull First, Then Push (Merge Both) ✅

**Use this if:** You want to keep files from both local and GitHub, merging them together.

```powershell
cd C:\Users\ahirs\Desktop\sonstiges\soul_aligned_oils

# Connect to GitHub
git remote add origin https://github.com/Garveda/soul-aligned-oils-bot.git
# OR if already connected:
# git remote set-url origin https://github.com/Garveda/soul-aligned-oils-bot.git

# Pull existing files from GitHub and merge
git pull origin main --allow-unrelated-histories

# If there are conflicts, resolve them, then:
git add .
git commit -m "Merge local and GitHub versions"

# Push everything back
git branch -M main
git push -u origin main
```

---

## Option 3: Check Differences First (Recommended) 🔍

**Use this to see what's different before deciding:**

```powershell
cd C:\Users\ahirs\Desktop\sonstiges\soul_aligned_oils

# Connect to GitHub
git remote add origin https://github.com/Garveda/soul-aligned-oils-bot.git

# Fetch what's on GitHub (doesn't change your files)
git fetch origin

# See what's different
git log HEAD..origin/main  # Commits on GitHub you don't have
git log origin/main..HEAD  # Commits you have that GitHub doesn't
git diff origin/main        # File differences

# Then decide: Option 1 (force push) or Option 2 (merge)
```

---

## Quick Setup (Most Common)

If you just want to push your current local project to GitHub:

```powershell
cd C:\Users\ahirs\Desktop\sonstiges\soul_aligned_oils

# Set remote
git remote add origin https://github.com/Garveda/soul-aligned-oils-bot.git
# OR update if exists:
git remote set-url origin https://github.com/Garveda/soul-aligned-oils-bot.git

# Add and commit everything
git add .
git commit -m "Complete project refresh"

# Push (force if you want to overwrite GitHub)
git branch -M main
git push -u origin main --force
```

---

## After Pushing: Connect to Railway

Once your code is on GitHub:

1. Go to: https://railway.app
2. Sign in with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Select: `Garveda/soul-aligned-oils-bot`
5. Add environment variables (see below)

---

## Environment Variables for Railway

Add these in Railway → Your Project → **Variables**:

```
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_IDS=5700477215,1626046234,6228197533,6537608925
CHAT_LANGUAGES=de,de,de,de
SEND_TIME=08:00
TIMEZONE=Europe/Berlin
TESTING_MODE=False
LOG_LEVEL=INFO
```

---

## 🔐 Authentication

If asked for password during push, use a **GitHub Personal Access Token**:

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic) with `repo` scope
3. Copy token
4. Use token as password when pushing

---

## ✅ Verify Success

After pushing, check:

1. Go to: https://github.com/Garveda/soul-aligned-oils-bot
2. Verify all your files are there
3. Check that `.env` is NOT there (should be ignored by .gitignore)

---

## 🛠️ Troubleshooting

### "Remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/Garveda/soul-aligned-oils-bot.git
```

### "Updates were rejected"
Use `--force` flag (see Option 1 above)

### "Authentication failed"
Use Personal Access Token instead of password

---

**Recommendation:** Use **Option 1 (Force Push)** if you're sure your local version is the one you want on GitHub.
