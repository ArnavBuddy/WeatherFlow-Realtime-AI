from app.services.db_service import get_session_events, update_session_summary
from app.services.llm_service import llm_service
import asyncio

async def process_session_summary(session_id: str, duration: int):
    """
    Background task to analyze session history and generate a summary.
    """
    print(f"Starting background processing for session {session_id}")
    
    # 1. Fetch events
    events = await get_session_events(session_id)
    if not events:
        print(f"No events found for session {session_id}")
        return

    # 2. Format history for LLM
    # events is a list of dicts (from Supabase response)
    # We want a string representation
    conversation_text = ""
    for event in events:
        role = event.get('event_type', 'unknown')
        content = event.get('content', '')
        conversation_text += f"{role}: {content}\n"

    # 3. Ask LLM for summary
    prompt = f"""
    Analyze the following conversation log and provide a concise summary of the session.
    Focus on the main topics discussed and the outcome.
    
    Log:
    {conversation_text}
    
    Summary:
    """
    
    try:
        # We use a new chat or just generate content
        # model.generate_content is easier for one-off
        response = await llm_service.model.generate_content_async(prompt)
        summary = response.text
        
        # 4. Update session record
        await update_session_summary(session_id, summary, duration)
        print(f"Session {session_id} summary updated.")
        
    except Exception as e:
        print(f"Error generating summary for {session_id}: {e}")
