"""This module contains the ``PuppeteerRequest`` class"""

from scrapy import Request


class PuppeteerRequest(Request):
    """Scrapy ``Request`` subclass providing additional arguments"""

    def __init__(self, url, callback=None, screenshot=False, wait_until=None, wait_for=None, steps=None, *args, **kwargs):
        """Initialize a new Puppeteer request

        :wait_until:One of "load", "domcontentloaded", "networkidle0", "networkidle2".
            See https://miyakogi.github.io/pyppeteer/reference.html#pyppeteer.page.Page.goto
        :screenshot:If True, a screenshot of the page will be taken and the data of the screenshot
                    will be returned in the response "meta" attribute.
        :wait_for:  A selector, xpath, or function string, or timeout (milliseconds) to be waited for
        :steps:     A dict containing the steps to be executed in the page
        """

        self.wait_until = wait_until or 'domcontentloaded'
        self.wait_for = wait_for
        self.screenshot = screenshot
        self.steps = steps

        super().__init__(url, callback, *args, **kwargs)
