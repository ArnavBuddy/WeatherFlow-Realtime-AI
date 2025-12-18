import google.generativeai as genai
import os
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def test_models():
    print("Fetching available models...")
    try:
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        print(f"Error listing models: {e}")
        return

    print(f"Found {len(models)} candidate models. Testing availability...")
    
    working_model = None

    # prioritize flash and pro models
    sorted_models = sorted(models, key=lambda x: 'flash' not in x.name)

    for m in sorted_models:
        model_name = m.name.replace('models/', '')
        print(f"Testing {model_name}...", end=" ")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello", request_options={"timeout": 10})
            if response.text:
                print("SUCCESS!")
                working_model = model_name
                break
        except Exception as e:
            print(f"FAILED ({str(e)[:100]}...)")
            
    if working_model:
        print(f"\nRecommended Model: {working_model}")
        print(f"Please update llm_service.py to use: '{working_model}'")
    else:
        print("\nNo working models found. You may have exhausted all quotas.")

if __name__ == "__main__":
    test_models()
