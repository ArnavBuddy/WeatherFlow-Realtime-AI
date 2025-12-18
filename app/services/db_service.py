from datetime import datetime
from app.core.database import supabase
from app.models.schemas import EventLog

async def create_new_session(session_id: str, user_id: str | None = None) -> str:
    response = supabase.table("sessions").insert({
        "session_id": session_id,
        "user_id": user_id,
        "start_time": datetime.utcnow().isoformat()
    }).execute()
    return response.data[0]['session_id']

async def update_session_summary(session_id: str, summary: str, duration: int):
    supabase.table("sessions").update({
        "summary": summary,
        "duration_seconds": duration,
        "end_time": datetime.utcnow().isoformat()
    }).eq("session_id", session_id).execute()

async def log_event(session_id: str, event_type: str, content: str):
    supabase.table("events").insert({
        "session_id": session_id,
        "event_type": event_type,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }).execute()

async def get_session_events(session_id: str):
    response = supabase.table("events").select("*").eq("session_id", session_id).order("timestamp").execute()
    return response.data
