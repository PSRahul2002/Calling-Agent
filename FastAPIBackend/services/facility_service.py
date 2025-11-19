import json
from typing import Dict, Optional
from pathlib import Path
from schemas.booking_schemas import Facility


class FacilityService:
    """Service for managing facility configurations"""
    
    def __init__(self, config_path: str = "config/facilities.json"):
        self.config_path = config_path
        self.facilities: Dict[str, Facility] = {}
        self.phone_to_facility: Dict[str, str] = {}
    
    def load_facilities(self) -> None:
        """Load facility configurations from JSON file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Facilities configuration file not found: {self.config_path}")
        
        with open(config_file, "r") as f:
            data = json.load(f)
        
        for facility_id, facility_data in data.items():
            facility = Facility(**facility_data)
            self.facilities[facility_id] = facility
            self.phone_to_facility[facility_data["phone_number"]] = facility_id
        
        print(f"✓ Loaded {len(self.facilities)} facilities:")
        for fid, facility in self.facilities.items():
            print(f"  - {facility.facility_name} ({fid}): {facility.phone_number}")
    
    def get_facility_by_id(self, facility_id: str) -> Optional[Facility]:
        """Get facility by ID"""
        return self.facilities.get(facility_id)
    
    def get_facility_by_phone(self, phone_number: str) -> Optional[Facility]:
        """Get facility by phone number (called number)"""
        facility_id = self.phone_to_facility.get(phone_number)
        if facility_id:
            return self.facilities.get(facility_id)
        return None
    
    def get_all_facilities(self) -> Dict[str, Facility]:
        """Get all facilities"""
        return self.facilities
    
    def get_facility_system_prompt(self, facility: Facility) -> str:
        """Generate system prompt for a facility"""
        prompt = f"""You are an AI voice assistant for {facility.facility_name}, a sports facility booking system.

FACILITY DETAILS:
- Name: {facility.facility_name}
- Number of Courts: {facility.number_of_courts}
- Operating Hours: {facility.open_time} to {facility.close_time}

BOOKING RULES:
- Minimum Duration: {facility.booking_rules.get('minimum_duration')} minutes
- Slots must be in multiples of: {facility.booking_rules.get('duration_multiples')} minutes
- Fixed Slots (hourly boundaries only): {facility.booking_rules.get('fixed_slots')}

PRICING:
- Weekday (Mon-Fri): ₹{facility.pricing.get('weekday_per_hour')}/hour
- Weekend (Sat-Sun): ₹{facility.pricing.get('weekend_per_hour')}/hour

RENTALS AVAILABLE:
- Racket: ₹{facility.rentals.get('racket', 0)}
- Shoes: ₹{facility.rentals.get('shoes', 0)}
- Shuttle (sale): ₹{facility.rentals.get('shuttle_sale', 0)}

COACHING:
- Available: {facility.coaching.get('available')}
- Fee: ₹{facility.coaching.get('fee', 0)}
- Timings: {', '.join(facility.coaching.get('timings', []))}
- Age Requirement: Below {facility.coaching.get('age_below', 18)} years

YOUR RESPONSIBILITIES:
1. Greet the caller warmly and professionally
2. Collect phone number for booking:
   - If caller ID is present, ask: "Is this the same number you want to use for booking?"
   - If yes, use the caller ID
   - If no or caller ID is missing, ask them to provide their phone number
3. Help them check court availability using the check_availability function
4. Create bookings using the create_booking function
5. Provide information about pricing, rentals, and coaching when asked
6. Be helpful, friendly, and efficient

IMPORTANT BOOKING RULES:
- All bookings must start at hourly boundaries (e.g., 06:00, 14:00, 18:00)
- No half-hour slots allowed (e.g., NO 14:30 or 18:15)
- Duration must be in multiples of 60 minutes only
- Always verify availability before creating a booking

When a caller wants to book, always:
1. Ask for their preferred date and time
2. Check availability using check_availability function
3. If available, collect their name and confirm phone number
4. Create the booking using create_booking function
5. Confirm the booking details back to them

Be conversational, natural, and helpful!"""
        
        return prompt


# Global facility service instance
facility_service = FacilityService()
