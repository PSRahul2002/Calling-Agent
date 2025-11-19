from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging
import asyncio
from datetime import datetime

from services.facility_service import facility_service
from services.booking_service import booking_service
from schemas.function_call_schemas import (
    CheckAvailabilityRequest,
    CreateBookingRequest,
    FUNCTION_DEFINITIONS
)

router = APIRouter(tags=["realtime"])
logger = logging.getLogger(__name__)


class RealtimeSession:
    """Manages a single OpenAI Realtime API session"""
    
    def __init__(self, facility_id: str, caller_number: Optional[str] = None):
        self.facility_id = facility_id
        self.caller_number = caller_number
        self.session_id = f"session_{facility_id}_{datetime.utcnow().timestamp()}"
        self.facility = facility_service.get_facility_by_id(facility_id)
        
        if not self.facility:
            raise ValueError(f"Facility not found: {facility_id}")
    
    def handle_function_call(self, function_name: str, arguments: dict) -> dict:
        """
        Handle function calls from OpenAI Realtime API
        
        Args:
            function_name: Name of the function to call
            arguments: Function arguments
        
        Returns:
            Function result as a dictionary
        """
        try:
            if function_name == "check_availability":
                request = CheckAvailabilityRequest(**arguments)
                response = booking_service.check_availability(request)
                return response.model_dump()
            
            elif function_name == "create_booking":
                request = CreateBookingRequest(**arguments)
                response = booking_service.create_booking(request)
                return response.model_dump()
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
        
        except Exception as e:
            logger.error(f"Error handling function call {function_name}: {e}")
            return {
                "success": False,
                "error": f"Error executing {function_name}: {str(e)}"
            }
    
    def get_system_prompt(self) -> str:
        """Get system prompt for this facility"""
        if not self.facility:
            raise ValueError("Facility not initialized")
        
        base_prompt = facility_service.get_facility_system_prompt(self.facility)
        
        if self.caller_number:
            base_prompt += f"\n\nCALLER ID: {self.caller_number}"
        
        return base_prompt


@router.websocket("/realtime")
async def realtime_websocket(
    websocket: WebSocket,
    facility_id: str = Query(..., description="Facility ID"),
    caller_number: Optional[str] = Query(None, description="Caller phone number")
):
    """
    WebSocket endpoint for OpenAI Realtime API integration
    
    This endpoint:
    1. Accepts WebSocket connection from client
    2. Creates a Realtime session for the facility
    3. Handles bidirectional audio streaming
    4. Processes function calls (check_availability, create_booking)
    5. Returns function results to OpenAI
    
    Protocol:
    - Client sends: audio data, session control messages
    - Server sends: audio responses, function call results
    - Function calls are intercepted and processed locally
    
    Query Parameters:
    - facility_id: Required, identifies which facility is being called
    - caller_number: Optional, caller's phone number
    """
    await websocket.accept()
    session = None
    
    try:
        session = RealtimeSession(facility_id, caller_number)
        logger.info(f"Realtime session started: {session.session_id}")
        
        if not session.facility:
            raise ValueError("Facility not initialized")
        
        await websocket.send_json({
            "type": "session.created",
            "session_id": session.session_id,
            "facility": session.facility.facility_name,
            "system_prompt": session.get_system_prompt(),
            "functions": FUNCTION_DEFINITIONS
        })
        
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                message_type = data.get("type")
                
                if message_type == "function_call":
                    function_name = data.get("function_name")
                    arguments = data.get("arguments", {})
                    
                    logger.info(f"Function call: {function_name} with args: {arguments}")
                    
                    result = session.handle_function_call(function_name, arguments)
                    
                    await websocket.send_json({
                        "type": "function_result",
                        "function_name": function_name,
                        "result": result
                    })
                
                elif message_type == "audio":
                    logger.debug("Received audio data")
                    await websocket.send_json({
                        "type": "audio_received",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message_type == "session.update":
                    logger.info("Session update received")
                    await websocket.send_json({
                        "type": "session.updated",
                        "session_id": session.session_id
                    })
                
                elif message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON format"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session.session_id if session else 'unknown'}")
    
    except Exception as e:
        logger.error(f"Error in realtime WebSocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass
    
    finally:
        logger.info("Realtime session ended")


@router.get("/realtime/status")
async def realtime_status():
    """Status check for realtime router"""
    return {
        "status": "active",
        "endpoint": "/realtime",
        "protocol": "WebSocket",
        "supported_functions": ["check_availability", "create_booking"]
    }
