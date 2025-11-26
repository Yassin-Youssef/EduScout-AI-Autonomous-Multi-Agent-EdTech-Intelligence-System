# Discovery Agent V4 —thefinal tuned version
# - Uses an LLM (via OpenRouter) to find the official website for a company
# - Does NOT hardcode any URLs (the AI must discover them)
# - Validates the URL by doing a real HTTP request with browser-like headers
# - Fetches HTML and cleans it into plain text for later LLM processing

import os # to read environment variables, API key
import re # to search for URLs in text using regex
import requests # to send HTTP requests
from bs4 import BeautifulSoup  # to clean HTML into readable text

# Global headers so we look like a real browser this basicallyhelps avoid 403 forbidden
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def llm_search(prompt: str) -> str:
    # Reads the OpenRouter API key from the environment
    api_key = os.getenv("OPENROUTER_API_KEY")

    # If there is no key, it cannot call the LLM
    if not api_key:
        print("OPENROUTER_API_KEY missing")
        return ""

    # OpenRouter chat completions endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"

    # HTTP headers and auth + JSON
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Body which model to use + our prompt as a single user message
    data = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    # Send the POST request and return the text of the first choice
    try:
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        out = response.json()
        return out["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"error the LLM search failed: {e}")
        return ""


def extract_url_from_text(text: str) -> str:
    # Regex that matches http:// or https:// followed by non-space characters
    pattern = r"https?://[^\s]+"

    # Find all URL-like substrings in the text
    matches = re.findall(pattern, text)

    # If there are no matches at all, return empty string
    if not matches:
        return ""

    # Take the first URL candidate
    url = matches[0]

    # Strip whitespace around it
    url = url.strip()

    # Remove common trailing punctuation that may be attached by the model
    url = url.rstrip(".,!?)\"]}'<>")

    return url


def validate_url(url: str) -> bool:
    # Empty string is automatically invalid
    if not url:
        return False

    # A valid URL should start with http:// or https://
    if not (url.startswith("http://") or url.startswith("https://")):
        return False

    # First try a HEAD request (lightweight)
    try:
        head_resp = requests.head(
            url,
            headers=DEFAULT_HEADERS,
            allow_redirects=True,
            timeout=8,
        )

        # Some servers do not support HEAD correctly; if 405/403 we can try GET
        if head_resp.status_code == 405 or head_resp.status_code == 403:
            raise Exception(f"HEAD not allowed: {head_resp.status_code}")

        # If status code < 400, consider it valid
        return head_resp.status_code < 400
    except Exception:
        # If HEAD fails, fall back to GET
        try:
            get_resp = requests.get(
                url,
                headers=DEFAULT_HEADERS,
                allow_redirects=True,
                timeout=12,
            )
            return get_resp.status_code < 400
        except Exception as e:
            print(f"[DISCOVERY V4] URL validation failed for {url}: {e}")
            return False


def discover_company_website(company_name: str) -> str:
    # Log which company we are working on
    print(f"[DISCOVERY V4] Searching for website of: {company_name}")

    # Two prompts for two attempts (slightly different wording)
    prompts = [
        (
            f"Give ONLY the official website URL for the company "
            f"'{company_name}'. No explanation, no extra text. Just one URL."
        ),
        (
            f"What is the official homepage URL of the company "
            f"'{company_name}'? Answer with a single http:// or https:// URL "
            f"and nothing else."
        ),
    ]

    # Try each prompt once
    for attempt_index, prompt in enumerate(prompts, start=1):
        # Ask the LLM for the website
        llm_output = llm_search(prompt)

        # If the LLM returned nothing, try the next prompt
        if not llm_output:
            print(f"[DISCOVERY V4] Empty LLM response on attempt {attempt_index}.")
            continue

        # Try to extract a URL from the LLM text
        url = extract_url_from_text(llm_output)

        # If we did not find any URL pattern, log and continue
        if not url:
            print("[DISCOVERY V4] No URL detected in AI response.")
            continue

        # Check if the URL actually works (not 404, etc.)
        if validate_url(url):
            print(f"[DISCOVERY V4] ✔ Valid website: {url}")
            return url
        else:
            print(f"[DISCOVERY V4] ⚠ URL seems invalid: {url}")

    # If both attempts failed, report that no usable URL was found
    print("[DISCOVERY V4] No valid URL found.")
    return ""


def fetch_website(url: str) -> str:
    # Download HTML content for the given URL
    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return ""


def extract_text_from_html(html: str) -> str:
    # Parse the HTML into a BeautifulSoup tree
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style tags because they contain code rather than content
    for tag in soup(["script", "style"]):
        tag.extract()

    # Extract visible text with line breaks
    raw_text = soup.get_text(separator="\n")

    # Split into lines, strip spaces, and remove empty lines
    lines = [line.strip() for line in raw_text.splitlines()]
    non_empty_lines = [line for line in lines if line]

    # Join back with newline so the text is compact and readable
    cleaned_text = "\n".join(non_empty_lines)

    return cleaned_text
