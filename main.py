"""
Soul Aligned Oils - Daily Affirmation Bot
Main application entry point
"""

import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from scheduler import DailyScheduler
from affirmation_generator import AffirmationGenerator
from telegram_sender import TelegramSender


def setup_logging():
    """Set up logging configuration."""
    log_dir = Path(Config.LOG_FILE_PATH).parent
    log_dir.mkdir(exist_ok=True)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    file_handler = logging.FileHandler(Config.LOG_FILE_PATH, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.INFO)


def print_banner():
    """Print application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🌸 SOUL ALIGNED OILS 🌸                         ║
║                                                               ║
║         Daily Affirmations & Essential Oil Guidance          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Print main menu."""
    print("\n" + "="*60)
    print("Main Menu")
    print("="*60)
    print("\n1. Start Scheduler (Run continuously)")
    print("2. Send Now (ALL users - Production)")
    print("3. 🧪 Test Send (Admin ONLY - 5700477215)")
    print("4. Test Configuration")
    print("5. Test Telegram Connection")
    print("6. Generate Test Message (no send)")
    print("7. Exit")
    print()


def test_configuration():
    """Test and display configuration."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("Configuration Test")
    print("="*60 + "\n")
    
    print(f"OpenAI API Key: {'✓ Set' if Config.OPENAI_API_KEY else '✗ Not Set'}")
    print(f"OpenAI Model: {Config.OPENAI_MODEL}")
    print(f"Telegram Bot Token: {'✓ Set' if Config.TELEGRAM_BOT_TOKEN else '✗ Not Set'}")
    print(f"Telegram Chat IDs: {len(Config.TELEGRAM_CHAT_IDS)} configured")
    for i, chat_id in enumerate(Config.TELEGRAM_CHAT_IDS, 1):
        if chat_id:
            language = Config.get_language_for_chat(chat_id)
            print(f"  {i}. {chat_id} ({language})")
    print(f"Send Time: {Config.SEND_TIME} {Config.TIMEZONE}")
    print(f"Testing Mode: {'Enabled' if Config.TESTING_MODE else 'Disabled'}")
    print(f"Log Level: {Config.LOG_LEVEL}")
    
    print("\nValidation Result:", end=" ")
    if Config.validate():
        print("✓ PASSED")
        logger.info("Configuration validation passed")
        return True
    else:
        print("✗ FAILED")
        logger.error("Configuration validation failed")
        return False


def test_telegram_connection():
    """Test Telegram bot connection."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("Telegram Connection Test")
    print("="*60 + "\n")
    
    if not Config.TELEGRAM_BOT_TOKEN:
        print("✗ Telegram bot token not configured")
        return False
    
    sender = TelegramSender()
    success = sender.test_connection_sync()
    
    if success:
        print("\n✓ Telegram connection test PASSED")
        logger.info("Telegram connection test passed")
    else:
        print("\n✗ Telegram connection test FAILED")
        logger.error("Telegram connection test failed")
    
    return success


def generate_test_message():
    """Generate a test message without sending."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("Generating Test Message")
    print("="*60 + "\n")
    
    if not Config.OPENAI_API_KEY:
        print("✗ OpenAI API key not configured")
        return
    
    try:
        generator = AffirmationGenerator()
        message = generator.generate_daily_message()
        
        if message:
            print("\n" + "="*60)
            print("GENERATED MESSAGE")
            print("="*60 + "\n")
            print(message)
            print("\n" + "="*60 + "\n")
            logger.info("Test message generated successfully")
        else:
            print("✗ Failed to generate message")
            logger.error("Failed to generate test message")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.error(f"Error generating test message: {e}", exc_info=True)


def send_now():
    """Send affirmation immediately to ALL users."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("Sending Affirmation Now (ALL USERS)")
    print("="*60 + "\n")
    
    if not Config.validate():
        print("✗ Configuration validation failed. Please check your settings.")
        return
    
    try:
        scheduler = DailyScheduler()
        scheduler.run_immediately()
        
        print("\n✓ Message sent successfully!")
        logger.info("Manual send completed successfully")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.error(f"Error during manual send: {e}", exc_info=True)


def send_test():
    """Send test affirmation ONLY to admin (ID 5700477215)."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("🧪 TEST MODE: Sending to Admin Only (5700477215)")
    print("="*60 + "\n")
    
    if not Config.validate():
        print("✗ Configuration validation failed. Please check your settings.")
        return
    
    try:
        scheduler = DailyScheduler()
        scheduler.run_immediately(test_mode=True)
        
        print("\n✓ Test message sent to admin only!")
        logger.info("Test send completed successfully (admin only)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.error(f"Error during test send: {e}", exc_info=True)


def start_scheduler():
    """Start the daily scheduler."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("Starting Daily Scheduler")
    print("="*60 + "\n")
    
    if not Config.validate():
        print("✗ Configuration validation failed. Please check your settings.")
        input("\nPress Enter to continue...")
        return
    
    try:
        scheduler = DailyScheduler()
        scheduler.schedule_daily_job()
        
        next_run = scheduler.scheduler.get_job('daily_affirmation').next_run_time
        print(f"✓ Scheduler configured")
        print(f"  Next run: {next_run.strftime('%A, %B %d, %Y at %H:%M %Z')}")
        print(f"\nScheduler is now running...")
        print("Press Ctrl+C to stop\n")
        
        logger.info("Starting scheduler in blocking mode")
        scheduler.start()
        
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        logger.info("Scheduler stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.error(f"Scheduler error: {e}", exc_info=True)


def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("Soul Aligned Oils Bot Starting")
    logger.info("="*60)
    
    print_banner()
    
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print("\n⚠️  WARNING: .env file not found!")
        print("Please create a .env file with your configuration.")
        logger.warning(".env file not found")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return
    
    while True:
        try:
            print_menu()
            choice = input("Select option (1-7): ").strip()
            
            if choice == "1":
                start_scheduler()
            elif choice == "2":
                send_now()
                input("\nPress Enter to continue...")
            elif choice == "3":
                send_test()
                input("\nPress Enter to continue...")
            elif choice == "4":
                test_configuration()
                input("\nPress Enter to continue...")
            elif choice == "5":
                test_telegram_connection()
                input("\nPress Enter to continue...")
            elif choice == "6":
                generate_test_message()
                input("\nPress Enter to continue...")
            elif choice == "7":
                print("\nGoodbye! May your day be filled with light. 💜\n")
                logger.info("Application exited by user")
                break
            else:
                print("\n✗ Invalid option. Please select 1-7.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            logger.info("Application interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

