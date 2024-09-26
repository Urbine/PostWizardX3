import asyncio
from playwright.async_api import async_playwright, Playwright

import helpers

media_source_login = 'https://media_source.com/external.php?page=access'
username = helpers.get_client_info('client_info.json',
                                   parent=True)['MediaSource']['username']

password = helpers.get_client_info('client_info.json',
                                   parent=True)['MediaSource']['password']

zip_file = "http://example.com/zip_tool/sample/NATS_Content_SampleSet1.zip"
download_dir = f'{helpers.cwd_or_parent_path(parent=True)}/tmp'

async def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch()
    page = await browser.new_page()
    await page.goto(media_source_login)
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