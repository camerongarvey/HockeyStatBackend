# playwright_extract_table.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_tables(url: str):
    """Open a URL and extract all <table> elements as BeautifulSoup objects."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Get the full page HTML
        html_content = page.content()
        browser.close()

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract all <table> elements
    tables = soup.find_all("tbody")

    print(f"✅ Found {len(tables)} table(s) on {url}")
    return tables  # List of BeautifulSoup <table> objects


def process_goalies(t):
    for i in t:
        soup = BeautifulSoup(str(i), "html.parser")

        titles = [div.get('title') for div in soup.find_all('div')]
        name = titles[1]
        number = soup.find('span', class_='ml-2 text-muted').text

        print(f"{name} : {number}")


def process_players(t):
    players = []
    for i in t:
        soup = BeautifulSoup(str(i), "html.parser")

        titles = [div.get('title') for div in soup.find_all('div')]
        name = titles[1]
        number = soup.find('span', class_='ml-2 text-muted').text
        players.append((name,number))

    print(players)
    return players




def run(team):
    target_url = team
    tables = extract_tables(target_url)

    # Example: process the first table
    if tables:
        if len(tables) == 2:
            return process_players(tables[0])
        elif len(tables) == 3:
            return process_players(tables[1])
