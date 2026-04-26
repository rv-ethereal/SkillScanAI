import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")
client_kwargs = {"api_key": api_key}
if api_key.startswith("AIza"):
    client_kwargs["base_url"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
    MODEL_NAME = "gemini-2.5-flash"
elif api_key.startswith("gsk_"):
    client_kwargs["base_url"] = "https://api.groq.com/openai/v1"
    MODEL_NAME = "llama-3.1-8b-instant"
else:
    MODEL_NAME = "gpt-4o-mini"

try:
    client = OpenAI(**client_kwargs)
except Exception:
    client = None

def generate_learning_roadmap(missing_skills: list[str]) -> dict:
    """
    Generates a personalized 3-week learning roadmap.
    """
    if not client:
        return {"Error": "OpenAI API Key is required to generate the roadmap."}
        
    if not missing_skills:
        return {"Week 1": {"topics": ["Maintain expertise"], "resources": ["N/A"], "time_estimate": "Ongoing"}}
        
    skills_str = ", ".join(missing_skills)
    prompt = f"""
    Create a highly personalized 3-week learning roadmap for someone needing to quickly learn these missing skills: {skills_str}.
    Provide the topics to learn, suggested free resources (e.g., official docs, YouTube, free courses), and an estimated time commitment (e.g., '10 hours/week').
    
    Return strictly as a JSON object with this exact structure:
    {{
        "Week 1": {{"topics": ["topic1", "topic2"], "resources": ["link or text"], "time_estimate": "10 hrs"}},
        "Week 2": {{"topics": ["topic3"], "resources": [], "time_estimate": "10 hrs"}},
        "Week 3": {{"topics": ["topic4"], "resources": [], "time_estimate": "10 hrs"}}
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert technical mentor creating structural learning pathways. You only output JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        return data
    except Exception as e:
        print(f"Error generating roadmap: {e}")
        return {}
