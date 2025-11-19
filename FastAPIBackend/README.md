# AI Voice Assistant Backend for Sports Facility Bookings

A production-ready FastAPI backend that powers an AI voice assistant for sports facility bookings (pickleball/badminton courts). This system uses OpenAI Realtime API for voice interactions and Google Calendar as the single source of truth for bookings.

## Features

- **WebSocket-based Realtime API**: Full bidirectional audio streaming with OpenAI Realtime API
- **Twilio/Exotel Integration**: Handles inbound call webhooks and routes to appropriate facility
- **Google Calendar Integration**: Uses Google Calendar as the only data store for bookings
- **Multi-Facility Support**: Configure multiple facilities with unique phone numbers
- **Smart Availability Checking**: Checks each court individually for conflicts
- **Slot Validation**: Enforces hourly boundaries and duration multiples
- **Function Calling**: Exposes `check_availability` and `create_booking` functions to the AI

## Architecture

```
├── main.py                     # FastAPI application entry point
├── config/
│   ├── facilities.json         # Facility configurations
│   └── settings.py             # Application settings
├── routers/
│   ├── voice.py               # Twilio/Exotel webhook endpoint
│   └── realtime.py            # OpenAI Realtime WebSocket endpoint
├── services/
│   ├── facility_service.py    # Facility management
│   ├── calendar_service.py    # Google Calendar operations
│   └── booking_service.py     # Booking logic (availability, creation)
├── utils/
│   ├── time_utils.py          # DateTime utilities
│   └── slot_utils.py          # Slot validation utilities
└── schemas/
    ├── function_call_schemas.py  # Function call schemas
    └── booking_schemas.py        # Booking data models
```

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Google Calendar ID (Required)
GOOGLE_CALENDAR_ID=your_calendar_id@gmail.com

# Server Settings
HOST=0.0.0.0
PORT=5000
DEBUG=True

# Twilio Settings (Optional)
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

### 2. Google Calendar Setup

This project uses the Replit Google Calendar integration:

1. The integration is already connected (check connection status in integrations panel)
2. Set your `GOOGLE_CALENDAR_ID` in the `.env` file
3. The integration handles OAuth authentication automatically

### 3. Configure Facilities

Edit `config/facilities.json` to add your facilities:

```json
{
  "pickle_x_mysore": {
    "facility_id": "pickle_x_mysore",
    "facility_name": "Pickle X Mysore",
    "phone_number": "+919876543210",
    "number_of_courts": 4,
    "open_time": "06:00",
    "close_time": "23:00",
    "booking_rules": {
      "minimum_duration": 60,
      "duration_multiples": 60,
      "fixed_slots": true
    },
    "pricing": {
      "weekday_per_hour": 280,
      "weekend_per_hour": 300
    },
    "rentals": {
      "racket": 100,
      "shoes": 100,
      "shuttle_sale": 380
    },
    "coaching": {
      "available": true,
      "fee": 2500,
      "timings": ["7-9 AM", "4-6 PM"],
      "age_below": 18
    }
  }
}
```

### 4. Install Dependencies

Dependencies are automatically installed via Replit's package manager.

### 5. Run the Server

```bash
python main.py
```

Or use the configured workflow (click Run button in Replit).

## API Endpoints

### Voice Webhook
**POST** `/voice/webhook`

Receives incoming calls from Twilio/Exotel, identifies facility by called number, and returns TwiML response.

**Request** (form data):
- `CallSid`: Call session ID
- `From`: Caller phone number
- `To`: Called phone number (facility number)
- `CallStatus`: Call status

**Response**: TwiML/XML

### Realtime WebSocket
**WS** `/realtime?facility_id=<id>&caller_number=<number>`

WebSocket endpoint for OpenAI Realtime API integration.

**Query Parameters**:
- `facility_id` (required): Facility identifier
- `caller_number` (optional): Caller's phone number

**Message Types**:

1. **session.created** (server → client)
```json
{
  "type": "session.created",
  "session_id": "session_xxx",
  "facility": "Pickle X Mysore",
  "system_prompt": "...",
  "functions": [...]
}
```

