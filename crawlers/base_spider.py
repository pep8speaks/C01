# Scrapy and Twister libs
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.http import Response
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
import cchardet as chardet

# Other external libs
import datetime
import json
import itertools
import os
import re
import mimetypes
import requests
import string
import cgi

# Project libs
import crawling_utils

from crawlers.constants import *
from crawlers.file_descriptor import FileDescriptor
from crawlers.injector_tools import create_probing_object,\
    create_parameter_generators

from main.models import CrawlRequest
from crawlers.constants import AUTO_ENCODE_DETECTION_CONFIDENCE_THRESHOLD

from crawlers.port import *

PUNCTUATIONS = "[{}]".format(string.punctuation)


class BaseSpider(scrapy.Spider):
    name = 'base_spider'
    request_session = requests.sessions.Session()

    def __init__(self, config, *a, **kw):
        """
        Spider init operations.
        Create folders to store files and some config and log files.
        """

        print("At BaseSpider.init")
        self.stop_flag = False

        self.config = json.loads(config)

        self.data_folder = f"{self.config['data_path']}/data/"
        self.flag_folder = f"{self.config['data_path']}/flags/"

        folders = [
            f"{self.data_folder}",
            f"{self.data_folder}/raw_pages",
            f"{self.data_folder}/files",
            f"{self.data_folder}/screenshots",
            f"{self.data_folder}/screenshots/{self.config['instance_id']}",
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

        if bool(self.config.get("download_files_allow_extensions")):
            normalized_allowed_extensions = self.config["download_files_allow_extensions"].replace(
                " ", "")
            normalized_allowed_extensions = normalized_allowed_extensions.lower()
            self.download_allowed_extensions = set(
                normalized_allowed_extensions.split(","))

        else:
            self.download_allowed_extensions = set()

        self.preprocess_link_configs()
        self.preprocess_download_configs()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

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

    def generate_initial_requests(self):
        """
        Generates the initial requests to be done from the templated requests
        configuration. Yields the base URL if no template is used. Should be
        called by start_requests.
        """

        base_url = self.config['base_url']
        req_type = self.config['request_type']
        form_req_type = self.config['form_request_type']

        has_placeholder = "{}" in base_url
        templated_url_generator = [[None]]
        templated_url_probe = create_probing_object(base_url, req_type)

        if has_placeholder:
            # Configure the probing process
            templated_url_probe = create_probing_object(base_url, req_type,
                                                        self.config['templated_url_response_handlers']
                                                        )

            # Instantiate the parameter injectors for the URL
            url_injectors = create_parameter_generators(templated_url_probe,
                                                        self.config['templated_url_parameter_handlers']
                                                        )

            # Generate the requests
            templated_url_generator = itertools.product(*url_injectors)

        use_static_forms = self.config['static_form_parameter_handlers']
        static_form_generator = [[None]]
        static_form_probe = create_probing_object(base_url, form_req_type)

        if use_static_forms:
            # Configure the probing process
            static_form_probe = create_probing_object(base_url, form_req_type,
                                                      self.config['static_form_response_handlers']
                                                      )

            # Instantiate the parameter injectors for the forms
            static_injectors = create_parameter_generators(static_form_probe,
                                                           self.config['static_form_parameter_handlers']
                                                           )

            # Generate the requests
            static_form_generator = itertools.product(*static_injectors)

        parameter_keys = list(map(lambda x: x['parameter_key'],
                                  self.config['static_form_parameter_handlers']))
        for templated_param_combination in templated_url_generator:
            # Check if this entry hits a valid page

            is_valid = templated_url_probe.check_entry(
                url_entries=templated_param_combination
            )
            if is_valid:

                # Copy the generator (we'd need to "rewind" if we used the
                # original)
                cp_result = itertools.tee(static_form_generator)
                static_form_generator, static_form_generator_cp = cp_result

                # Iterate through the form data now
                for form_param_combination in static_form_generator_cp:

                    req_entries = dict(zip(parameter_keys,
                                           form_param_combination))

                    # Check if once again we hit a valid page
                    is_valid = static_form_probe.check_entry(
                        url_entries=templated_param_combination,
                        req_entries=req_entries
                    )

                    if is_valid:
                        # Insert parameters into URL and request body
                        curr_url = base_url\
                            .format(*templated_param_combination)

                        method = form_req_type
                        if not use_static_forms:
                            # If no form data is injected, use the regular
                            # request method set
                            method = req_type

                        yield {
                            'url': curr_url,
                            'method': method,
                            'body': req_entries
                        }

    def stop(self):
        """
        Checks if the crawler was signaled to stop.
        Should be called at the begining of every parse operation.
        """

        flag_file = f"{self.flag_folder}/{self.config['instance_id']}.json"

        with open(flag_file) as f:
            flags = json.loads(f.read())

        self.stop_flag = flags["stop"]

        if self.stop_flag:
            raise CloseSpider("Received signal to stop.")

        return self.stop_flag

    def store_html(self, response: Response):
        """Stores html and adds its description to file_description file."""
        print(f'Saving html page {response.url}')

        encoding = None
        encoding_detection_method = self.config.get(
            'encoding_detection_method', CrawlRequest.HEADER_ENCODE_DETECTION)

        if encoding_detection_method == CrawlRequest.HEADER_ENCODE_DETECTION:
            encoding = response.encoding

        elif encoding_detection_method == CrawlRequest.AUTO_ENCODE_DETECTION:
            detection = chardet.detect(response.body)

            detected_encoding = detection['encoding']
            confidence = detection['confidence']

            if confidence >= AUTO_ENCODE_DETECTION_CONFIDENCE_THRESHOLD:
                encoding = detected_encoding

            else:
                msg = f'Could not detect page encoding "{response.url}" at the level of confidence "{AUTO_ENCODE_DETECTION_CONFIDENCE_THRESHOLD}"".' + \
                    f'The predicted encoding was "{detected_encoding}" with "{confidence}" confidence. THE PAGE WILL BE SAVED AS BINARY.'
                self.logger.warn(msg)

        else:
            ValueError(
                f'"{encoding_detection_method}" is not a valid encoding detection method.')

        raw_body = response.body
        hsh = self.hash_response(response)
        relative_path = f"{self.data_folder}raw_pages/{hsh}.html"

        description = {
            "file_name": f"{hsh}.html",
            "encoding": encoding,
            "relative_path": relative_path,
            "url": response.url,
            "crawler_id": self.config["crawler_id"],
            "instance_id": self.config["instance_id"],
            "type": response.headers['Content-type'].decode(),
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": response.meta["referer"]
        }

        if encoding is None:
            description['encoding'] = 'unknown'
            description["type"] = 'binary'
            with open(file=relative_path, mode="wb") as f:
                f.write(raw_body)

        else:
            with open(file=relative_path, mode="w+", encoding=encoding, errors='ignore') as f:
                f.write(raw_body.decode(encoding))


        self.feed_file_description(
            self.data_folder + "raw_pages", description)

    # based on: https://github.com/steveeJ/python-wget/blob/master/wget.py
    def filetype_from_url(self, url: str) -> str:
        """Detects the file type through its URL"""
        extension = url.split('.')[-1]
        if 0 < len(extension) < 6:
            return extension
        return ""

    def filetype_from_filename_on_server(self, content_disposition: str) -> str:
        """Detects the file extension by its name on the server"""

        # content_disposition is a string with the following format: 'attachment; filename="filename.extension"'
        # the following operations are to extract only the extension
        extension = content_disposition.split(".")[-1]

        # removes any kind of accents
        return re.sub(PUNCTUATIONS, "", extension)

    def filetypes_from_mimetype(self, mimetype: str) -> str:
        """Detects the file type using its mimetype"""
        extensions = mimetypes.guess_all_extensions(mimetype)
        if len(extensions) > 0:
            return [ext.replace(".", "") for ext in extensions]
        return [""]

    def detect_file_extensions(self, url, content_type: str, content_disposition: str) -> list:
        """detects the file extension, using its mimetype, url or name on the server, if available"""
        extension = self.filetype_from_url(url)
        if len(extension) > 0:
            return [extension]

        extension = self.filetype_from_filename_on_server(content_disposition)
        if len(extension) > 0:
            return [extension]

        return self.filetypes_from_mimetype(content_type)

    def get_download_filename(self, url: str, extension: str) -> tuple:
        url_hash = crawling_utils.hash(url.encode())
        file_name = url_hash
        file_name += '.' + extension if extension else ''

        return file_name

    def store_large_file(self, url: str, referer: str):
        print(f"Saving large file {url}")

        # Head type request to obtain the mimetype and/or file name to be downloaded on the server
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
        response = requests.head(url, allow_redirects=True, headers=headers)

        content_type = response.headers.get("Content-type", "")
        content_disposition = response.headers.get("Content-Disposition", "")

        response.close()

        extension = self.detect_file_extensions(
            url, content_type, content_disposition)[0]

        file_name = self.get_download_filename(url, extension)
        relative_path = f"{self.data_folder}files/{file_name}"

        # The stream parameter is not to save in memory
        with requests.get(url, stream=True, allow_redirects=True, headers=headers) as req:
            with open(relative_path, "wb") as f:
                for chunk in req.iter_content(chunk_size=8192):
                    f.write(chunk)

        self.create_and_feed_file_description(
            url, file_name, referer, extension)

    def store_small_file(self, response):
        print(f"Saving small file {response.url}")

        content_type = response.headers.get("Content-Type", b"").decode()
        content_disposition = response.headers.get(
            "Content-Disposition", b"").decode()

        extension = self.detect_file_extensions(
            response.url, content_type, content_disposition)[0]

        file_name = self.get_download_filename(response.url, extension)
        relative_path = f"{self.data_folder}files/{file_name}"

        with open(relative_path, "wb") as f:
            f.write(response.body)

        self.create_and_feed_file_description(
            response.url, file_name, response.meta["referer"], extension)

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

    def feed_file_description(self, destination: str, content: dict):
        FileDescriptor.feed_description(destination, content)

    def create_and_feed_file_description(self, url: str, file_name: str, referer: str, extension: str):
        """Creates the description file of the downloaded files and saves them"""

        description = {
            "url": url,
            "file_name": file_name,
            "crawler_id": self.config["crawler_id"],
            "instance_id": self.config["instance_id"],
            "crawled_at_date": str(datetime.datetime.today()),
            "referer": referer,
            "type": extension,
        }

        self.feed_file_description(f"{self.data_folder}files/", description)

    def hash_response(self, response):
        """
        Turns a response into a hashed value to be used as a file name

        :param response: response obtained from crawling

        :returns: hash of the response's URL and body
        """

        # POST requests may access the same URL with different parameters, so
        # we hash the URL with the response body
        return crawling_utils.hash(response.url.encode() + response.body)

    def preprocess_listify(self, value, default):
        """Converts a string of ',' separaded values into a list."""
        if value is None or len(value) == 0:
            value = default

        elif type(value) == str:
            value = tuple(value.replace(" ", "").split(","))

        return value

    def preprocess_download_configs(self):
        """Process download_files configurations."""
        defaults = [
            ("download_files_tags", ('a', 'area')),
            ("download_files_allow_domains", None),
            ("download_files_attrs", ('href',))
        ]

        for attr, default in defaults:
            self.config[attr] = self.preprocess_listify(
                self.config[attr], default)

        deny = "download_files_deny_extensions"
        if len(self.download_allowed_extensions) > 0:
            extensions = [
                ext for ext in scrapy.linkextractors.IGNORED_EXTENSIONS]
            self.config[deny] = [
                ext for ext in extensions if ext not in self.download_allowed_extensions]

        else:
            self.config[deny] = []

        attr = "download_files_process_value"
        if self.config[attr] is not None and len(self.config[attr]) > 0 and type(self.config[attr]) is str:
            self.config[attr] = eval(self.config[attr])

    def preprocess_link_configs(self):
        """Process link_extractor configurations."""

        defaults = [
            ("link_extractor_tags", ('a', 'area')),
            ("link_extractor_allow_domains", None),
            ("link_extractor_attrs", ('href',))
        ]
        for attr, default in defaults:
            self.config[attr] = self.preprocess_listify(
                self.config[attr], default)

    def spider_closed(self, spider):
        crawler_id = spider.crawler.settings.get('CRAWLER_ID')

        # PORT comes from the port module and is set on run.py directly from CLI input
        requests.get(
            f'http://localhost:{PORT}/detail/stop_crawl/{crawler_id}')
