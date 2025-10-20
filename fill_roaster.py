# playwright_extract_table.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_tables(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        html_content = page.content()
        browser.close()

    soup = BeautifulSoup(html_content, "html.parser")

    tables = soup.find_all("tbody")

    return tables


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
    return players




def run(team):
    target_url = team
    tables = extract_tables(target_url)

    if tables:
        if len(tables) == 2:
            return process_players(tables[0])
        elif len(tables) == 3:
            return process_players(tables[1])
