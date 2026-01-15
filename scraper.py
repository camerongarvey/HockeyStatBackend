import asyncio
import os
import re
import time

from playwright.async_api import async_playwright

MAX_CONCURRENT_TASKS = 20


async def block_assets(route):
    if route.request.resource_type in ["image", "stylesheet", "font"]:
        await route.abort()
    else:
        await route.continue_()


async def scrape_game(context, url, row_index, league_output_folder, complete_output_folder, schedule_type):
    page = await context.new_page()
    try:
        await page.goto(url, wait_until='domcontentloaded')

        if schedule_type:
            dropdown = page.locator("text=Regular Season")
            await dropdown.click()

            menu_item = page.locator(f"text={schedule_type}")
            if await menu_item.count() == 0:
                print(f"[Warning] Schedule '{schedule_type}' not found, defaulting to Regular Season")
            else:
                await menu_item.first.click(force=True)
                await page.wait_for_timeout(1500)

        await page.locator("button:has-text('Show all games')").click()
        await page.wait_for_timeout(1500)

        row = page.locator("tr.gamelist-row.approved").nth(row_index)
        await row.scroll_into_view_if_needed()
        box = await row.bounding_box()
        if not box:
            raise Exception("Row bounding box not found")

        await page.mouse.click(box["x"] + 10, box["y"] + 10)

        modal_selector = "div.ReactModal__Content"
        content_ready_selector = "div.boxscore-modal table"

        await page.wait_for_selector(modal_selector, timeout=5000)
        await page.wait_for_selector(content_ready_selector, timeout=5000)

        modal = page.locator(modal_selector)
        modal_html = await modal.inner_html()

        heading = await modal.locator("h2.text-uppercase.m-3").text_content()
        match = re.search(r'Game\s+(\w+-\d+)', heading or "")
        game_id = match.group(1) if match else f"game_{row_index + 1}"

        filepath = os.path.join(complete_output_folder, f"{game_id}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modal_html)

        if "Regular Season" in schedule_type:
            filepath = os.path.join(league_output_folder, f"{game_id}.html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(modal_html)

    except Exception as e:
        print(f"[Row {row_index}] Error: {e}")
    finally:
        await page.close()


async def download_game_modals_optimized(url, league_output_folder, complete_output_folder, schedule_type=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.route("**/*", block_assets)

        page = await context.new_page()
        await page.goto(url, wait_until='domcontentloaded')

        if schedule_type:
            dropdown = page.locator("text=Regular Season")
            await dropdown.click()

            menu_item = page.locator(f"text={schedule_type}")
            if await menu_item.count() == 0:
                print(f"[Warning] Schedule '{schedule_type}' not found, defaulting to Regular Season")
            else:
                await menu_item.first.click(force=True)
                await page.wait_for_timeout(1500)  # wait for games to load

        await page.locator("button:has-text('Show all games')").click()
        await page.wait_for_timeout(1500)

        rows = page.locator("tr.gamelist-row.approved")
        row_count = await rows.count()

        sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

        async def bounded_scrape(i):
            async with sem:
                await scrape_game(context, url, i, league_output_folder, complete_output_folder, schedule_type)

        tasks = [bounded_scrape(i) for i in range(row_count)]
        await asyncio.gather(*tasks)

        await context.close()
        await browser.close()


async def find_schedules(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.route("**/*", block_assets)

        page = await context.new_page()
        await page.goto(url, wait_until='domcontentloaded')

        dropdown = page.locator("text=Regular Season")
        await dropdown.click()

        menu_item = page.locator(f"text=VIAHA")

        leagues = await menu_item.all_text_contents()
        del leagues[0] #first item is duplicate
        return leagues



def run(url, output, schedule_type=None):
    leagues = asyncio.run(find_schedules(url))
    print(leagues)

    league_output_folder = "data/" + "league/" + str(output)
    os.makedirs(league_output_folder, exist_ok=True)
    for file in os.listdir(league_output_folder):
        os.remove(os.path.join(league_output_folder, file))

    complete_output_folder = "data/" + "complete/" + str(output)
    os.makedirs(complete_output_folder, exist_ok=True)
    for file in os.listdir(complete_output_folder):
        os.remove(os.path.join(complete_output_folder, file))

    for league in leagues:
        asyncio.run(download_game_modals_optimized(url, league_output_folder, complete_output_folder, schedule_type=league))
