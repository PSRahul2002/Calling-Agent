from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from services.facility_service import facility_service
import logging

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)


@router.post("/webhook")
async def voice_webhook(request: Request):
    """
    Twilio/Exotel webhook endpoint for incoming calls
    
    This endpoint:
    1. Receives incoming call data from Twilio/Exotel
    2. Identifies facility based on called phone number
    3. Returns TwiML/Exotel response to connect to AI
    
    For production use, this would:
    - Connect to OpenAI Realtime API via WebSocket
    - Stream audio bidirectionally
    - Handle function calls during the conversation
    """
    try:
        form_data = await request.form()
        
        call_sid = str(form_data.get("CallSid", ""))
        from_number = str(form_data.get("From", ""))
        to_number = str(form_data.get("To", ""))
        call_status = str(form_data.get("CallStatus", ""))
        
        logger.info(f"Incoming call: SID={call_sid}, From={from_number}, To={to_number}, Status={call_status}")
        
        facility = facility_service.get_facility_by_phone(to_number)
        
        if not facility:
            logger.warning(f"No facility found for phone number: {to_number}")
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>We're sorry, this facility is not configured. Please try again later.</Say>
    <Hangup/>
</Response>"""
            return Response(content=twiml, media_type="application/xml")
        
        logger.info(f"Call routed to facility: {facility.facility_name} ({facility.facility_id})")
        
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Welcome to {facility.facility_name}. Please hold while we connect you to our AI assistant.</Say>
    <Pause length="1"/>
    <Say>This is a demo webhook. In production, this would connect to the OpenAI Realtime API via WebSocket.</Say>
</Response>"""
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in voice webhook: {e}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>We're sorry, an error occurred. Please try again later.</Say>
    <Hangup/>
</Response>"""
        return Response(content=twiml, media_type="application/xml")


@router.get("/webhook")
async def voice_webhook_get():
    """GET endpoint for webhook verification"""
    return {"status": "ok", "message": "Voice webhook endpoint is active"}


@router.get("/status")
async def voice_status():
    """Status check for voice router"""
    facilities = facility_service.get_all_facilities()
    return {
        "status": "active",
        "facilities_loaded": len(facilities),
        "facility_ids": list(facilities.keys())
    }
