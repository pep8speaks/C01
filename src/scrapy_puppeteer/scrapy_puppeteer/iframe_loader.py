"""This module contains the code responsible for loading the content of an iframe"""

import asyncio
import time

from pyppeteer import launch
from bs4 import BeautifulSoup

from .chromium_downloader import chromium_executable


def content_empty(content: str) -> bool:
    """Check if iframe content is empty

    Args:
        content (str) - Content of iframe

    Returns:
        Returns True if content of iframe is empty, False otherwise.
    """

    soup = BeautifulSoup(content, 'html.parser')

    title = soup.find('title').getText().replace('\n', '')
    content = soup.getText().replace('\n', '')

    return (len(content) - len(title)) == 0


async def async_iframe_loader(url: str, xpath: str, max_attempts: int = 5) -> str:
    """ Method responsible for extracting the content of an iframe from a website with the `url` passed from `xpath`.

    Args:
        url (str) - Address of the site that has the iframe
        xpath (str) - The iframe XPATH
        max_attempts (int) - Maximum attempts to get iframe content (default 5) 

    Returns:
        Returns the content of the iframe in XPATH at the URL site
    """
    wait_time = 1.5

    browser = await launch({'handleSIGINT': False,
                            'handleSIGTERM': False,
                            'handleSIGHUP': False,
                            'LOG_LEVEL': 'INFO',
                            'executablePath': chromium_executable(),
                            'headless': True})

    page = await browser.newPage()

    await page.goto(url)
    await page.waitForXPath(xpath)

    el_handlers = await page.xpath(xpath)
    iframe = await el_handlers[0].contentFrame()

    attempt = 1
    error = None
    while attempt <= max_attempts:
        try:

            time.sleep(wait_time * attempt)

            # Extract the content inside the iframe
            content = await iframe.evaluate('''
                () => {
                    const el = document.querySelector("*");
                    return el.innerHTML;
                }
            ''')

            if content_empty(content):
                attempt += 1

            else:
                break

        except Exception as e:
            attempt += 1
            error = e

    await browser.close()

    if attempt == max_attempts:
        raise error

    return content


def iframe_loader(url: str, xpath: str) -> str:
    """wrapper for the asynchronous method of retrieving iframe content

    Args:
        url (str) - Address of the site that has the iframe
        xpath (str) - The iframe XPATH

    Returns:
        Returns the content of the iframe in XPATH at the URL site
    """

    try:
        loop = asyncio.get_event_loop()

    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop = asyncio.get_event_loop()
    coroutine = async_iframe_loader(url, xpath)
    content = loop.run_until_complete(coroutine)
    return content
