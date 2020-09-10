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
import parsing_html

from lxml.html.clean import Cleaner
import codecs

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError

class BaseSpider(scrapy.Spider):
    name = 'base_spider'

    def __init__(self, crawler_id, output_path, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """
        print("At BaseSpider.init")
        self.crawler_id = crawler_id
        self.stop_flag = False


        self.data_folder = f"{output_path}/data/{crawler_id}"
        cofig_file_path = f"{output_path}/config/{crawler_id}.json"
        self.flag_folder = f"{output_path}/flags/"

        with open(cofig_file_path, "r") as f:
            self.config = json.loads(f.read())

        print('config output: ', self.config["output_path"])

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

        self.get_format = lambda i: str(i).split("/")[1][:-1].split(";")[0]


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
        flag_file = f"{self.flag_folder}/{self.crawler_id}.json"
        with open(flag_file) as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag


    def extract_and_store_csv(self, response, content, save_csv):
        """
        Try to extract a json/csv from response data.
        """
        file_format = self.get_format(response.headers['Content-type'])
        hsh = crawling_utils.hash(response.url)

        success = False

        output_filename = f"{self.data_folder}/csv/{hsh}"
        if save_csv and (".csv" not in output_filename):
            output_filename += ".csv"

        if b'text/html' in response.headers['Content-type']:
            try:
                parsing_html.content.html_detect_content(
                    f"{self.data_folder}/raw_pages/{hsh}.{file_format}",
                    is_string=False,
                    output_file=output_filename,
                    to_csv=save_csv
                )
                success = True

            except Exception as e:
                print(
                    f"Could not extract csv from {response.url} -",
                    f"message: {str(type(e))}-{e}"
                )
        else:
            # TODO call binary_extractor
            pass

        content["type"] = "csv"
        file_description_file = f"{self.data_folder}/csv/" \
            "file_description.jsonl"
        if success:
            with open(file_description_file, "a+") as f:
                f.write(json.dumps(content) + '\n')


    def store_raw(
            self, response, to_csv, file_format=None, binary=True, save_at="files"):
        """Save response content."""
        if file_format is None:
            file_format = self.get_format(
                response.headers['Content-type']
            )
        print(f'Saving file from {response.url}, file_format: {file_format}')

        if binary:
            file_mode = "wb"
            body = response.body
            encoding = None
        else:
            cleaner = Cleaner(
                style=True, links=False, scripts=True,
                comments=True, page_structure=False
            )

            file_mode = "w+"
            body = cleaner.clean_html(
                response.body.decode('utf-8', errors='ignore'))

        hsh = crawling_utils.hash(response.url)

        folder = f"{self.data_folder}/{save_at}"

        content = {
            "file_name": f"{hsh}.{file_format}",
            "url": response.url,
            "crawler_id": self.crawler_id,
            "type": str(response.headers['Content-type']),
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response.meta["referer"]
        }

        with open(f"{folder}/file_description.jsonl", "a+") as f:
            f.write(json.dumps(content) + '\n')

        with open(
            file=f"{folder}/{hsh}.{file_format}",
            mode=file_mode,
        ) as f:
            f.write(body)

        self.extract_and_store_csv(response, content, to_csv)

    def store_html(self, response, to_csv=False):
        """Stores html and adds its description to file_description file."""
        self.store_raw(
            response, to_csv, file_format="html", binary=False, save_at="raw_pages")
        

    def errback_httpbin(self, failure):
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
