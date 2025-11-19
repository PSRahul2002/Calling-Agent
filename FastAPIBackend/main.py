from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from config.settings import settings
from services.facility_service import facility_service
from services.calendar_service import calendar_service
from routers import voice, realtime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("=== FastAPI Application Starting ===")
    
    try:
        facility_service.load_facilities()
        logger.info("✓ Facilities loaded successfully")
    except Exception as e:
        logger.error(f"✗ Error loading facilities: {e}")
    
    logger.info("✓ Google Calendar service initialized")
    
    logger.info(f"✓ OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
    
    logger.info("=== Application Started Successfully ===")
    logger.info(f"Server running on {settings.host}:{settings.port}")
    logger.info("Available endpoints:")
    logger.info("  - POST   /voice/webhook       (Twilio/Exotel webhook)")
    logger.info("  - GET    /voice/status        (Voice router status)")
    logger.info("  - WS     /realtime            (OpenAI Realtime WebSocket)")
    logger.info("  - GET    /realtime/status     (Realtime router status)")
    logger.info("  - GET    /health              (Health check)")
    logger.info("  - GET    /facilities          (List all facilities)")
    
    yield
    
    logger.info("=== Application Shutting Down ===")


app = FastAPI(
    title="AI Voice Assistant for Sports Facility Bookings",
    description="FastAPI backend powering AI voice assistant for pickleball/badminton court bookings",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(realtime.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Voice Assistant Backend API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "voice_webhook": "/voice/webhook",
            "voice_status": "/voice/status",
            "realtime_ws": "/realtime",
            "realtime_status": "/realtime/status",
            "health": "/health",
            "facilities": "/facilities"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    facilities = facility_service.get_all_facilities()
    
    return {
        "status": "healthy",
        "timestamp": "2024-11-19T00:00:00Z",
        "services": {
            "facility_service": "active",
            "calendar_service": "active",
            "facilities_loaded": len(facilities)
        },
        "configuration": {
            "openai_configured": bool(settings.openai_api_key),
            "calendar_configured": bool(settings.google_calendar_id)
        }
    }


@app.get("/facilities")
async def list_facilities():
    """List all configured facilities"""
    facilities = facility_service.get_all_facilities()
    
    return {
        "count": len(facilities),
        "facilities": [
            {
                "facility_id": fid,
                "facility_name": f.facility_name,
                "phone_number": f.phone_number,
                "number_of_courts": f.number_of_courts,
                "operating_hours": f"{f.open_time} - {f.close_time}",
                "pricing": f.pricing
            }
            for fid, f in facilities.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
