import google.generativeai as genai
import os
from app.core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

import httpx

# Define a simulated tool
async def get_weather(location: str):
    """Get the current weather for a given location."""
    try:
        print(f"DEBUG: Fetching weather for {location} via Open-Meteo...")
        async with httpx.AsyncClient() as client:
            # 1. Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
            geo_res = await client.get(geo_url, timeout=10.0)
            if geo_res.status_code != 200:
                return f"Error geocoding: {geo_res.status_code}"
            
            geo_data = geo_res.json()
            if not geo_data.get("results"):
                return f"Location '{location}' not found."
            
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            name = geo_data["results"][0]["name"]
            
            # 2. Weather
            # Fetch current temperature
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
            weather_res = await client.get(weather_url, timeout=10.0)
            
            if weather_res.status_code != 200:
                return f"Error fetching weather: {weather_res.status_code}"
                
            w_data = weather_res.json()
            temp = w_data["current"]["temperature_2m"]
            unit = w_data["current_units"]["temperature_2m"]
            
            # Simple WMO code interpretation (optional, or just return code)
            return f"Weather in {name}: {temp}{unit}"

    except Exception as e:
        error = f"Error: {str(e)}"
        print(f"DEBUG: {error}")
        return error

tools_map = {
    'get_weather': get_weather
}

class LLMService:
    def __init__(self):
        # Tools configuration
        # For GenAI SDK, we pass the function itself. 
        # CAUTION: The SDK might inspect the function signature.
        # If we pass an async function, the SDK might not handle it if we were using auto-calling.
        # But here we are using manual calling, so we just need the definition for the model schema.
        # Safety settings to allow all content (prevent false positives)
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            safety_settings=self.safety_settings,
            tools=[get_weather]
        )
    
    def start_chat(self):
        # Disable automatic function calling to allow streaming
        return self.model.start_chat(enable_automatic_function_calling=False)

    async def generate_stream(self, chat_session, message: str):
        # 1. Send message with stream=True
        # We need to handle potential FunctionCalls manually
        try:
            response = chat_session.send_message(message, stream=True)
            
            function_call_found = False
            tool_response_parts = []
            
            for chunk in response:
                # Debug logging to see what we received
                # print(f"DEBUG: Chunk received: {chunk}")
                
                if not chunk.candidates:
                     continue
                
                if not chunk.candidates[0].content.parts:
                    continue
                
                part = chunk.candidates[0].content.parts[0]
                
                if part.function_call:
                    function_call_found = True
                    fc = part.function_call
                    tool_name = fc.name
                    tool_args = dict(fc.args)
                    
                    # Execute tool
                    if tool_name in tools_map:
                        print(f"Executing tool: {tool_name} with {tool_args}")
                        
                        # Check if tool is async
                        import inspect
                        func = tools_map[tool_name]
                        if inspect.iscoroutinefunction(func):
                            result = await func(**tool_args)
                        else:
                            result = func(**tool_args)
                        
                        # Prepare response part
                        tool_response_parts.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={'result': result}
                                )
                            )
                        )
                    else:
                        print(f"Unknown tool: {tool_name}")
                        tool_response_parts.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={'error': 'Unknown tool'}
                                )
                            )
                        )
                else:
                    # Just text
                    # We already checked candidates and parts above
                    if part.text:
                        yield part.text

            # 2. If we had a function call, we need to send the result back and get the answer
            if function_call_found and tool_response_parts:
                # Send tool response
                final_response = chat_session.send_message(
                    tool_response_parts, 
                    stream=True
                )
                
                for chunk in final_response:
                    if not chunk.candidates:
                        continue
                    if not chunk.candidates[0].content.parts:
                        continue
                    part = chunk.candidates[0].content.parts[0]
                    if part.text:
                        yield part.text

        except Exception as e:
            yield f"Error: {str(e)}"
            print(f"LLM Stream Error: {e}")

llm_service = LLMService()
