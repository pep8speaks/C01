import json

import sys
sys.path.append("../../../")

from pyppeteer import launch

from step_crawler import code_generator as code_g
from step_crawler import functions_file
from step_crawler.functions_file import *




async def main():
    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.goto('http://www.in.gov.br/web/guest/inicio')

    steps = __import__('steps')
    await steps.execute_steps(page=page)

    await browser.close()
    return


with open('recipe.json') as file:
    recipe = json.load(file)

with open('steps.py', 'w+') as file:
    file.write(code_g.generate_code(recipe, functions_file))

asyncio.get_event_loop().run_until_complete(main())
