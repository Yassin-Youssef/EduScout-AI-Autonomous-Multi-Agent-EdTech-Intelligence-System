# Discovery Agent V3 — AI-powered website finder
# This agent uses an LLM (Gemini via OpenRouter) to automatically find
# the official website for any company name.

import os                 # lets Python access environment variables (API keys)
import re                 # lets us search text using regular expressions
import requests           # used to send HTTP requests (GET / POST)
from bs4 import BeautifulSoup  # used to clean HTML into readable text

# LLM CLIENT — sends questions to OpenRouter

def llm_search(prompt: str) -> str:
    # Reads your OpenRouter API key from the OS environment.
    api_key = os.getenv("OPENROUTER_API_KEY")
    # If no API key is found, we warn and return empty text.
    if not api_key:
        print("[WARN] OPENROUTER_API_KEY missing")
        return ""

    # This is the API endpoint for OpenRouter chat models.
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Required headers for authentication and JSON format.
    headers = {
        "Authorization": f"Bearer {api_key}",  # attach your API key
        "Content-Type": "application/json"
    }

    # Data we send to the API: choose model + send our text prompt.
    data = {
        "model": "google/gemini-2.0-flash-001",  # fast Gemini model
        "messages": [{"role": "user", "content": prompt}]
    }

    # Try sending the request; if it fails, return empty string.
    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        response.raise_for_status()  # checks for errors
        out = response.json()        # convert reply into JSON
        return out["choices"][0]["message"]["content"]  # return text answer
    except Exception as e:
        print(f"[ERROR] LLM search failed: {e}")
        return ""

# URL EXTRACTOR — finds the first URL in text

def extract_url_from_text(text: str) -> str:
    # This pattern finds any http:// or https:// URL.
    pattern = r"https?://[^\s]+"
    matches = re.findall(pattern, text)  # returns all URLs found

    # If no URL found, return empty.
    if not matches:
        return ""

    # Take first URL.
    url = matches[0].strip()

    # Clean punctuation so the URL is valid.
    url = url.rstrip(".,!?)\"]}")

    return url

# URL VALIDATOR — verifies URL actually works
def validate_url(url: str) -> bool:
    # If empty → invalid.
    if not url:
        return False

    # Try a HEAD request (faster than GET).
    try:
        response = requests.head(url, timeout=8)
        # If status code < 400 → success.
        return response.status_code < 400
    except:
        return False

# MAIN LLM DISCOVERY — gets official company URL

def discover_company_website(company_name: str) -> str:
    # Print what we are searching for.
    print(f"[LLM-DISCOVERY] Searching for: {company_name}")

    # The prompt instructs the AI to output ONLY a website URL.
    prompt = (
        f"Give ONLY the official website URL for the company '{company_name}'. "
        "No explanations. No extra text. Only the URL."
    )

    # Ask the LLM.
    llm_output = llm_search(prompt)

    # If nothing returned, stop.
    if not llm_output:
        print("[LLM-DISCOVERY] No output from LLM.")
        return ""

    # Extract URL from the text.
    url = extract_url_from_text(llm_output)

    # If no URL present, stop.
    if not url:
        print("[LLM-DISCOVERY] No URL found in LLM response.")
        return ""

    # Validate URL to ensure it's a real website.
    if validate_url(url):
        print(f"[LLM-DISCOVERY] ✔ Valid URL: {url}")
        return url

    # Otherwise it's not a good URL.
    print(f"[LLM-DISCOVERY] ✖ Invalid URL: {url}")
    return ""


# HTML DOWNLOADER — fetch page contents

def fetch_website(url: str) -> str:
    # Download a webpage using HTTP GET.
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()  # check if page loaded correctly
        return res.text         # return HTML as string
    except Exception as e:
        print(f"Could not fetch {url}: {e}")
        return ""

# HTML CLEANER — convert messy HTML → clean text

def extract_text_from_html(html: str) -> str:
    # Parse HTML into a tree structure.
    soup = BeautifulSoup(html, "html.parser")

    # Remove <script> and <style> because they are code, not text.
    for tag in soup(["script", "style"]):
        tag.extract()

    # Get visible text with line breaks.
    text = soup.get_text(separator="\n")

    # Clean empty lines and spaces.
    cleaned = "\n".join(
        [line.strip() for line in text.splitlines() if line.strip()]
    )

    return cleaned
