from crawlers.page_spider import PageSpider
from crawlers.crawler_manager import *
import json

with open("teste/config.json", "r") as file:
    config = json.loads(file.read())

config["id"] = config["crawler_id"]

crawler_process(config)
print("lero")