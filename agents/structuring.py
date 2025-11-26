#This is baially the decide agent 
#Takes clean website text and turns it into a structured Python dict
#using an LLM (OpenRouter or Gemini) or a mock fallback.

import os #lets python read environment
import json #converts between pythn dictionaries and json text
import requests #make http requests
from dotenv import load_dotenv # loads the evn file

#Load environment variables from .env
load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

#first function of callingt the open router
def call_openrouter_llm(prompt: str) -> str:
    #Call an LLM via OpenRouter if not working witch to mock
    if not OPENROUTER_KEY:
        print("warning  OPENROUTER_API_KEY missing now using mock LLM.")
        return call_mock_llm(prompt)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {#identify to api, setting the key, tell the model the data were going to send
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://constructor-hackathon.local",
        "X-Title": "EduScout Agent",
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }

    try:#here we send post requests, and checking if succesful, prases respone aand etract the text
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:#if anything fails we use mock
        print("[ERROR] OpenRouter call failed:", e)
        return call_mock_llm(prompt)

#Now for gemini same thing 
def call_gemini_llm(prompt: str) -> str:
    if not GEMINI_KEY:
        print("waring GEMINI_API_KEY missing now using mock LLM.")
        return call_mock_llm(prompt)

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-1.5-flash:generateContent"
    )
    #gemini uss key url not parameter
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.0},
    }

    try:
        resp = requests.post(
            url, headers=headers, params=params, json=payload, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            print("[WARN] Gemini returned no candidates → using mock.")
            return call_mock_llm(prompt)
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            print("warning Gemini candidates have no parts now using mock.")
            return call_mock_llm(prompt)
        return parts[0].get("text", "")
    except Exception as e:
        print("error Gemini API call failed:", e)
        return call_mock_llm(prompt)

#now for mock
def call_mock_llm(prompt: str) -> str:
    #Offline fallback return a fixed JSON example as text
    print("Using mock LLM output.")
    sample_output = {
        "company_name": "Canvas LMS",
        "founded": "2011",
        "headquarters": "Salt Lake City, Utah, USA",
        "summary": (
            "Canvas LMS is a widely used educational platform designed for "
            "K–12 and higher education institutions."
        ),
        "products": ["Canvas LMS", "Canvas Studio", "Canvas Catalog"],
        "target_market": ["K–12", "Higher Education"],
        "technology_stack": {
            "languages": ["Ruby", "JavaScript"],
            "frameworks": ["Ruby on Rails", "React"],
        },
        "pricing_model": "Subscription-based (institutional licensing)",
        "company_size": "1000–5000 employees",
        "key_features": [
            "Course creation",
            "Assessments",
            "Analytics",
            "Integrations",
        ],
        "use_cases": [
            "Online learning",
            "Hybrid learning",
            "Enterprise education",
        ],
        "value_proposition": (
            "Modern, scalable, cloud-based LMS with strong analytics "
            "and integrations."
        ),
        "market_position": "Industry leader",
        "competitors": ["Moodle", "Blackboard", "Google Classroom"],
        "metadata": {"source": "mock", "confidence": "low (example data)"},
    }
    return json.dumps(sample_output, indent=2)

#deciding agent now
def extract_structure(clean_text: str, detail_level: str = "standard") -> dict:
    #Turn clean website text into a structured company profile dict.
    prompt = f"""
You are an expert market-research assistant.

You receive raw text from the website of an EdTech or LMS company.
From this text, extract a structured JSON object describing the company.

Always return ONLY valid JSON, no explanations, no markdown.

Desired JSON fields:
- company_name
- founded
- headquarters
- summary
- products (list of strings)
- target_market (list of strings)
- technology_stack (object, e.g. languages, frameworks, infrastructure)
- pricing_model
- company_size
- key_features (list of strings)
- use_cases (list of strings)
- value_proposition
- market_position
- competitors (list of strings)
- metadata (object, may include sources, confidence, notes)

Detail level: {detail_level}

Here is the raw text:
--------------------------------
{clean_text}
--------------------------------

Return ONLY valid JSON. No extra text.
"""

    if PROVIDER == "gemini":
        response_text = call_gemini_llm(prompt)
    else:
        response_text = call_openrouter_llm(prompt)

    try:
        return json.loads(response_text)
    except Exception:
        print("warning Could not parse JSON from LLM. Returning raw response.")
        return {"error": "invalid_json", "raw_response": response_text}
