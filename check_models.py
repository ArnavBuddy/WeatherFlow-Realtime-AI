import google.generativeai as genai
import os
from app.core.config import settings
import time

genai.configure(api_key=settings.GEMINI_API_KEY)

def check_models():
    candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash"
    ]
    
    print("Checking specific candidates for availability...")
    for model_name in candidates:
        print(f"Testing {model_name}...", end=" ")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi", request_options={"timeout": 5})
            if response.text:
                print("SUCCESS! (Working)")
                return model_name
        except Exception as e:
            if "429" in str(e):
                print("FAILED (Quota Exceeded)")
            elif "404" in str(e):
                print("FAILED (Not Found)")
            else:
                print(f"FAILED ({str(e)[:50]}...)")
    return None

if __name__ == "__main__":
    working = check_models()
    if working:
        print(f"\nFOUND WORKING MODEL: {working}")
    else:
        print("\nNO WORKING MODELS FOUND.")
