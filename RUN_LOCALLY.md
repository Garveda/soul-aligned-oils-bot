# Running the Bot Locally (For Testing)

## ⚠️ Important Note
**The bot is already running on Railway automatically!** You don't need to run it locally unless you want to test changes before deploying.

## If You Want to Test Locally:

### 1. Navigate to the project directory:
```powershell
cd C:\Users\admin\Desktop\Sonstiges\HMS_PROJEKT\soul_aligned_oils
```

### 2. Activate the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Set encoding (for Windows):
```powershell
$env:PYTHONIOENCODING='utf-8'
```

### 4. Run the scheduler:
```powershell
python main_scheduler.py
```

The bot will:
- ✅ Initialize the database
- ✅ Populate lunar calendar
- ✅ Start checking for commands every 5 minutes
- ✅ Send daily messages at 07:00 Berlin time
- ✅ Process scheduled repeats every minute

### 5. To Stop:
Press `Ctrl+C` to stop the bot.

## For Production (Railway):
The bot runs automatically - no action needed! The `Procfile` tells Railway to run `python main_scheduler.py`.
