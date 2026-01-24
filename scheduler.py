"""
Scheduler Module
Handles daily scheduling of affirmation messages.
"""

import logging
from datetime import datetime, date, timedelta
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import Config
from affirmation_generator import AffirmationGenerator
from telegram_sender import TelegramSender
from database import Database
from lunar_calendar import LunarCalendar
from command_handler import CommandHandler

# Set up logging
logger = logging.getLogger(__name__)


class DailyScheduler:
    """Manages scheduled sending of daily affirmations."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(Config.TIMEZONE))
        self.timezone = pytz.timezone(Config.TIMEZONE)
        
        # Initialize database and related modules
        self.db = Database()
        self.lunar_calendar = LunarCalendar(self.db)
        self.generator = AffirmationGenerator(db=self.db, lunar_calendar=self.lunar_calendar)
        self.command_handler = CommandHandler(self.db, self.generator)
        self.sender = TelegramSender(command_handler=self.command_handler)
        
        # Populate lunar calendar for next 90 days
        self._populate_lunar_calendar()
        
        # Populate oils database on first run (if empty)
        self._populate_oils_database_if_needed()
        
        logger.info(f"Scheduler initialized with timezone: {Config.TIMEZONE}")
    
    def _populate_lunar_calendar(self):
        """Populate lunar calendar for the next 90 days."""
        try:
            start_date = date.today()
            end_date = start_date + timedelta(days=90)
            self.lunar_calendar.populate_lunar_calendar(start_date, end_date)
            logger.info(f"Lunar calendar populated for {start_date} to {end_date}")
        except Exception as e:
            logger.error(f"Error populating lunar calendar: {e}")
    
    def _populate_oils_database_if_needed(self):
        """Populate oils database on first run if empty."""
        try:
            # Check if database has any oils
            test_oil = self.db.get_oil("Lavender")
            if not test_oil:
                logger.info("Oils database is empty, populating from JSON...")
                from populate_oils_database import populate_oils
                count = populate_oils()
                logger.info(f"✅ Populated {count} oils in database")
            else:
                logger.info("Oils database already populated")
        except Exception as e:
            logger.warning(f"Could not populate oils database: {e} (Info command may not work)")
    
    def send_daily_affirmation(self, test_mode: bool = False):
        """Generate and send the daily affirmation.
        
        Args:
            test_mode: If True, only sends to admin ID 5700477215
        """
        try:
            if test_mode:
                logger.info("🧪 Starting TEST MODE affirmation job (admin only)")
            else:
                logger.info("Starting daily affirmation job")
            
            current_time = datetime.now(self.timezone)
            today = current_time.date()
            
            # Check for special days
            special_day_info = self.lunar_calendar.get_special_day_info(today)
            message_type = special_day_info.get('message_type', 'regular')
            logger.info(f"Generating affirmations for {current_time.strftime('%A, %B %d, %Y at %H:%M %Z')} (Type: {message_type})")
            
            # Generate and send messages
            results = self.sender.send_personalized_messages_sync(self.generator, test_mode, special_day_info)
            
            # Save messages to database with programmatically selected oils
            for result in results:
                if result.get('success') and result.get('message'):
                    user_id = result['chat_id']
                    message = result['message']
                    
                    # Use programmatically selected oils directly (more reliable than extraction)
                    primary_oil = result.get('primary_oil')
                    alternative_oil = result.get('alternative_oil')
                    
                    # Fallback to extraction if oils weren't provided (backward compatibility)
                    if not primary_oil or not alternative_oil:
                        logger.warning(f"Oils not provided in result, falling back to extraction for user {user_id}")
                        primary_oil, alternative_oil = self.generator._extract_oil_names(message)
                    
                    # Save to database
                    self.db.save_daily_message(
                        user_id=user_id,
                        message_date=today,
                        message_text=message,
                        primary_oil=primary_oil,
                        alternative_oil=alternative_oil,
                        message_type=message_type
                    )
                    
                    if primary_oil and alternative_oil:
                        logger.info(f"Saved message for {user_id}: Primary={primary_oil}, Alternative={alternative_oil}")
            
            successful = sum(1 for r in results if r['success'])
            total = len(results)
            
            if test_mode:
                logger.info(f"🧪 TEST job completed: {successful}/{total} sent to admin")
            else:
                logger.info(f"Daily affirmation job completed: {successful}/{total} sent successfully")
                # Only send admin report in production mode, not test mode
                self._send_admin_report(results, current_time)
            
            if successful < total:
                logger.warning("Some messages failed to send. Check logs for details.")
            
        except Exception as e:
            logger.error(f"Error in daily affirmation job: {e}", exc_info=True)
    
    def _send_admin_report(self, results, send_time):
        """Send delivery report to admin (ID 5700477215)."""
        try:
            admin_id = "5700477215"
            
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            # Check for new users
            logger.info("Checking for new users...")
            new_users = self.sender.discover_new_users_sync()
            
            # Build report message in German
            report = f"📊 *Soul Aligned Oils - Versandbericht*\n\n"
            report += f"🕐 Zeit: {send_time.strftime('%d.%m.%Y um %H:%M Uhr')}\n"
            report += f"📨 Gesamt: {len(results)} Nachrichten\n\n"
            
            # Successful deliveries
            report += f"✅ *Erfolgreich: {len(successful)}*\n"
            if successful:
                for r in successful:
                    language = r.get('language', 'de')
                    report += f"  • {r['chat_id']} ({language})\n"
            else:
                report += "  Keine erfolgreichen Zusendungen\n"
            
            report += f"\n"
            
            # Failed deliveries
            if failed:
                report += f"❌ *Fehlgeschlagen: {len(failed)}*\n"
                for r in failed:
                    error_msg = r.get('error', 'Unbekannter Fehler')
                    language = r.get('language', 'de')
                    report += f"  • {r['chat_id']} ({language})\n"
                    report += f"    Fehler: {error_msg}\n"
            else:
                report += f"✅ *Keine Fehler!*\n"
            
            # New users section
            if new_users:
                report += f"\n"
                report += f"🆕 *Neue Benutzer gefunden: {len(new_users)}*\n"
                report += f"(Diese Benutzer haben den Bot kontaktiert, sind aber noch nicht konfiguriert)\n\n"
                
                new_ids = []
                for i, user in enumerate(new_users, 1):
                    name = f"{user['first_name']} {user['last_name'] or ''}".strip()
                    username = user.get('username', 'Nicht gesetzt')
                    report += f"  {i}. *{name}*\n"
                    report += f"     Chat ID: `{user['chat_id']}`\n"
                    report += f"     Username: @{username}\n"
                    report += f"     Typ: {user['type']}\n"
                    new_ids.append(user['chat_id'])
                
                report += f"\n📋 *Zum Hinzufügen auf Railway:*\n"
                report += f"`TELEGRAM_CHAT_IDS={','.join(Config.TELEGRAM_CHAT_IDS + new_ids)}`\n"
                report += f"`CHAT_LANGUAGES={'de,' * (len(Config.TELEGRAM_CHAT_IDS) + len(new_ids))}`\n"
                report += f"(Sprachen anpassen: de=Deutsch, en=Englisch)\n"
            else:
                report += f"\n✅ *Keine neuen Benutzer*\n"
            
            report += f"\n🌸 Soul Aligned Oils Bot"
            
            # Send report to admin
            logger.info(f"Sending admin report to {admin_id}")
            self.sender.send_message_sync_to_admin(admin_id, report)
            logger.info("Admin report sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send admin report: {e}", exc_info=True)
    
    def process_scheduled_repeats(self):
        """Process and send any pending scheduled repeat messages."""
        try:
            now = datetime.now(self.timezone)
            pending_repeats = self.db.get_pending_repeats(now)
            
            if not pending_repeats:
                return
            
            logger.info(f"Processing {len(pending_repeats)} pending repeat message(s)")
            
            for repeat in pending_repeats:
                user_id = repeat['user_id']
                message_date = date.fromisoformat(repeat['message_date'])
                
                # Get the saved daily message
                daily_msg = self.db.get_daily_message(user_id, message_date)
                
                if daily_msg:
                    message_text = daily_msg['message_text']
                    
                    # Send the message
                    result = self.sender.send_message_sync_to_admin(user_id, message_text)
                    
                    if result.get('success'):
                        self.db.mark_repeat_sent(repeat['id'])
                        logger.info(f"Sent repeat message to {user_id} at {repeat['repeat_time']}")
                    else:
                        logger.error(f"Failed to send repeat message to {user_id}: {result.get('error')}")
                else:
                    logger.warning(f"No daily message found for user {user_id} on {message_date}")
                    self.db.mark_repeat_sent(repeat['id'])  # Mark as sent to avoid retrying
                    
        except Exception as e:
            logger.error(f"Error processing scheduled repeats: {e}", exc_info=True)
    
    def process_user_commands(self):
        """Check for and process incoming user commands."""
        try:
            results = self.sender.check_and_process_messages_sync()
            if results:
                logger.info(f"Processed {len(results)} user command(s)")
        except Exception as e:
            logger.error(f"Error processing user commands: {e}", exc_info=True)
    
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
        
        # Schedule repeat message processing (every minute)
        self.scheduler.add_job(
            func=self.process_scheduled_repeats,
            trigger=IntervalTrigger(minutes=1, timezone=self.timezone),
            id='process_repeats',
            name='Process Scheduled Repeats',
            replace_existing=True
        )
        
        # Schedule command processing (every 5 minutes)
        self.scheduler.add_job(
            func=self.process_user_commands,
            trigger=IntervalTrigger(minutes=5, timezone=self.timezone),
            id='process_commands',
            name='Process User Commands',
            replace_existing=True
        )
        
        logger.info(f"Daily job and periodic jobs configured successfully")
    
    def run_immediately(self, test_mode: bool = False):
        """Run the daily affirmation job immediately.
        
        Args:
            test_mode: If True, only sends to admin ID 5700477215
        """
        if test_mode:
            logger.info("🧪 Manual TEST execution triggered (admin only)")
        else:
            logger.info("Manual execution triggered")
        self.send_daily_affirmation(test_mode)
    
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