2. **function_call** (client → server)
```json
{
  "type": "function_call",
  "function_name": "check_availability",
  "arguments": {
    "facility_id": "pickle_x_mysore",
    "date": "2024-12-25",
    "start_time": "14:00",
    "duration_minutes": 60,
    "number_of_courts": 1
  }
}
```

3. **function_result** (server → client)
```json
{
  "type": "function_result",
  "function_name": "check_availability",
  "result": {
    "success": true,
    "available": true,
    "free_courts": [1, 2, 3, 4]
  }
}
```

### Other Endpoints

- **GET** `/` - API information
- **GET** `/health` - Health check
- **GET** `/facilities` - List all facilities
- **GET** `/voice/status` - Voice router status
- **GET** `/realtime/status` - Realtime router status

## Function Calling

The AI assistant can call two functions:

### check_availability

Check court availability for a specific time slot.

**Parameters**:
- `facility_id` (string): Facility identifier
- `date` (string): Date in YYYY-MM-DD format
- `start_time` (string): Start time in HH:MM (24-hour)
- `duration_minutes` (integer): Duration in minutes (must be multiple of 60)
- `number_of_courts` (integer): Number of courts requested

**Returns**:
```json
{
  "success": true,
  "available": true,
  "free_courts": [1, 2, 3],
  "data": {...}
}
```

### create_booking

Create a booking for specific courts.

**Parameters**:
- `facility_id` (string): Facility identifier
- `date` (string): Date in YYYY-MM-DD format
- `start_time` (string): Start time in HH:MM (24-hour)
- `duration_minutes` (integer): Duration in minutes
- `name` (string): Customer name
- `phone_number` (string): Customer phone number
- `court_numbers` (array): List of court numbers to book

**Returns**:
```json
{
  "success": true,
  "booking_id": "event_id_1,event_id_2",
  "message": "Booking confirmed!",
  "data": {...}
}
```

## Booking Rules

1. **Hourly Boundaries**: All bookings must start at hourly boundaries (06:00, 14:00, etc.)
2. **No Half-Hour Slots**: Times like 14:30 or 18:15 are NOT allowed
3. **Duration Multiples**: Duration must be in multiples of 60 minutes
4. **Operating Hours**: Bookings must be within facility operating hours
5. **Court Availability**: Each court is checked individually for conflicts

## Google Calendar Integration

### Event Format

**Title**: `Court {court_number} Booking - {Customer Name}`

**Description**:
```
Customer Name: John Doe
Phone: +919876543210
Facility: Pickle X Mysore (pickle_x_mysore)
Court Number: 1
Date: 2024-12-25
Start Time: 14:00
End Time: 16:00
Duration: 120 minutes
```

### Availability Logic

1. Query Google Calendar for events in the requested time slot
2. Check each court (1 to N) individually
3. If event title contains "Court X" and facility ID, mark court X as booked
4. Return list of free courts
5. If free courts < requested courts, booking fails

## Testing

### Test Health Endpoint
```bash
curl http://localhost:5000/health
```

### Test Facilities Endpoint
```bash
curl http://localhost:5000/facilities
```

### Test Voice Webhook
```bash
curl -X POST http://localhost:5000/voice/webhook \
  -d "CallSid=test123" \
  -d "From=+919876543210" \
  -d "To=+919876543210" \
  -d "CallStatus=ringing"
```

### Test WebSocket (using wscat)
```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c "ws://localhost:5000/realtime?facility_id=pickle_x_mysore"

# Send a message
{"type": "ping"}
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure proper CORS origins in `main.py`
3. Use production ASGI server (Uvicorn with workers)
4. Set up proper logging and monitoring
5. Configure Twilio/Exotel webhook URLs to point to your server
6. Ensure Google Calendar integration is properly authenticated

## Troubleshooting

### Facilities Not Loading
- Check `config/facilities.json` exists and is valid JSON
- Check server logs for errors during startup

### Google Calendar Errors
- Verify `GOOGLE_CALENDAR_ID` is set correctly
- Check Google Calendar integration is connected in Replit
- Ensure calendar exists and is accessible

### WebSocket Connection Fails
- Check facility_id parameter is valid
- Check server logs for errors
- Verify WebSocket endpoint is accessible

## License

This project is a production-ready template for sports facility booking systems.
