"""
Database Module
Handles all database operations for reactions, lunar calendar, scheduled repeats,
oil database, and command logging.
"""

import sqlite3
import json
import logging
import os
from datetime import datetime, date, time
from typing import List, Dict, Optional
from contextlib import contextmanager

from config import Config

logger = logging.getLogger(__name__)


class Database:
    """Handles all database operations."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                'data',
                'bot_database.db'
            )
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialize_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create all required tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Reactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message_date DATE NOT NULL,
                    reaction TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, message_date)
                )
            """)
            
            # Lunar calendar table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lunar_calendar (
                    date DATE PRIMARY KEY,
                    moon_phase TEXT,
                    is_portal_day BOOLEAN DEFAULT 0
                )
            """)
            
            # Scheduled repeats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_repeats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message_date DATE NOT NULL,
                    repeat_time TIME NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sent_at DATETIME
                )
            """)
            
            # Oils database table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS oils_database (
                    oil_name TEXT PRIMARY KEY,
                    alternative_names TEXT,
                    energetic_effects TEXT,
                    main_components TEXT,
                    interesting_facts TEXT,
                    seasonal_fit TEXT,
                    weekday_energy_match TEXT,
                    contraindications TEXT,
                    best_uses TEXT
                )
            """)
            
            # User command log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_command_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    parameters TEXT,
                    response_sent BOOLEAN DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Interaction attempts table (for strict Info-only model)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interaction_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    attempted_command TEXT,
                    was_allowed BOOLEAN,
                    oil_requested TEXT,
                    daily_primary_oil TEXT,
                    daily_alternative_oil TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Daily messages cache (store today's message per user)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message_date DATE NOT NULL,
                    message_text TEXT NOT NULL,
                    primary_oil TEXT,
                    alternative_oil TEXT,
                    message_type TEXT DEFAULT 'regular',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, message_date)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    # ============= REACTIONS =============
    
    def add_reaction(self, user_id: str, message_date: date, reaction: str) -> bool:
        """Add or update a reaction to a message."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO reactions (user_id, message_date, reaction, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (user_id, message_date.isoformat(), reaction, datetime.now()))
                return True
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")
            return False
    
    def get_reactions_for_date(self, message_date: date) -> List[Dict]:
        """Get all reactions for a specific date."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, reaction, timestamp
                    FROM reactions
                    WHERE message_date = ?
                    ORDER BY timestamp
                """, (message_date.isoformat(),))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting reactions: {e}")
            return []
    
    def get_reaction_stats(self, start_date: date, end_date: date) -> Dict:
        """Get reaction statistics for a date range."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT reaction, COUNT(*) as count
                    FROM reactions
                    WHERE message_date BETWEEN ? AND ?
                    GROUP BY reaction
                """, (start_date.isoformat(), end_date.isoformat()))
                results = cursor.fetchall()
                return {row['reaction']: row['count'] for row in results}
        except Exception as e:
            logger.error(f"Error getting reaction stats: {e}")
            return {}
    
    # ============= LUNAR CALENDAR =============
    
    def add_lunar_event(self, event_date: date, moon_phase: str, is_portal_day: bool = False):
        """Add or update a lunar calendar event."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO lunar_calendar (date, moon_phase, is_portal_day)
                    VALUES (?, ?, ?)
                """, (event_date.isoformat(), moon_phase, 1 if is_portal_day else 0))
                return True
        except Exception as e:
            logger.error(f"Error adding lunar event: {e}")
            return False
    
    def get_lunar_event(self, event_date: date) -> Optional[Dict]:
        """Get lunar event for a specific date."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT date, moon_phase, is_portal_day
                    FROM lunar_calendar
                    WHERE date = ?
                """, (event_date.isoformat(),))
                row = cursor.fetchone()
                if row:
                    return {
                        'date': date.fromisoformat(row['date']),
                        'moon_phase': row['moon_phase'],
                        'is_portal_day': bool(row['is_portal_day'])
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting lunar event: {e}")
            return None
    
    def is_portal_day(self, event_date: date) -> bool:
        """Check if a date is a portal day."""
        event = self.get_lunar_event(event_date)
        return event['is_portal_day'] if event else False
    
    def get_moon_phase(self, event_date: date) -> Optional[str]:
        """Get moon phase for a specific date."""
        event = self.get_lunar_event(event_date)
        return event['moon_phase'] if event else None
    
    # ============= SCHEDULED REPEATS =============
    
    def schedule_repeat(self, user_id: str, message_date: date, repeat_time: time) -> bool:
        """Schedule a message repeat for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO scheduled_repeats (user_id, message_date, repeat_time, status)
                    VALUES (?, ?, ?, 'pending')
                """, (user_id, message_date.isoformat(), repeat_time.isoformat()))
                return True
        except Exception as e:
            logger.error(f"Error scheduling repeat: {e}")
            return False
    
    def get_pending_repeats(self, current_datetime: datetime) -> List[Dict]:
        """Get all pending repeats that should be sent now."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                current_date = current_datetime.date()
                current_time = current_datetime.time()
                
                cursor.execute("""
                    SELECT id, user_id, message_date, repeat_time
                    FROM scheduled_repeats
                    WHERE status = 'pending'
                    AND message_date = ?
                    AND repeat_time <= ?
                    ORDER BY repeat_time
                """, (current_date.isoformat(), current_time.isoformat()))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting pending repeats: {e}")
            return []
    
    def mark_repeat_sent(self, repeat_id: int):
        """Mark a repeat as sent."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE scheduled_repeats
                    SET status = 'sent', sent_at = ?
                    WHERE id = ?
                """, (datetime.now(), repeat_id))
        except Exception as e:
            logger.error(f"Error marking repeat as sent: {e}")
    
    # ============= OILS DATABASE =============
    
    def add_oil(self, oil_data: Dict) -> bool:
        """Add or update an oil in the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO oils_database (
                        oil_name, alternative_names, energetic_effects,
                        main_components, interesting_facts, seasonal_fit,
                        weekday_energy_match, contraindications, best_uses
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    oil_data['oil_name'],
                    json.dumps(oil_data.get('alternative_names', [])),
                    oil_data.get('energetic_effects', ''),
                    json.dumps(oil_data.get('main_components', [])),
                    oil_data.get('interesting_facts', ''),
                    json.dumps(oil_data.get('seasonal_fit', [])),
                    json.dumps(oil_data.get('weekday_energy_match', [])),
                    oil_data.get('contraindications', ''),
                    json.dumps(oil_data.get('best_uses', []))
                ))
                return True
        except Exception as e:
            logger.error(f"Error adding oil: {e}")
            return False
    
    def get_oil(self, oil_name: str) -> Optional[Dict]:
        """Get oil information by name (supports fuzzy matching)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # First try exact match
                cursor.execute("SELECT * FROM oils_database WHERE oil_name = ?", (oil_name,))
                row = cursor.fetchone()
                
                if not row:
                    # Try case-insensitive match
                    cursor.execute("SELECT * FROM oils_database WHERE LOWER(oil_name) = LOWER(?)", (oil_name,))
                    row = cursor.fetchone()
                
                if not row:
                    # Try matching in alternative names
                    cursor.execute("SELECT * FROM oils_database WHERE alternative_names LIKE ?", 
                                 (f'%{oil_name}%',))
                    row = cursor.fetchone()
                
                if row:
                    return {
                        'oil_name': row['oil_name'],
                        'alternative_names': json.loads(row['alternative_names'] or '[]'),
                        'energetic_effects': row['energetic_effects'],
                        'main_components': json.loads(row['main_components'] or '[]'),
                        'interesting_facts': row['interesting_facts'],
                        'seasonal_fit': json.loads(row['seasonal_fit'] or '[]'),
                        'weekday_energy_match': json.loads(row['weekday_energy_match'] or '[]'),
                        'contraindications': row['contraindications'],
                        'best_uses': json.loads(row['best_uses'] or '[]')
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting oil: {e}")
            return None
    
    def search_oils(self, query: str, limit: int = 10) -> List[str]:
        """Search for oils by name."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT oil_name FROM oils_database
                    WHERE LOWER(oil_name) LIKE LOWER(?)
                    OR LOWER(alternative_names) LIKE LOWER(?)
                    LIMIT ?
                """, (f'%{query}%', f'%{query}%', limit))
                return [row['oil_name'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching oils: {e}")
            return []
    
    # ============= COMMAND LOG =============
    
    def log_command(self, user_id: str, command: str, parameters: str = None, response_sent: bool = False):
        """Log a user command."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_command_log (user_id, command, parameters, response_sent)
                    VALUES (?, ?, ?, ?)
                """, (user_id, command, parameters, 1 if response_sent else 0))
        except Exception as e:
            logger.error(f"Error logging command: {e}")
    
    # ============= INTERACTION ATTEMPTS =============
    
    def log_interaction_attempt(
        self,
        user_id: str,
        attempted_command: str,
        was_allowed: bool,
        oil_requested: str = None,
        daily_primary_oil: str = None,
        daily_alternative_oil: str = None,
    ):
        """Log an interaction attempt for analytics (e.g., disallowed commands)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO interaction_attempts (
                        user_id,
                        attempted_command,
                        was_allowed,
                        oil_requested,
                        daily_primary_oil,
                        daily_alternative_oil
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        attempted_command,
                        1 if was_allowed else 0,
                        oil_requested,
                        daily_primary_oil,
                        daily_alternative_oil,
                    ),
                )
        except Exception as e:
            logger.error(f"Error logging interaction attempt: {e}")
    
    # ============= DAILY MESSAGES CACHE =============
    
    def save_daily_message(self, user_id: str, message_date: date, message_text: str,
                          primary_oil: str = None, alternative_oil: str = None,
                          message_type: str = 'regular'):
        """Save a daily message for later retrieval."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_messages 
                    (user_id, message_date, message_text, primary_oil, alternative_oil, message_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, message_date.isoformat(), message_text, primary_oil, 
                     alternative_oil, message_type))
        except Exception as e:
            logger.error(f"Error saving daily message: {e}")
    
    def get_daily_message(self, user_id: str, message_date: date) -> Optional[Dict]:
        """Get the daily message for a user on a specific date."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM daily_messages
                    WHERE user_id = ? AND message_date = ?
                """, (user_id, message_date.isoformat()))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error getting daily message: {e}")
            return None
    
    def get_recently_used_oils(self, user_id: str, days: int = 14) -> List[str]:
        """Get list of oils used by a user in the last N days.
        
        Args:
            user_id: The user's chat ID
            days: Number of days to look back (default 14)
            
        Returns:
            List of unique oil names (primary and alternative) used in the period
        """
        try:
            from datetime import timedelta
            cutoff_date = (date.today() - timedelta(days=days)).isoformat()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT primary_oil, alternative_oil
                    FROM daily_messages
                    WHERE user_id = ? AND message_date >= ? 
                    AND (primary_oil IS NOT NULL OR alternative_oil IS NOT NULL)
                """, (user_id, cutoff_date))
                
                rows = cursor.fetchall()
                oils = set()
                for row in rows:
                    if row['primary_oil']:
                        oils.add(row['primary_oil'])
                    if row['alternative_oil']:
                        oils.add(row['alternative_oil'])
                
                return list(oils)
        except Exception as e:
            logger.error(f"Error getting recently used oils: {e}")
            return []
