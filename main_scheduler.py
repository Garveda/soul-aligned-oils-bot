"""
Cloud-ready entry point for Soul Aligned Oils Bot
Automatically starts the scheduler without user interaction.
"""

import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from scheduler import DailyScheduler


def setup_logging():
    """Set up logging configuration."""
    log_dir = Path(Config.LOG_FILE_PATH).parent
    log_dir.mkdir(exist_ok=True)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # File handler
    file_handler = logging.FileHandler(Config.LOG_FILE_PATH, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress verbose library logs
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.INFO)


def main():
    """Main entry point for cloud deployment."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("🌸 Soul Aligned Oils Bot - Cloud Mode 🌸")
    logger.info("="*60)
    
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Cannot start bot.")
        logger.error("Please check your environment variables:")
        logger.error("- OPENAI_API_KEY")
        logger.error("- TELEGRAM_BOT_TOKEN")
        logger.error("- TELEGRAM_CHAT_IDS")
        sys.exit(1)
    
    logger.info("Configuration validated successfully")
    logger.info(f"Timezone: {Config.TIMEZONE}")
    logger.info(f"Send Time: {Config.SEND_TIME}")
    logger.info(f"Chat IDs configured: {len([c for c in Config.TELEGRAM_CHAT_IDS if c])}")
    
    try:
        # Create and configure scheduler
        scheduler = DailyScheduler()
        scheduler.schedule_daily_job()
        
        logger.info(f"✓ Scheduler configured successfully")
        logger.info(f"✓ Daily messages will be sent at {Config.SEND_TIME} {Config.TIMEZONE}")
        logger.info(f"✓ Bot is now running in the cloud...")
        logger.info("="*60)
        
        # Start the scheduler (blocking call)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

