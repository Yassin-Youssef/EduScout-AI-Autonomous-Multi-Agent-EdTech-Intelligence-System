import requests #allows python to download web pages from the urls
from bs4 import BeautifulSoup #allws python to clean html web text


def fetch_website(url: str) -> str:
    #Downloads HTML content from a URL and returns it as text.
    #This is the sense part of the agent
    try:
        response = requests.get(url, timeout=10) #this is the request download the page with time out to prevent frezing
        response.raise_for_status() #checking to see if there is an error
        return response.text #returning the html
    except Exception as e:
        print(f"there was an error could not fetch {url}: {e}") #simple error message
        return ""
    
def extract_text_from_html(html: str) -> str: 
    
    #Turns messy HTML into clean plain text.
    #Removes scripts, CSS, menus, and garbage.
    #This gives readable text for AI analysis.
    soup = BeautifulSoup(html, "html.parser") #this parses the html like a tree

    #removes Javascript and CSS because they contain useless code
    for element in soup(["script", "style"]):      
        element.extract() # Remove these elements
    text = soup.get_text(separator="\n") #getting all visible text
    #Clean empty lines and extra spaces to make the text clean and readable
    cleaned = "\n".join(
        [line.strip() for line in text.splitlines() if line.strip()]
    )

    return cleaned                                  # Return clean, readable text

def discover_company_website(company_name: str) -> str:
    
    #TEMPORARY website finder, basically returns the homepage of companies
    known = {
        "canvas": "https://www.instructure.com",# Canvas LMS official site
        "moodle": "https://moodle.org", # Moodle LMS official site
        "blackboard": "https://www.blackboard.com" # Blackboard LMS official site
    }

    return known.get(company_name.lower(), "")  # Return URL or empty string if not found
