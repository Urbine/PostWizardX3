import asyncio
from playwright.async_api import async_playwright, Playwright

from core import helpers, MONGER_CASH_INFO

mcash_login = 'https://mongercash.com/external.php?page=access'
username = MONGER_CASH_INFO.username
password = MONGER_CASH_INFO.password

zip_file = "http://mongercash.com/zip_tool/MzAwMTc2NC4xLjE2LjQ2LjAuMTQxNjguMC4wLjA/NATS_Content_LaizaandMayaOnAsianSexDiarySet1.zip"
download_dir = f'{helpers.cwd_or_parent_path(parent=True)}/tmp'


async def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch()
    page = await browser.new_page()
    await page.goto(mcash_login)
    await page.get_by_label('user').fill(username)
    await page.get_by_label('password').fill(password)
    await page.get_by_label('head-login').click()
    async with page.expect_download() as download_info:
        await page.goto(zip_file)
    download = await download_info.value
    await download.save_as(download_dir + download.suggested_filename)
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
