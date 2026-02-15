"""Clock module for time operations."""
from datetime import datetime, timezone
from typing import Optional
from dateutil import parser as date_parser


class Clock:
    """Utility class for time operations."""
    
    @staticmethod
    def now() -> datetime:
        """Get current UTC datetime."""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse date string to datetime."""
        try:
            return date_parser.parse(date_str)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def format_date(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime to string."""
        return dt.strftime(format_str)
    
    @staticmethod
    def is_past(dt: datetime) -> bool:
        """Check if datetime is in the past."""
        return dt < Clock.now()
    
    @staticmethod
    def is_this_week(dt: datetime) -> bool:
        """Check if datetime is in current week."""
        now = Clock.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)
        return week_start <= dt < week_end


from datetime import timedelta
