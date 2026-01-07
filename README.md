# 🌸 Soul Aligned Oils - Daily Affirmation Bot

A Python-based automation system that sends daily personalized affirmations with doTerra essential oil recommendations via Telegram at a scheduled time.

## ✨ Features

- 🌅 **Daily Scheduling**: Automatically sends messages at your chosen time
- 🤖 **AI-Generated Content**: Uses OpenAI GPT to create personalized affirmations
- 🌿 **Essential Oil Pairing**: Matches 30 doTerra oils to daily themes
- 🌍 **Multi-Language Support**: English and German (more can be added)
- 📱 **Multi-Recipient**: Send to unlimited users
- 🧪 **Testing Mode**: Preview without sending
- 📊 **Comprehensive Logging**: Track all activities

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd soul_aligned_oils
pip install -r requirements.txt
```

### 2. Create .env File

```bash
notepad .env
```

Add your configuration:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4

# Telegram Configuration  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_IDS=5700477215,1626046234
CHAT_LANGUAGES=en,de

# Scheduling
SEND_TIME=08:00
TIMEZONE=Europe/Berlin

# Settings
TESTING_MODE=False
LOG_LEVEL=INFO
```

### 3. Run the Bot

```bash
python main.py
```

Choose option 1 to start the scheduler, or option 2 to send immediately.

## 📋 Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy and save it

### Telegram Bot Token
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow prompts
4. Copy the bot token

### Telegram Chat IDs
1. Have recipients message your bot
2. Run `python discover_chats.py`
3. Copy the chat IDs

## 🌍 Multi-Language Support

Configure different languages for different recipients:

```env
TELEGRAM_CHAT_IDS=123456,789012
CHAT_LANGUAGES=en,de
```

- First person gets English
- Second person gets German

Supported languages: `en` (English), `de` (German)

## ⚙️ Configuration Options

- `SEND_TIME`: When to send daily (HH:MM format, 24-hour)
- `TIMEZONE`: Your timezone (e.g., `Europe/Berlin`, `America/New_York`)
- `OPENAI_MODEL`: `gpt-4` (best quality) or `gpt-3.5-turbo` (cheaper)
- `TESTING_MODE`: `True` to preview without sending

## 📱 Example Message

**English:**
```
🌅 Good Morning, Beautiful Soul

Today is a day of new beginnings. "I embrace this fresh  
start with confidence and clarity..."

✨ Your Oil Companion: Frankincense
This sacred oil supports deep intention-setting...

🌿 Your Ritual:
Apply 1-2 drops to your wrists and heart center...

With love and light,
Soul Aligned Oils 💜
```

**German:**
```
🌅 Guten Morgen, Wunderschöne Seele

Heute ist ein Tag des Neubeginns. "Ich nehme diesen  
frischen Start mit Zuversicht und Klarheit an..."

✨ Dein Öl-Begleiter: Weihrauch
Dieses heilige Öl unterstützt tiefe Absichtssetzung...

🌿 Dein Ritual:
Trage 1-2 Tropfen auf deine Handgelenke auf...

Mit Liebe und Licht,
Soul Aligned Oils 💜
```

## 🛠️ Menu Options

1. **Start Scheduler** - Runs 24/7, sends at configured time
2. **Send Now** - Manual one-time send
3. **Test Configuration** - Verify settings
4. **Test Telegram Connection** - Check bot and chat IDs
5. **Generate Test Message** - Preview without sending
6. **Exit** - Stop the application

## 💰 Cost Estimates

For 2 recipients daily:
- **GPT-3.5-turbo**: ~$0.18/month
- **GPT-4**: ~$1.80/month
- **Telegram**: Free

## 🔧 Troubleshooting

### "Unauthorized" Error
- Get a new bot token from @BotFather
- Update TELEGRAM_BOT_TOKEN in .env

### Messages in Wrong Language
- Check CHAT_LANGUAGES order matches TELEGRAM_CHAT_IDS
- For German, use GPT-4 for better results

### No Messages Received
- Verify recipients messaged the bot first
- Run `python discover_chats.py` to see valid chat IDs
- Check logs in `logs/bot.log`

## 📚 Project Structure

```
soul_aligned_oils/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── affirmation_generator.py  # OpenAI integration
├── telegram_sender.py     # Telegram bot logic
├── scheduler.py           # Daily scheduling
├── discover_chats.py      # Find chat IDs
├── data/
│   └── doterra_oils.json  # 30 essential oils database
├── logs/
│   └── bot.log           # Application logs
├── requirements.txt       # Python dependencies
└── .env                  # Your configuration
```

## 🌟 Essential Oils Included

30 doTerra oils: Lavender, Peppermint, Frankincense, Wild Orange, Lemon, Balance, Serenity, and more!

## 📝 Daily Energy Themes

- **Monday**: New beginnings, intention setting
- **Tuesday**: Action, courage, momentum
- **Wednesday**: Balance, reflection
- **Thursday**: Growth, gratitude
- **Friday**: Release, celebration
- **Saturday**: Rest, self-care
- **Sunday**: Reflection, spiritual connection

## 🎯 Next Steps

1. Configure your `.env` file
2. Test with `python main.py` → option 2
3. Start scheduler with option 1
4. Keep terminal running (or deploy to cloud)

## 💜 Support

Check `logs/bot.log` for detailed error messages.

---

**Built with love for holistic wellness and daily inspiration** 🌸

