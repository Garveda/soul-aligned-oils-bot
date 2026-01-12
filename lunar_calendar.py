"""
Lunar Calendar Module
Handles moon phase calculations and portal days detection.
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict

from database import Database

logger = logging.getLogger(__name__)


class LunarCalendar:
    """Manages lunar calendar and portal days."""
    
    # Portal days for 2024-2026 (from Maya calendar)
    # These are specific dates known as "portal days" with heightened energy
    PORTAL_DAYS = {
        # 2024
        '2024-01-01', '2024-01-11', '2024-01-22',
        '2024-02-02', '2024-02-12', '2024-02-23',
        '2024-03-04', '2024-03-15', '2024-03-26',
        '2024-04-05', '2024-04-16', '2024-04-27',
        '2024-05-08', '2024-05-19', '2024-05-30',
        '2024-06-10', '2024-06-21', '2024-07-02',
        '2024-07-13', '2024-07-24', '2024-08-04',
        '2024-08-15', '2024-08-26', '2024-09-06',
        '2024-09-17', '2024-09-28', '2024-10-09',
        '2024-10-20', '2024-10-31', '2024-11-11',
        '2024-11-22', '2024-12-03', '2024-12-14',
        '2024-12-25',
        
        # 2025
        '2025-01-05', '2025-01-16', '2025-01-27',
        '2025-02-07', '2025-02-18', '2025-03-01',
        '2025-03-12', '2025-03-23', '2025-04-03',
        '2025-04-14', '2025-04-25', '2025-05-06',
        '2025-05-17', '2025-05-28', '2025-06-08',
        '2025-06-19', '2025-06-30', '2025-07-11',
        '2025-07-22', '2025-08-02', '2025-08-13',
        '2025-08-24', '2025-09-04', '2025-09-15',
        '2025-09-26', '2025-10-07', '2025-10-18',
        '2025-10-29', '2025-11-09', '2025-11-20',
        '2025-12-01', '2025-12-12', '2025-12-23',
        
        # 2026
        '2026-01-03', '2026-01-14', '2026-01-25',
        '2026-02-05', '2026-02-16', '2026-02-27',
        '2026-03-10', '2026-03-21', '2026-04-01',
        '2026-04-12', '2026-04-23', '2026-05-04',
        '2026-05-15', '2026-05-26', '2026-06-06',
        '2026-06-17', '2026-06-28', '2026-07-09',
        '2026-07-20', '2026-07-31', '2026-08-11',
        '2026-08-22', '2026-09-02', '2026-09-13',
        '2026-09-24', '2026-10-05', '2026-10-16',
        '2026-10-27', '2026-11-07', '2026-11-18',
        '2026-11-29', '2026-12-10', '2026-12-21',
    }
    
    def __init__(self, db: Database):
        """Initialize lunar calendar."""
        self.db = db
        logger.info("Lunar calendar initialized")
    
    def is_portal_day(self, check_date: date = None) -> bool:
        """Check if a date is a portal day."""
        if check_date is None:
            check_date = date.today()
        date_str = check_date.isoformat()
        return date_str in self.PORTAL_DAYS
    
    def get_moon_phase(self, check_date: date = None) -> Optional[str]:
        """Get moon phase for a date using API or calculation."""
        if check_date is None:
            check_date = date.today()
        
        # First check database
        event = self.db.get_lunar_event(check_date)
        if event and event.get('moon_phase'):
            return event['moon_phase']
        
        # Try to calculate or fetch from API
        try:
            moon_phase = self._calculate_moon_phase(check_date)
            # Save to database
            self.db.add_lunar_event(check_date, moon_phase, self.is_portal_day(check_date))
            return moon_phase
        except Exception as e:
            logger.error(f"Error calculating moon phase: {e}")
            return None
    
    def _calculate_moon_phase(self, check_date: date) -> str:
        """Calculate approximate moon phase using a simple algorithm."""
        # Simple approximation: cycle length ~29.53 days
        # Known new moon reference: 2024-01-11 (example)
        reference_new_moon = date(2024, 1, 11)
        days_since_reference = (check_date - reference_new_moon).days
        
        cycle_position = (days_since_reference % 29.53) / 29.53
        
        if cycle_position < 0.03 or cycle_position > 0.97:
            return 'new_moon'
        elif cycle_position < 0.22:
            return 'waxing_crescent'
        elif cycle_position < 0.28:
            return 'first_quarter'
        elif cycle_position < 0.47:
            return 'waxing_gibbous'
        elif cycle_position < 0.53:
            return 'full_moon'
        elif cycle_position < 0.72:
            return 'waning_gibbous'
        elif cycle_position < 0.78:
            return 'last_quarter'
        else:
            return 'waning_crescent'
    
    def get_special_day_info(self, check_date: date = None) -> Dict:
        """Get all special day information (portal, moon phase)."""
        if check_date is None:
            check_date = date.today()
        
        moon_phase = self.get_moon_phase(check_date)
        is_portal = self.is_portal_day(check_date)
        
        # Determine priority message type
        message_type = 'regular'
        if is_portal:
            message_type = 'portal'
        elif moon_phase == 'full_moon':
            message_type = 'full_moon'
        elif moon_phase == 'new_moon':
            message_type = 'new_moon'
        
        return {
            'date': check_date,
            'moon_phase': moon_phase,
            'is_portal_day': is_portal,
            'message_type': message_type
        }
    
    def populate_lunar_calendar(self, start_date: date, end_date: date):
        """Populate lunar calendar for a date range."""
        current_date = start_date
        count = 0
        
        while current_date <= end_date:
            moon_phase = self._calculate_moon_phase(current_date)
            is_portal = self.is_portal_day(current_date)
            self.db.add_lunar_event(current_date, moon_phase, is_portal)
            count += 1
            current_date += timedelta(days=1)
        
        logger.info(f"Populated lunar calendar for {count} days")
        return count
