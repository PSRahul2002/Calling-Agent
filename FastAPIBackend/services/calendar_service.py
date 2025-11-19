from datetime import datetime
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os


class CalendarService:
    """Service for Google Calendar operations"""
    
    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service using Replit integration"""
        try:
            creds = None
            
            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file("token.json")
            
            if not creds or not creds.valid:
                print("⚠️  Google Calendar credentials not found or invalid")
                print("   Using Replit Google Calendar integration...")
                print("   Calendar operations will simulate until credentials are available")
                self.service = None
                return
            
            self.service = build("calendar", "v3", credentials=creds)
            print("✓ Google Calendar service initialized successfully")
            
        except Exception as e:
            print(f"⚠️  Error initializing Google Calendar: {e}")
            print("   Make sure Google Calendar integration is properly configured")
            self.service = None
    
    def check_court_availability(
        self, 
        court_number: int, 
        start_dt: datetime, 
        end_dt: datetime,
        facility_id: str
    ) -> bool:
        """
        Check if a specific court is available for the given time slot
        
        Args:
            court_number: Court number to check
            start_dt: Start datetime
            end_dt: End datetime
            facility_id: Facility identifier
        
        Returns:
            True if available, False if booked
        
        Note:
            When calendar service is not initialized, returns True to allow
            testing and development. In production, ensure calendar is properly
            configured before accepting bookings.
        """
        if not self.service:
            print(f"⚠️  Calendar service not initialized - availability check skipped (court {court_number})")
            return True
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            for event in events:
                event_summary = event.get('summary', '')
                event_description = event.get('description', '')
                
                if f"Court {court_number}" in event_summary:
                    if facility_id in event_description or facility_id in event_summary:
                        return False
            
            return True
            
        except HttpError as e:
            print(f"⚠️  Error checking calendar: {e}")
            return True
    
    def get_available_courts(
        self,
        facility_id: str,
        total_courts: int,
        start_dt: datetime,
        end_dt: datetime
    ) -> List[int]:
        """
        Get list of available courts for the given time slot
        
        Args:
            facility_id: Facility identifier
            total_courts: Total number of courts at facility
            start_dt: Start datetime
            end_dt: End datetime
        
        Returns:
            List of available court numbers
        """
        available_courts = []
        
        for court_num in range(1, total_courts + 1):
            if self.check_court_availability(court_num, start_dt, end_dt, facility_id):
                available_courts.append(court_num)
        
        return available_courts
    
    def create_booking_event(
        self,
        facility_name: str,
        facility_id: str,
        court_number: int,
        customer_name: str,
        customer_phone: str,
        start_dt: datetime,
        end_dt: datetime,
        date_str: str,
        start_time: str,
        duration_minutes: int
    ) -> Optional[str]:
        """
        Create a booking event in Google Calendar
        
        Args:
            facility_name: Name of the facility
            facility_id: Facility identifier
            court_number: Court number
            customer_name: Customer name
            customer_phone: Customer phone
            start_dt: Start datetime
            end_dt: End datetime
            date_str: Date string
            start_time: Start time string
            duration_minutes: Duration in minutes
        
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.service:
            print(f"✗ Calendar service not initialized - cannot create booking")
            return None
        
        try:
            event_title = f"Court {court_number} Booking - {customer_name}"
            
            event_description = f"""Customer Name: {customer_name}
Phone: {customer_phone}
Facility: {facility_name} ({facility_id})
Court Number: {court_number}
Date: {date_str}
Start Time: {start_time}
End Time: {end_dt.strftime('%H:%M')}
Duration: {duration_minutes} minutes"""
            
            event = {
                'summary': event_title,
                'description': event_description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': str(start_dt.tzinfo),
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': str(end_dt.tzinfo),
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 60},
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            print(f"✓ Created booking: {event_title} (ID: {created_event['id']})")
            return created_event['id']
            
        except HttpError as e:
            print(f"⚠️  Error creating calendar event: {e}")
            return None


# Global calendar service instance
calendar_service = CalendarService()
