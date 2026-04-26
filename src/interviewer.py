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

def get_chat_response(messages: list, missing_skills: list[str]) -> str:
    """
    Continues the conversation. 
    `messages` is a list of dicts: [{"role": "user"/"assistant", "content": "..."}]
    """
    if not client:
        return "System Error: AI client not configured."
        
    skills_context = ", ".join(missing_skills) if missing_skills else "general technical skills"
    
    system_prompt = {
        "role": "system",
        "content": f"You are a professional, direct technical interviewer for an AI Agent startup. The candidate is applying for a role but lacks direct experience in these specific areas: {skills_context}. Your goal is to ask targeted questions to see if they possess adjacent knowledge or strong problem-solving skills to learn them quickly. Ask only ONE concise question at a time. Do not break character."
    }
    
    # Gemini API requires at least one 'user' message, it fails if only 'system' is provided.
    if not messages:
        full_messages = [
            system_prompt, 
            {"role": "user", "content": "Hello, I am the candidate. I am ready for my first question."}
        ]
    else:
        full_messages = [system_prompt] + messages
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=full_messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate response due to an error: {e}"

def calculate_final_eligibility(chat_history: list, resume_score: float, required_skills: list[str]) -> dict:
    """
    Synthesizes the resume match score and the interview transcript to make a final decision.
    """
    if not client:
        return {"eligible": False, "final_score": 0.0, "feedback": "API Key missing."}

    transcript = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in chat_history])
    req_skills_str = ", ".join(required_skills)
    
    prompt = f"""
    You are the final hiring committee AI.
    The candidate's initial resume match score was {resume_score}/10.0 against these required skills: {req_skills_str}.
    
    Here is the transcript of their technical interview:
    {transcript}
    
    Based on the resume score and their performance in the interview, make a final decision on their eligibility for the role.
    Return strictly as a JSON object with:
    1. "eligible" (boolean: true or false)
    2. "final_score" (number out of 10.0, factoring in both resume and interview)
    3. "feedback" (A professional 2-3 sentence paragraph explaining the decision to the candidate)
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You output strict JSON determining a candidate's fate."},
                {"role": "user", "content": prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "eligible": bool(data.get("eligible", False)),
            "final_score": float(data.get("final_score", resume_score)),
            "feedback": str(data.get("feedback", "No feedback provided."))
        }
    except Exception as e:
        return {"eligible": False, "final_score": resume_score, "feedback": f"Error calculating decision: {e}"}
