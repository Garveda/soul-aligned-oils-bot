# Quick Setup Guide

## ⚡ 5-Minute Setup

### Step 1: Get Your API Keys (5 minutes)

#### OpenAI API Key
1. Visit: https://platform.openai.com/api-keys
2. Sign up/login
3. Click "Create new secret key"
4. Copy it (starts with `sk-...`)

#### Telegram Bot Token  
1. Open Telegram
2. Search: `@BotFather`
3. Send: `/newbot`
4. Follow prompts
5. Copy bot token

#### Chat IDs
1. Have each person message your bot
2. Run: `python discover_chats.py`
3. Copy the chat IDs shown

### Step 2: Create .env File (2 minutes)

Create a file named `.env` in the `soul_aligned_oils` folder:

```powershell
notepad .env
```

Paste this and fill in YOUR values:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4

# Telegram Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNO
TELEGRAM_CHAT_IDS=5700477215,1626046234
CHAT_LANGUAGES=en,de

# Scheduling
SEND_TIME=08:00
TIMEZONE=Europe/Berlin

# Settings
TESTING_MODE=False
LOG_LEVEL=INFO
```

**Save the file!**

### Step 3: Install & Run (2 minutes)

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

Choose option 2 to test immediately!

## 🎯 Configuration Explained

```env
TELEGRAM_CHAT_IDS=5700477215,1626046234
CHAT_LANGUAGES=en,de
```

- First person (5700477215) gets **English**
- Second person (1626046234) gets **German**

## ⏰ Setting the Time

```env
SEND_TIME=08:00  # 8:00 AM
SEND_TIME=18:30  # 6:30 PM
```

Use 24-hour format!

## 🧪 Testing Without Sending

```env
TESTING_MODE=True
```

Shows what would be sent without actually sending.

## 💡 Quick Troubleshooting

**"No module named..."**
```powershell
pip install -r requirements.txt
```

**"Unauthorized" error**
- Get new bot token from @BotFather
- Update TELEGRAM_BOT_TOKEN in .env

**Messages in English when should be German**
- Change to `OPENAI_MODEL=gpt-4`
- GPT-4 follows language instructions better

**Can't find chat IDs**
- Make sure they messaged the bot first
- Run `python discover_chats.py`

## ✅ You're Ready!

```powershell
python main.py
# Choose 1 for scheduler
# Or 2 to send now
```

**That's it!** 🌸💜

