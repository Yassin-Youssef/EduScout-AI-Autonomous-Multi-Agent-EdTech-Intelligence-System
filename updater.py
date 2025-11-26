import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
JSON_DIR = BASE_DIR / "profiles" / "json"
CHANGES_LOG = BASE_DIR / "changes.log"


def load_existing_profile(company_slug: str) -> Dict:
    # Load existing JSON profile if it exists
    # INPUT: "instructure"
    # OUTPUT: existing JSON data or None if doesn't exist
    
    json_path = JSON_DIR / f"{company_slug}.json"
    
    if not json_path.exists():
        return None
    
    try:
        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load existing profile: {e}")
        return None


def detect_changes(old_data: Dict, new_data: Dict) -> List[Dict]:
    # Compare old vs new data and detect what changed
    
    changes = []
    
    # Fields to monitor for changes
    monitored_fields = [
        "founded", "headquarters", "summary", "products", 
        "target_market", "pricing_model", "company_size",
        "key_features", "use_cases", "value_proposition",
        "market_position", "competitors", "technology_stack"
    ]
    
    for field in monitored_fields:
        old_value = old_data.get(field)
        new_value = new_data.get(field)
        
        # Convert to JSON strings for comparison (handles lists/dicts)
        old_str = json.dumps(old_value, sort_keys=True)
        new_str = json.dumps(new_value, sort_keys=True)
        
        if old_str != new_str:
            changes.append({
                "field": field,
                "old": old_value,
                "new": new_value
            })
    
    return changes


def log_changes(company_name: str, changes: List[Dict]):
    # Write changes to log file with timestamp
    
    if not changes:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with CHANGES_LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"[{timestamp}] CHANGES DETECTED: {company_name}\n")
        f.write(f"{'='*70}\n")
        
        for change in changes:
            f.write(f"\nField: {change['field']}\n")
            f.write(f"  OLD: {change['old']}\n")
            f.write(f"  NEW: {change['new']}\n")
        
        f.write(f"\n")
    
    print(f"[UPDATE] Logged {len(changes)} changes for {company_name}")


def check_for_updates(company_slug: str, new_data: Dict) -> bool:
    # Main update checker function
    # Returns True if changes were detected, False if no changes
    
    # Load existing profile
    old_data = load_existing_profile(company_slug)
    
    # If no existing profile, this is a new entry
    if old_data is None:
        print(f"[UPDATE] New company profile created: {company_slug}")
        return False
    
    # Detect changes
    changes = detect_changes(old_data, new_data)
    
    if changes:
        company_name = new_data.get("company_name", company_slug)
        log_changes(company_name, changes)
        print(f"[UPDATE] {len(changes)} changes detected!")
        return True
    else:
        print(f"[UPDATE]  No changes detected (data is up-to-date)")
        return False

def scheduled_update():
    # This function could be called by a scheduler (cron, schedule library, etc.)
    # For now, it's just a placeholder showing how it would work
    
    from utils import load_companies_from_file
    from agents.discovery_4 import discover_company_website, fetch_website, extract_text_from_html
    from agents.structuring import extract_structure
    
    print("\n[SCHEDULER] Starting scheduled update check...")
    
    companies = load_companies_from_file("companies.txt")
    changes_detected = 0
    
    for company in companies[:5]:  # Process first 5 for demo
        print(f"\n[SCHEDULER] Checking: {company}")
        
        # Re-run discovery and structuring
        url = discover_company_website(company)
        if not url:
            continue
        
        html = fetch_website(url)
        if not html:
            continue
        
        text = extract_text_from_html(html)
        new_data = extract_structure(text[:4000])
        
        # Check for changes
        slug = company.lower().replace(" ", "_")
        if check_for_updates(slug, new_data):
            changes_detected += 1
    
    print(f"\n[SCHEDULER] Update check complete. {changes_detected} companies changed.")
