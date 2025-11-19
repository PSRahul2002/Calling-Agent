from typing import Dict, List
from datetime import datetime
from services.calendar_service import calendar_service
from services.facility_service import facility_service
from utils.time_utils import combine_datetime, get_end_datetime, calculate_end_time, is_within_operating_hours
from utils.slot_utils import validate_booking_slot, validate_court_numbers
from schemas.function_call_schemas import (
    CheckAvailabilityRequest,
    CheckAvailabilityResponse,
    CreateBookingRequest,
    CreateBookingResponse
)


class BookingService:
    """Service for handling booking operations"""
    
    def check_availability(self, request: CheckAvailabilityRequest) -> CheckAvailabilityResponse:
        """
        Check availability of courts for a specific time slot
        
        Args:
            request: CheckAvailabilityRequest with facility_id, date, start_time, duration, courts
        
        Returns:
            CheckAvailabilityResponse with availability status and free courts
        """
        try:
            facility = facility_service.get_facility_by_id(request.facility_id)
            if not facility:
                return CheckAvailabilityResponse(
                    success=False,
                    available=False,
                    error=f"Facility not found: {request.facility_id}"
                )
            
            is_valid_slot, slot_error = validate_booking_slot(
                request.start_time,
                request.duration_minutes,
                facility.booking_rules
            )
            if not is_valid_slot:
                return CheckAvailabilityResponse(
                    success=False,
                    available=False,
                    reason_if_not_available=slot_error
                )
            
            end_time = calculate_end_time(request.start_time, request.duration_minutes)
            is_in_hours, hours_error = is_within_operating_hours(
                request.start_time,
                end_time,
                facility.open_time,
                facility.close_time
            )
            if not is_in_hours:
                return CheckAvailabilityResponse(
                    success=False,
                    available=False,
                    reason_if_not_available=hours_error
                )
            
            start_dt = combine_datetime(request.date, request.start_time)
            end_dt = get_end_datetime(start_dt, request.duration_minutes)
            
            available_courts = calendar_service.get_available_courts(
                facility.facility_id,
                facility.number_of_courts,
                start_dt,
                end_dt
            )
            
            if len(available_courts) < request.number_of_courts:
                return CheckAvailabilityResponse(
                    success=True,
                    available=False,
                    free_courts=available_courts,
                    reason_if_not_available=f"Only {len(available_courts)} court(s) available, but {request.number_of_courts} requested",
                    data={
                        "available_courts": available_courts,
                        "requested_courts": request.number_of_courts
                    }
                )
            
            return CheckAvailabilityResponse(
                success=True,
                available=True,
                free_courts=available_courts,
                data={
                    "available_courts": available_courts,
                    "total_courts": facility.number_of_courts,
                    "date": request.date,
                    "start_time": request.start_time,
                    "duration_minutes": request.duration_minutes
                }
            )
            
        except Exception as e:
            return CheckAvailabilityResponse(
                success=False,
                available=False,
                error=f"Error checking availability: {str(e)}"
            )
    
    def create_booking(self, request: CreateBookingRequest) -> CreateBookingResponse:
        """
        Create a booking for specific courts
        
        Args:
            request: CreateBookingRequest with booking details
        
        Returns:
            CreateBookingResponse with booking confirmation or error
        """
        try:
            if not calendar_service.service:
                return CreateBookingResponse(
                    success=False,
                    error="Calendar service is not initialized. Please configure Google Calendar integration."
                )
            
            facility = facility_service.get_facility_by_id(request.facility_id)
            if not facility:
                return CreateBookingResponse(
                    success=False,
                    error=f"Facility not found: {request.facility_id}"
                )
            
            is_valid_slot, slot_error = validate_booking_slot(
                request.start_time,
                request.duration_minutes,
                facility.booking_rules
            )
            if not is_valid_slot:
                return CreateBookingResponse(
                    success=False,
                    error=f"Invalid slot: {slot_error}"
                )
            
            is_valid_courts, courts_error = validate_court_numbers(
                request.court_numbers,
                facility.number_of_courts
            )
            if not is_valid_courts:
                return CreateBookingResponse(
                    success=False,
                    error=f"Invalid court numbers: {courts_error}"
                )
            
            end_time = calculate_end_time(request.start_time, request.duration_minutes)
            is_in_hours, hours_error = is_within_operating_hours(
                request.start_time,
                end_time,
                facility.open_time,
                facility.close_time
            )
            if not is_in_hours:
                return CreateBookingResponse(
                    success=False,
                    error=f"Outside operating hours: {hours_error}"
                )
            
            start_dt = combine_datetime(request.date, request.start_time)
            end_dt = get_end_datetime(start_dt, request.duration_minutes)
            
            available_courts = calendar_service.get_available_courts(
                facility.facility_id,
                facility.number_of_courts,
                start_dt,
                end_dt
            )
            
            for court_num in request.court_numbers:
                if court_num not in available_courts:
                    return CreateBookingResponse(
                        success=False,
                        error=f"Court {court_num} is not available at the requested time"
                    )
            
            booking_ids = []
            for court_num in request.court_numbers:
                event_id = calendar_service.create_booking_event(
                    facility_name=facility.facility_name,
                    facility_id=facility.facility_id,
                    court_number=court_num,
                    customer_name=request.name,
                    customer_phone=request.phone_number,
                    start_dt=start_dt,
                    end_dt=end_dt,
                    date_str=request.date,
                    start_time=request.start_time,
                    duration_minutes=request.duration_minutes
                )
                if event_id:
                    booking_ids.append(event_id)
            
            if not booking_ids:
                return CreateBookingResponse(
                    success=False,
                    error="Failed to create calendar events"
                )
            
            return CreateBookingResponse(
                success=True,
                booking_id=",".join(booking_ids),
                message=f"Booking confirmed for {request.name}! Courts {', '.join(map(str, request.court_numbers))} on {request.date} at {request.start_time} for {request.duration_minutes} minutes.",
                data={
                    "facility": facility.facility_name,
                    "court_numbers": request.court_numbers,
                    "date": request.date,
                    "start_time": request.start_time,
                    "end_time": end_time,
                    "duration_minutes": request.duration_minutes,
                    "customer_name": request.name,
                    "customer_phone": request.phone_number,
                    "booking_ids": booking_ids
                }
            )
            
        except Exception as e:
            return CreateBookingResponse(
                success=False,
                error=f"Error creating booking: {str(e)}"
            )


# Global booking service instance
booking_service = BookingService()
