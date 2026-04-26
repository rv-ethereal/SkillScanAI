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
except Exception as e:
    client = None

def extract_skills(text: str, text_type: str = "resume") -> list[str]:
    """
    Extracts a list of skills from the text using LLM.
    """
    if not client:
        return []
        
    prompt = f"Extract a precise list of professional skills from the following {text_type}. Return the response strictly as a JSON object with a single key 'skills' containing a list of strings.\n\nText: {text}"
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in parsing HR documents. You only output JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        skills = data.get("skills", [])
        return [str(skill).strip() for skill in skills] # preserve casing optionally, we'll handle case in analyzer
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []

def extract_resume_skills(resume_text: str) -> list[str]:
    return extract_skills(resume_text, "resume")

def extract_jd_skills(jd_text: str) -> list[str]:
    return extract_skills(jd_text, "job description")
