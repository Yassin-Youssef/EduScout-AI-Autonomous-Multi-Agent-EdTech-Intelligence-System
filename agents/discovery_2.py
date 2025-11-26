import requests                     # download web pages
from bs4 import BeautifulSoup       # clean & parse HTML
#DOWNLOAD HTML
def fetch_website(url: str) -> str:
    # Download HTML content from a webpage
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"there was an error could not fetch {url}: {e}")
        return ""


# CLEAN HTML → TEXT
def extract_text_from_html(html: str) -> str:
    # Convert HTML into readable plain text

    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style"]):
        element.extract()

    text = soup.get_text(separator="\n")

    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)



#DISCOVERY v2

def discover_company_website(company_name: str) -> str:
    # Simple mapping for 45+ EdTech/LMS companies

    key = company_name.strip().lower()

    known_websites = {
        "canvas": "https://www.instructure.com",
        "moodle": "https://moodle.com",
        "blackboard": "https://www.anthology.com/blackboard",
        "brightspace": "https://www.d2l.com/brightspace",
        "schoology": "https://www.schoology.com",
        "google classroom": "https://classroom.google.com",
        "open edx": "https://openedx.org",
        "d2l": "https://www.d2l.com",
        "sakai": "https://www.sakailms.org",
        "neo lms": "https://www.neolms.com",
        "talentlms": "https://www.talentlms.com",
        "ispring learn": "https://www.ispringsolutions.com/ispring-learn",
        "absorb lms": "https://www.absorblms.com",
        "docebo": "https://www.docebo.com",
        "litmos": "https://www.litmos.com",
        "totara": "https://www.totaralearning.com",
        "saba": "https://www.saba.com",

        "coursera": "https://www.coursera.org",
        "udemy": "https://www.udemy.com",
        "khan academy": "https://www.khanacademy.org",
        "byjus": "https://byjus.com",
        "futurelearn": "https://www.futurelearn.com",
        "edx": "https://www.edx.org",
        "masterclass": "https://www.masterclass.com",
        "skillshare": "https://www.skillshare.com",
        "udacity": "https://www.udacity.com",

        "duolingo": "https://www.duolingo.com",
        "photomath": "https://photomath.com",
        "quizlet": "https://quizlet.com",
        "gradescope": "https://www.gradescope.com",
        "turnitin": "https://www.turnitin.com",
        "socratic": "https://socratic.org",
        "knewton": "https://www.wileyplus.com/knewton",
        "brainly": "https://brainly.com",

        "edmodo": "https://new.edmodo.com",
        "nearpod": "https://nearpod.com",
        "seesaw": "https://web.seesaw.me",
        "flipgrid": "https://info.flip.com",
        "kahoot": "https://kahoot.com",
        "epic books": "https://www.getepic.com",
        "tophat": "https://tophat.com",

        "code.org": "https://code.org",
        "scratch": "https://scratch.mit.edu",
        "brilliant": "https://brilliant.org",
        "codecademy": "https://www.codecademy.com",
    }

    if key in known_websites:
        return known_websites[key]

    cleaned_key = " ".join(key.replace(".", " ").split())
    if cleaned_key in known_websites:
        return known_websites[cleaned_key]

    return ""
