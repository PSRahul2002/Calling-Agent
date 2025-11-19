from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class Facility(BaseModel):
    """Facility configuration model"""
    facility_id: str
    facility_name: str
    phone_number: str
    number_of_courts: int
    open_time: str
    close_time: str
    booking_rules: Dict[str, Any]
    pricing: Dict[str, int]
    rentals: Dict[str, int]
    coaching: Dict[str, Any]


class WebhookRequest(BaseModel):
    """Twilio/Exotel webhook request model"""
    CallSid: Optional[str] = None
    From: Optional[str] = None
    To: Optional[str] = None
    CallStatus: Optional[str] = None
    Direction: Optional[str] = None


class SessionData(BaseModel):
    """Real-time session data model"""
    session_id: str
    facility_id: str
    caller_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
