import json
from pathlib import Path

# Base folders
BASE_DIR = Path(__file__).resolve().parents[1]
JSON_DIR = BASE_DIR / "profiles" / "json"
MD_DIR = BASE_DIR / "profiles" / "markdown"
KB_PATH = BASE_DIR / "knowledge_base.jsonl"

# Create folders if they don't exist
JSON_DIR.mkdir(parents=True, exist_ok=True)
MD_DIR.mkdir(parents=True, exist_ok=True)

# Helper, Always return a list 
def safe_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return [str(value)]

# Helper, Format list into markdown bullet points
def format_list_for_md(items):
    items = safe_list(items)
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)

# Helper, Create filesystem-safe filenames
def slugify(name: str) -> str:
    if not name:
        return "unknown"

    name = name.lower().strip()

    replacements = {
        "lms": "",
        ".": "",
        "'": "",
        "\"": "",
        ":": "",
        ";": "",
        ",": "",
        "!": "",
        "?": "",
        "(": "",
        ")": "",
        "/": "",
        "\\": "",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    return "_".join(name.split())

# FEATURE #1 — DATA COMPLETENESS SCORE
def calculate_completeness(structured: dict) -> float:
    # Calculates how many fields are filled out of all expected fields.
    # Includes nested fields inside technology_stack.

    # Main expected fields
    fields = [
        "company_name", "founded", "headquarters", "summary",
        "products", "target_market", "pricing_model",
        "company_size", "key_features", "use_cases",
        "value_proposition", "market_position", "competitors"
    ]

    filled = 0
    total = len(fields)

    # Count completeness for main fields
    for f in fields:
        val = structured.get(f)
        if val not in [None, "", [], {}]:
            filled += 1

    # Now include nested tech stack fields
    tech = structured.get("technology_stack") or {}
    tech_fields = ["languages", "frameworks", "infrastructure"]
    total += len(tech_fields)

    for f in tech_fields:
        val = tech.get(f)
        if val not in [None, "", [], {}]:
            filled += 1

    return round(filled / total, 2)

#FEATURE #2 — CATEGORY CLASSIFICATION
def classify_company(structured: dict) -> str:
    # Uses simple keyword matching to assign company category.

    text = json.dumps(structured).lower()

    if any(k in text for k in ["lms", "learning management", "canvas", "moodle", "blackboard"]):
        return "Learning Management System (LMS)"
    if any(k in text for k in ["k-12", "schools", "classroom", "teachers"]):
        return "K-12 Learning Platform"
    if any(k in text for k in ["assessment", "grading", "testing", "quiz"]):
        return "Assessment & Testing"
    if any(k in text for k in ["training", "corporate", "employees", "hr"]):
        return "Corporate Training / HR Learning"
    if any(k in text for k in ["coding", "programming", "developer"]):
        return "Coding Education"
    if any(k in text for k in ["language learning", "duolingo"]):
        return "Language Learning"
    if any(k in text for k in ["mooc", "open courses", "coursera", "edx"]):
        return "MOOC Platform"

    return "General EdTech"

# Markdown Generator
def generate_markdown(structured: dict) -> str:
    company_name = structured.get("company_name") or "Unknown"
    founded = structured.get("founded") or "Unknown"
    headquarters = structured.get("headquarters") or "Unknown"
    pricing_model = structured.get("pricing_model") or "Unknown"
    company_size = structured.get("company_size") or "Unknown"
    market_position = structured.get("market_position") or "Unknown"
    value_proposition = structured.get("value_proposition") or "No value proposition provided."
    summary = structured.get("summary") or "No summary available."
    completeness = structured.get("data_completeness_score") or 0.0
    category = structured.get("category") or "Unclassified"

    products = safe_list(structured.get("products"))
    target_market = safe_list(structured.get("target_market"))
    key_features = safe_list(structured.get("key_features"))
    use_cases = safe_list(structured.get("use_cases"))
    competitors = safe_list(structured.get("competitors"))

    tech = structured.get("technology_stack") or {}
    languages = safe_list(tech.get("languages"))
    frameworks = safe_list(tech.get("frameworks"))
    infrastructure = safe_list(tech.get("infrastructure"))

    # Professional wiki-style markdown
    md = (
        f"# {company_name}\n\n"
        f"**Category:** {category}  \n"
        f"**Data Completeness Score:** {completeness}  \n\n"
        "---\n\n"
        "## Key Information\n\n"
        f"| Field | Value |\n"
        f"|-------|-------|\n"
        f"| Founded | {founded} |\n"
        f"| Headquarters | {headquarters} |\n"
        f"| Pricing Model | {pricing_model} |\n"
        f"| Company Size | {company_size} |\n"
        f"| Market Position | {market_position} |\n\n"
        "## Summary\n\n"
        f"{summary}\n\n"
        "## Products\n\n"
        f"{format_list_for_md(products)}\n\n"
        "## Target Market\n\n"
        f"{format_list_for_md(target_market)}\n\n"
        "## Key Features\n\n"
        f"{format_list_for_md(key_features)}\n\n"
        "## Use Cases\n\n"
        f"{format_list_for_md(use_cases)}\n\n"
        "## Technology Stack\n\n"
        "### Languages\n"
        f"{format_list_for_md(languages)}\n\n"
        "### Frameworks\n"
        f"{format_list_for_md(frameworks)}\n\n"
        "### Infrastructure\n"
        f"{format_list_for_md(infrastructure)}\n\n"
        "## Value Proposition\n\n"
        f"{value_proposition}\n\n"
        "## Competitors\n\n"
        f"{format_list_for_md(competitors)}\n\n"
        "---\n\n"
        "*Auto-generated by EduScout AI*\n"
    )

    return md

# ACT PHASE – Save JSON, Markdown, KB
def act_save_outputs(structured: dict):

    # Add completeness score
    structured["data_completeness_score"] = calculate_completeness(structured)

    # Add category classification
    structured["category"] = classify_company(structured)

    company_name = structured.get("company_name") or "unknown_company"
    slug = slugify(company_name)
    
    # Check for updates before saving
    try:
        # Import the updater module
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).resolve().parents[1]))
        from updater import check_for_updates
        
        # Check if data changed
        has_changes = check_for_updates(slug, structured)
        if has_changes:
            print(f"[ACT]  Changes detected - updating profile")
        else:
            print(f"[ACT]  Data unchanged - saving anyway")
    except Exception as e:
        print(f"[ACT] Update check failed (continuing anyway): {e}")

    json_path = JSON_DIR / f"{slug}.json"
    md_path = MD_DIR / f"{slug}.md"

    # Save JSON
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    print(f"[ACT] Saved JSON profile → {json_path}")

    # Generate Markdown
    markdown = generate_markdown(structured)

    # Save Markdown
    with md_path.open("w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"[ACT] Saved Markdown profile → {md_path}")

    # Append to knowledge base
    with KB_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(structured, ensure_ascii=False) + "\n")
    print(f"[ACT] Appended to knowledge base → {KB_PATH}")