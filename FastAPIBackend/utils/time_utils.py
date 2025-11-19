from datetime import datetime, timedelta, time as dt_time
from typing import Tuple
import pytz


def parse_time(time_str: str) -> dt_time:
    """
    Parse time string in HH:MM format to time object
    
    Args:
        time_str: Time in HH:MM format (e.g., "14:00")
    
    Returns:
        datetime.time object
    """
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError as e:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM format.") from e


def parse_date(date_str: str) -> datetime:
    """
    Parse date string in YYYY-MM-DD format to datetime object
    
    Args:
        date_str: Date in YYYY-MM-DD format (e.g., "2024-12-25")
    
    Returns:
        datetime object
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD format.") from e


def combine_datetime(date_str: str, time_str: str, timezone_str: str = "Asia/Kolkata") -> datetime:
    """
    Combine date and time strings into a timezone-aware datetime object
    
    Args:
        date_str: Date in YYYY-MM-DD format
        time_str: Time in HH:MM format
        timezone_str: Timezone string (default: Asia/Kolkata)
    
    Returns:
        Timezone-aware datetime object
    """
    date_obj = parse_date(date_str)
    time_obj = parse_time(time_str)
    
    naive_dt = datetime.combine(date_obj.date(), time_obj)
    
    tz = pytz.timezone(timezone_str)
    return tz.localize(naive_dt)


def get_end_datetime(start_dt: datetime, duration_minutes: int) -> datetime:
    """
    Calculate end datetime from start datetime and duration
    
    Args:
        start_dt: Start datetime
        duration_minutes: Duration in minutes
    
    Returns:
        End datetime
    """
    return start_dt + timedelta(minutes=duration_minutes)


def format_datetime_for_calendar(dt: datetime) -> str:
    """
    Format datetime for Google Calendar API (RFC3339 format)
    
    Args:
        dt: Datetime object
    
    Returns:
        RFC3339 formatted string
    """
    return dt.isoformat()


def is_within_operating_hours(start_time: str, end_time: str, open_time: str, close_time: str) -> Tuple[bool, str]:
    """
    Check if booking time is within facility operating hours
    
    Args:
        start_time: Booking start time in HH:MM format
        end_time: Booking end time in HH:MM format
        open_time: Facility open time in HH:MM format
        close_time: Facility close time in HH:MM format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        start = parse_time(start_time)
        end = parse_time(end_time)
        open_t = parse_time(open_time)
        close_t = parse_time(close_time)
        
        if start < open_t:
            return False, f"Facility opens at {open_time}"
        
        if end > close_t:
            return False, f"Facility closes at {close_time}"
        
        return True, ""
    except ValueError as e:
        return False, str(e)


def calculate_end_time(start_time: str, duration_minutes: int) -> str:
    """
    Calculate end time from start time and duration
    
    Args:
        start_time: Start time in HH:MM format
        duration_minutes: Duration in minutes
    
    Returns:
        End time in HH:MM format
    """
    start = parse_time(start_time)
    start_dt = datetime.combine(datetime.today(), start)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return end_dt.strftime("%H:%M")
