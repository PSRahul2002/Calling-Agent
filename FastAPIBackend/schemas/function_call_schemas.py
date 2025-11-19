from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time


class CheckAvailabilityRequest(BaseModel):
    """Schema for check_availability function call"""
    facility_id: str = Field(..., description="Unique identifier for the facility")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    start_time: str = Field(..., description="Start time in HH:MM format (24-hour)")
    duration_minutes: int = Field(..., description="Duration in minutes (must be multiple of 60)")
    number_of_courts: int = Field(..., description="Number of courts requested")


class CheckAvailabilityResponse(BaseModel):
    """Schema for check_availability function response"""
    success: bool
    available: bool
    free_courts: List[int] = []
    reason_if_not_available: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None


class CreateBookingRequest(BaseModel):
    """Schema for create_booking function call"""
    facility_id: str = Field(..., description="Unique identifier for the facility")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    start_time: str = Field(..., description="Start time in HH:MM format (24-hour)")
    duration_minutes: int = Field(..., description="Duration in minutes (must be multiple of 60)")
    name: str = Field(..., description="Customer name")
    phone_number: str = Field(..., description="Customer phone number")
    court_numbers: List[int] = Field(..., description="List of court numbers to book")


class CreateBookingResponse(BaseModel):
    """Schema for create_booking function response"""
    success: bool
    booking_id: Optional[str] = None
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None


FUNCTION_DEFINITIONS = [
    {
        "type": "function",
        "name": "check_availability",
        "description": "Check availability of courts at a specific facility for a given date and time slot. Returns list of available courts.",
        "parameters": {
            "type": "object",
            "properties": {
                "facility_id": {
                    "type": "string",
                    "description": "Unique identifier for the facility (e.g., 'pickle_x_mysore')"
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (e.g., '2024-12-25')"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in HH:MM format using 24-hour notation (e.g., '14:00' for 2 PM)"
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Duration in minutes, must be a multiple of 60 (e.g., 60, 120, 180)"
                },
                "number_of_courts": {
                    "type": "integer",
                    "description": "Number of courts requested (e.g., 1, 2)"
                }
            },
            "required": ["facility_id", "date", "start_time", "duration_minutes", "number_of_courts"]
        }
    },
    {
        "type": "function",
        "name": "create_booking",
        "description": "Create a booking for specific courts at a facility. This creates an event in Google Calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "facility_id": {
                    "type": "string",
                    "description": "Unique identifier for the facility (e.g., 'pickle_x_mysore')"
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (e.g., '2024-12-25')"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in HH:MM format using 24-hour notation (e.g., '14:00' for 2 PM)"
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Duration in minutes, must be a multiple of 60 (e.g., 60, 120)"
                },
                "name": {
                    "type": "string",
                    "description": "Customer's full name"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Customer's phone number with country code (e.g., '+919876543210')"
                },
                "court_numbers": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of court numbers to book (e.g., [1, 2])"
                }
            },
            "required": ["facility_id", "date", "start_time", "duration_minutes", "name", "phone_number", "court_numbers"]
        }
    }
]
