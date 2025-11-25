import os
import sys
import json
import requests
from typing import Optional
from bs4 import BeautifulSoup


# Basic configuration
TARGET_URL = "https://itecfurg.org/?page_id=2695"
DB_FILE = "seen_opportunities.json"

# Keywords to filter
KEYWORDS = ["iniciação científica", "ic", "cientifica", "iniciacao"]

def load_db() -> Optional[list]:
    """
    Load the database of seen opportunities from disk.

    Returns:
        list: List of seen opportunity links, or None if not found or invalid.
    """
    if not os.path.exists(DB_FILE):
        return None
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def save_db(opportunities: list) -> None:
    """
    Save the list of seen opportunities to database.

    Args:
        opportunities (list): List of opportunity links.
    """
    with open(DB_FILE, "w") as f:
        json.dump(opportunities, f, indent=2)

def has_keyword(text: str) -> bool:
    """
    Check if any keyword is present in the given text.

    Args:
        text (str): Text to search for keywords.

    Returns:
        bool: True if any keyword is found, False otherwise.
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

def create_issue(title: str, link: str) -> None:
    """
    Create a GitHub issue for a new opportunity.

    Args:
        title (str): Title of the opportunity.
        link (str): URL of the opportunity.
    """
    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")

    if not repo or not token:
        print("ERROR: GitHub environment variables not found.")
        return

    api_url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    body = {
        "title": f"Nova Vaga IC: {title}",
        "body": (
            f"### Oportunidade de Iniciação Científica Encontrada!\n\n"
            f"**Título:** {title}\n"
            f"**Link:** {link}\n\n"
        )
    }
    
    resp = requests.post(api_url, json=body, headers=headers)
    if resp.status_code == 201:
        print(f"Created Issue: {title}")
    else:
        print(f"❌ Error creating issue: {resp.status_code} - {resp.text}")

def main():
    """
    Crawls the iTec website for new IC opportunities, updates the local database, and creates issues for new findings.
    - Loads previously seen opportunities from the database.
    - Fetches the target webpage and parses its content.
    - Extracts all links from the page and filters them based on keywords.
    - Detects new opportunities and creates issues for them (unless it's the first execution).
    - Updates the database with any new links found.
    """
    print("Crawling iTec website...")
    
    # Load history
    seen_opportunities = load_db()
    first_exec = False
    
    if seen_opportunities is None:
        print("Database file not found. Starting first executing (populating without notifying)...")
        seen_opportunities = []
        first_exec = True
    
    # Get soup
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error accessing Itec's website: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract links
    content = soup.find("div", class_="entry-content")
    if not content:
        content = soup

    found_links = content.find_all("a")
    
    new_opportunities = []
    actual_links = []

    print(f"Total links on page: {len(found_links)}")

    for tag in found_links:
        text = tag.get_text(strip=True)
        href = tag.get('href')

        if not text or not href:
            continue
            
        # Normalizes link
        if href.startswith("/"):
            href = "https://itecfurg.org" + href

        actual_links.append(href)

        # Detection filter (Is new? Is within keywords?)
        if href not in seen_opportunities:
            if has_keyword(text):
                # Only generates issues if it's not the first execution
                if not first_exec:
                    print(f"New IC opportunity: {text}")
                    create_issue(text, href)
                else:
                    print(f"Adding to initial history): {text}")

                new_opportunities.append(href)
            else:
                pass 
    
    # Update DB with new links
    updated_db = list(set(seen_opportunities + actual_links))
    
    if len(updated_db) > len(seen_opportunities):
        save_db(updated_db)
        print(f"Database updated with {len(updated_db) - len(seen_opportunities)} new links.")
    else:
        print("Nothing new.")

if __name__ == "__main__":
    main()