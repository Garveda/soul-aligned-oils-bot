"""
Scheduler Module
Handles daily scheduling of affirmation messages.
"""

import logging
from datetime import datetime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from affirmation_generator import AffirmationGenerator
from telegram_sender import TelegramSender

# Set up logging
logger = logging.getLogger(__name__)


class DailyScheduler:
    """Manages scheduled sending of daily affirmations."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(Config.TIMEZONE))
        self.generator = AffirmationGenerator()
        self.sender = TelegramSender()
        self.timezone = pytz.timezone(Config.TIMEZONE)
        logger.info(f"Scheduler initialized with timezone: {Config.TIMEZONE}")
    
    def send_daily_affirmation(self):
        """Generate and send the daily affirmation."""
        try:
            logger.info("Starting daily affirmation job")
            current_time = datetime.now(self.timezone)
            logger.info(f"Generating affirmations for {current_time.strftime('%A, %B %d, %Y at %H:%M %Z')}")
            
            results = self.sender.send_personalized_messages_sync(self.generator)
            
            successful = sum(1 for r in results if r['success'])
            total = len(results)
            logger.info(f"Daily affirmation job completed: {successful}/{total} sent successfully")
            
            if successful < total:
                logger.warning("Some messages failed to send. Check logs for details.")
            
        except Exception as e:
            logger.error(f"Error in daily affirmation job: {e}", exc_info=True)
    
    def schedule_daily_job(self):
        """Set up the daily scheduled job."""
        hour, minute = Config.get_send_hour_minute()
        logger.info(f"Scheduling daily job for {hour:02d}:{minute:02d} {Config.TIMEZONE}")
        
        trigger = CronTrigger(hour=hour, minute=minute, timezone=self.timezone)
        
        self.scheduler.add_job(
            func=self.send_daily_affirmation,
            trigger=trigger,
            id='daily_affirmation',
            name='Send Daily Affirmation',
            replace_existing=True,
            misfire_grace_time=3600
        )
        
        logger.info(f"Daily job configured successfully")
    
    def run_immediately(self):
        """Run the daily affirmation job immediately (for testing)."""
        logger.info("Manual execution triggered")
        self.send_daily_affirmation()
    
    def start(self):
        """Start the scheduler."""
        try:
            logger.info("Starting scheduler...")
            logger.info("Press Ctrl+C to stop")
            self.scheduler.start()
            
            # Log next run time after scheduler starts
            job = self.scheduler.get_job('daily_affirmation')
            if job and hasattr(job, 'next_run_time') and job.next_run_time:
                logger.info(f"Next scheduled execution: {job.next_run_time.strftime('%A, %B %d, %Y at %H:%M %Z')}")
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the scheduler."""
        logger.info("Shutting down scheduler...")
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down successfully")

