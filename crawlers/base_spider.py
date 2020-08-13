import scrapy
from scrapy.exceptions import CloseSpider

import requests
import logging
import os
import re
import json
import random
import datetime
import time
import crawling_utils

from crawlers.constants import *
from src.parsing.html.parsing_html_content import *


class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, crawler_id, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        print("At BaseSpider.init")
        self.crawler_id = crawler_id
        self.stop_flag = False

        self.data_folder = f"{CURR_FOLDER_FROM_ROOT}/data/{crawler_id}"

        cofig_file_path = f"{CURR_FOLDER_FROM_ROOT}/config/{crawler_id}.json"
        with open(cofig_file_path, "r") as f:
            self.config = json.loads(f.read())

        folders = [
            f"{self.data_folder}",
            f"{self.data_folder}/raw_pages",
            f"{self.data_folder}/csv",
            f"{self.data_folder}/files",
        ]
        for f in folders:
            try:
                os.mkdir(f)
            except FileExistsError:
                pass

        file = "file_description.jsonl"
        with open(f"{self.data_folder}/files/{file}", "a+") as f:
            pass        
        with open(f"{self.data_folder}/raw_pages/{file}", "a+") as f:
            pass

        self.get_file_format = lambda i: str(i).split("/")[1][:-1].split(";")[0]

    def start_requests(self):
        """
        Should be implemented by child class.
        Should yield the firsts urls to scrape.
        """
        raise NotImplementedError

    def parse(self, response):
        """
        A function to treat the responses from a request.
        Should check self.stop() at every call.
        """
        raise NotImplementedError

    def stop(self):
        """
        Checks if the crawler was signaled to stop.
        Should be called at the begining of every parse operation.
        """
        with open(f"{CURR_FOLDER_FROM_ROOT}/flags/{self.crawler_id}.json") as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def extract_and_store_csv(self, response):
        """
        Try to extract a json/csv from response data.
        """
        file_format = self.get_file_format(response.headers['Content-type'])
        hsh = crawling_utils.hash(response.url)

        html_detect_content(
            f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
            is_string=False, output_file=f"{self.data_folder}/csv/output",
        )

    def store_raw(
            self, response, file_format=None, binary=True, save_at="files"
        ):
        """Save response content."""
        if file_format is None:
            file_format = self.get_file_format(response.headers['Content-type'])
        print(f'Saving file from {response.url}, file_format: {file_format}')
        
        if binary:
            file_type = "wb"
            body = response.body
        else:
            file_type = "w+"
            body = str(response.body)

        hsh = crawling_utils.hash(response.url)
        
        folder = f"{self.data_folder}/{save_at}"
        with open(f"{folder}/{hsh}.{file_format}", file_type) as f:
            f.write(body)

        content = {
            "file_name": f"{hsh}.{file_format}",
            "url": response.url,
            "crawler_id": self.crawler_id,
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
        }

        with open(f"{folder}/file_description.jsonl", "a+") as f:
            f.write(json.dumps(content) + '\n')

    def store_html(self, response):
        """Stores html and adds its description to file_description file."""
        self.store_raw(
            response, file_format="html", binary=False, save_at="raw_pages")
