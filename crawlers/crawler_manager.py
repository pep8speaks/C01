import json
import time
import random
from multiprocessing import Process
import os
import sys
import shutil
from lxml.html.clean import Cleaner
import codecs

import scrapy
from scrapy.crawler import CrawlerProcess

from crawlers.constants import *

# from .crawlers.static_page import StaticPageSpider
# from .crawlers.static_page import StaticPageSpider
# from .crawlers.static_page import StaticPageSpider
from crawlers.static_page import StaticPageSpider

import crawling_utils.crawling_utils as crawling_utils

import requests

# TODO: implement following antiblock options
# antiblock_mask_type
# antiblock_ip_rotation_type
# antiblock_proxy_list
# antiblock_max_reqs_per_ip
# antiblock_max_reuse_rounds
# antiblock_reqs_per_user_agent
# antiblock_user_agents_file
# antiblock_cookies_file
# antiblock_persist_cookies


def create_folders(output_path):
    """Create essential folders for crawlers if they do not exists"""
    files = [
        f"{output_path}",
        f"{output_path}/config",
        f"{output_path}/data",
        f"{output_path}/flags",
        f"{output_path}/log",
        f"{output_path}/webdriver",
    ]
    for f in files:
        try:
            os.mkdir(f)
        except FileExistsError:
            pass


def get_crawler_base_settings(config):
    """Returns scrapy base configurations."""
    autothrottle = "antiblock_autothrottle_"
    return {
        "BOT_NAME": "crawlers",
        "ROBOTSTXT_OBEY": config['obey_robots'],
        "DOWNLOAD_DELAY": 1,
        # "SELENIUM_DRIVER_NAME": "chrome",
        # "SELENIUM_DRIVER_EXECUTABLE_PATH": shutil.which(
        #     crawling_utils.CHROME_WEBDRIVER_PATH
        # ),
        # "SELENIUM_DRIVER_ARGUMENTS": ["--headless"],
        # "DOWNLOADER_MIDDLEWARES": {"scrapy_selenium.SeleniumMiddleware": 0},
        "DOWNLOAD_DELAY": config["antiblock_download_delay"],
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": config[f"{autothrottle}enabled"],
        "AUTOTHROTTLE_START_DELAY": config[f"{autothrottle}start_delay"],
        "AUTOTHROTTLE_MAX_DELAY": config[f"{autothrottle}max_delay"],
    }


def crawler_process(crawler_id, config):
    """Starts crawling."""

    output_path = config["output_path"]

    # Redirects process logs to files
    sys.stdout = open(f"{output_path}/log/{crawler_id}.out", "a", buffering=1)
    sys.stderr = open(f"{output_path}/log/{crawler_id}.err", "a", buffering=1)

    process = CrawlerProcess(settings=get_crawler_base_settings(config))

    if config["crawler_type"] == "single_file":
        # process.crawl(StaticPageSpider, crawler_id=crawler_id)
        raise NotImplementedError
    elif config["crawler_type"] == "file_bundle":
        # process.crawl(StaticPageSpider, crawler_id=crawler_id)
        raise NotImplementedError
    elif config["crawler_type"] == "deep_crawler":
        # process.crawl(StaticPageSpider, crawler_id=crawler_id)
        raise NotImplementedError
    elif config["crawler_type"] == "static_page":
        process.crawl(StaticPageSpider, crawler_id=crawler_id, output_path=output_path)

    def update_database():
        # TODO: get port as variable
        port = 8000
        requests.get(f'http://localhost:{port}/detail/stop_crawl/{config["id"]}')

    for crawler in process.crawlers:
        crawler.signals.connect(
            update_database, signal=scrapy.signals.spider_closed)

    process.start()


def gen_key():
    """Generates a unique key based on time and a random seed."""
    return str(int(time.time() * 100)) + str((int(random.random() * 1000)))


def start_crawler(config):
    """Create and starts a crawler as a new process."""

    output_path = config["output_path"]
    create_folders(output_path=output_path)

    crawler_id = gen_key()
    print(os.getcwd())


    with open(f"{output_path}/config/{crawler_id}.json", "w+") as f:
        f.write(json.dumps(config, indent=2))

    with open(f"{output_path}/flags/{crawler_id}.json", "w+") as f:
        f.write(json.dumps({"stop": False}))

    # starts new process
    p = Process(target=crawler_process, args=(crawler_id, config))
    p.start()

    return crawler_id



def stop_crawler(crawler_id, config):
    """Sets the flags of a crawler to stop."""
    output_path = config["output_path"]
    with open(f"{output_path}/flags/{crawler_id}.json", "w+") as f:
        f.write(json.dumps({"stop": True}))


def remove_crawler(crawler_id, are_you_sure=False):
    """
    CAUTION: Delete ALL files and folders created by a crawler run.
    This includes all data stored under
    {CURR_FOLDER_FROM_ROOT}/data/{crawler_id}.
    Save data before deleting.
    """

    if are_you_sure is False:
        msg = "ERROR: Delete ALL files and folders created by a crawler run." \
            f" This includes all data stored under {CURR_FOLDER_FROM_ROOT}/" \
            "data/{crawler_id}. Save data before deleting. "
        raise Exception(msg)

    files = [
        f"{CURR_FOLDER_FROM_ROOT}/config/{crawler_id}.json",
        f"{CURR_FOLDER_FROM_ROOT}/flags/{crawler_id}.json",
        f"{CURR_FOLDER_FROM_ROOT}/log/{crawler_id}.out",
        f"{CURR_FOLDER_FROM_ROOT}/log/{crawler_id}.err",
    ]
    for f in files:
        try:
            os.remove(f)
        except FileNotFoundError:
            pass

    folders = [
        f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}",
    ]
    for f in folders:
        try:
            shutil.rmtree(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))

