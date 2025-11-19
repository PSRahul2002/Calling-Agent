from typing import Tuple


def validate_slot_alignment(start_time: str) -> Tuple[bool, str]:
    """
    Validate that start time aligns with hourly boundaries
    Only allows times like 05:00, 06:00, 14:00, etc.
    Does NOT allow 05:30, 14:15, etc.
    
    Args:
        start_time: Time in HH:MM format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        hour, minute = start_time.split(":")
        minute = int(minute)
        
        if minute != 0:
            return False, f"Start time must align with hourly boundaries (e.g., 06:00, 14:00). Got {start_time}"
        
        return True, ""
    except (ValueError, AttributeError):
        return False, f"Invalid time format: {start_time}. Expected HH:MM"


def validate_duration(duration_minutes: int, minimum_duration: int = 60, duration_multiples: int = 60) -> Tuple[bool, str]:
    """
    Validate that duration is a multiple of the required interval
    
    Args:
        duration_minutes: Duration in minutes
        minimum_duration: Minimum allowed duration
        duration_multiples: Duration must be a multiple of this value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if duration_minutes < minimum_duration:
        return False, f"Duration must be at least {minimum_duration} minutes"
    
    if duration_minutes % duration_multiples != 0:
        return False, f"Duration must be a multiple of {duration_multiples} minutes. Got {duration_minutes}"
    
    return True, ""


def validate_booking_slot(start_time: str, duration_minutes: int, booking_rules: dict) -> Tuple[bool, str]:
    """
    Validate complete booking slot against facility rules
    
    Args:
        start_time: Start time in HH:MM format
        duration_minutes: Duration in minutes
        booking_rules: Facility booking rules dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    minimum_duration = booking_rules.get("minimum_duration", 60)
    duration_multiples = booking_rules.get("duration_multiples", 60)
    fixed_slots = booking_rules.get("fixed_slots", True)
    
    if fixed_slots:
        is_aligned, align_msg = validate_slot_alignment(start_time)
        if not is_aligned:
            return False, align_msg
    
    is_valid_duration, duration_msg = validate_duration(
        duration_minutes, 
        minimum_duration, 
        duration_multiples
    )
    if not is_valid_duration:
        return False, duration_msg
    
    return True, ""


def validate_court_numbers(court_numbers: list, number_of_courts: int) -> Tuple[bool, str]:
    """
    Validate that requested court numbers are valid for the facility
    
    Args:
        court_numbers: List of court numbers requested
        number_of_courts: Total number of courts at facility
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not court_numbers:
        return False, "At least one court must be specified"
    
    for court_num in court_numbers:
        if court_num < 1 or court_num > number_of_courts:
            return False, f"Invalid court number {court_num}. Facility has courts 1-{number_of_courts}"
    
    if len(court_numbers) != len(set(court_numbers)):
        return False, "Duplicate court numbers found in request"
    
    return True, ""
