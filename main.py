import json
import os
print(">>> OPENROUTER KEY:", os.getenv("OPENROUTER_API_KEY"))

from agents.discovery_4 import (
    discover_company_website,
    fetch_website,
    extract_text_from_html,
)

from agents.structuring import extract_structure
from agents.profile_generator import act_save_outputs
from utils import load_companies_from_file

# Helper Pretty printing dividers

def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70 + "\n")

# Single-company pipeline (Sense Decide Act)

def test_pipeline(company_name: str):
    print_section(f"PROCESSING COMPANY: {company_name.upper()}")
    # 1. SENSE Discover website
    url = discover_company_website(company_name)
    print(f"[DISCOVERY] Website:", url if url else "âŒ NOT FOUND")
    if not url:
        print(f"[SKIP] No website detected for '{company_name}'.\n")
        return
    # 2. SENSE Fetch HTML
    html = fetch_website(url)
    if not html:
        print("[ERROR] Unable to fetch HTML.\n")
        return
    print(f"[FETCH] HTML downloaded ({len(html)} characters)")
    # 3. SENSE Clean HTML readable text
    text = extract_text_from_html(html)
    print(f"[CLEAN] Extracted clean text ({len(text)} characters)")
    # Limit size sent to LLM
    snippet = text[:4000]
    # 4. DECIDE: Ask LLM to extract structure
    print("\n[DECIDE] Sending clean text to LLM...\n")
    structured = extract_structure(snippet, detail_level="standard")
    # Pretty JSON output
    print("[STRUCTURED RESULT]\n")
    print(json.dumps(structured, indent=2, ensure_ascii=False))
    # 5. ACT: Save JSON + Markdown + KB
    print("\n[ACT] Saving formatted outputs...")
    act_save_outputs(structured)
    print(f"\n[DONE] Completed processing for: {company_name}")
    print("=" * 70 + "\n")

# Batch processor for companies.txt

def run_batch_from_file(path: str = "companies.txt"):
    print_section("PHASE 4 BATCH PROCESSING STARTED")
    companies = load_companies_from_file(path)
    if not companies:
        print("[ERROR] No companies found inside companies.txt")
        return
    print(f"[INFO] Found {len(companies)} companies to process.\n")
    for i, company in enumerate(companies, start=1):
        print(f"---- ({i}/{len(companies)}) {company} ----")
        try:
            test_pipeline(company)
        except Exception as e:
            print(f"[ERROR] Unexpected failure for '{company}': {e}")
            print("[INFO] Continuing to next company...\n")
    print_section("PHASE 4 BATCH PROCESSING COMPLETED")
    print("[SUCCESS] All companies processed.\n")
# Entry point
if __name__ == "__main__":
    # Run everything from companies.txt
    run_batch_from_file("companies.txt")   