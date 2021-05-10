import time
import sys
import os
import datetime
from multiprocessing import Process

import ujson
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from kafka import KafkaProducer

from crawling.spiders.base_spider import BaseSpider
from crawling.spiders.static_page import StaticPageSpider

from kafka_logger import KafkaLogger

LOGGING_OUT_PREFIX = os.getenv('SPIDER_LOGGING_OUT_PREFIX', 'spider_logging_out')
LOGGING_ERR_PREFIX = os.getenv('SPIDER_LOGGING_ERR_PREFIX', 'spider_logging_err')

class Executor:
    def __init__(self):
        self.__processes = dict()
        # self.__notifier = KafkaProducer(bootstrap_servers=KAFKA_HOSTS,
        #                                 value_serializer=lambda m: ujson.dumps(m).encode('utf-8'))

    def __get_random_logging_name(self) -> str:
        first_name = os.getpid()
        last_name = int(datetime.datetime.now().timestamp())

        return f'{first_name}-{last_name}'

    def __get_spider_base_settings(self, config: dict) -> dict:
        with open('sc_base_config.json') as f:
            base_config = ujson.loads(f.read())
            base_config['SC_LOGGER_NAME'] = self.__get_random_logging_name()

            # autothrottle = "antiblock_autothrottle_"

            # base_config["ROBOTSTXT_OBEY"] = config['obey_robots']
            # base_config["DOWNLOAD_DELAY"] = 1
            # # base_config["DOWNLOADER_MIDDLEWARES"] = {'scrapy_puppeteer.PuppeteerMiddleware': 800}
            # base_config["DOWNLOAD_DELAY"] = config["antiblock_download_delay"]
            # base_config["RANDOMIZE_DOWNLOAD_DELAY"] = True
            # base_config["AUTOTHROTTLE_ENABLED"] = config[f"{autothrottle}enabled"]
            # base_config["AUTOTHROTTLE_START_DELAY"] = config[f"{autothrottle}start_delay"]
            # base_config["AUTOTHROTTLE_MAX_DELAY"] = config[f"{autothrottle}max_delay"]

            return base_config

    def __new_spider(self, config: dict) -> None:
        base_settings = self.__get_spider_base_settings(config)
        instance_id = config['instance_id']
    
        process = CrawlerProcess(settings=base_settings)

        sys.stdout = KafkaLogger(topic=f'{LOGGING_OUT_PREFIX}-{instance_id}')
        sys.stderr = KafkaLogger(topic=f'{LOGGING_ERR_PREFIX}-{instance_id}')

        process.crawl(StaticPageSpider, name=instance_id, config=ujson.dumps(config))

        # process.crawlers é um set() com um único spider. Como não há como recuperar o spider
        # sem removê-lo do set() diretamente, é realizado o esquema abaixo para isso. Assim, é
        # possível atribuir a chamada de uma função quando o evento de quando o spider é fechado.
        iter_crawler = iter(process.crawlers)
        crawler = next(iter_crawler)

        # Quando o spider for fechado, o sistema será notificado por meio da função notify_crawler_manager;
        crawler.signals.connect(self.__notify_stop, signal=scrapy.signals.spider_closed)

        process.start()
    
    def __notify_stop(self, spider: Spider, reason: str) -> None:
        # Notifica o crawler manager de algum erro ou algo do tipo que aconteceu com algum spider,
        # ele, por sua vez, notificará a aplicação Django

        # print('--')
        # self.__notifier.send(STOP_NOTIFICATION_TOPIC, {'stop': instance_id})
        # self.__notifier.flush()
        # print('--->', e)

        print(f'Spider "{spider.name}" closed because "{reason}"')

    def create_spider(self, config: dict) -> None:
        print(f'Criando novo spider #{config["instance_id"]}...')

        instance_id = config['instance_id']
        self.__processes[instance_id] = Process(target=self.__new_spider, args=(config, ))  
        self.__processes[instance_id].start()

    def stop_spider(self, instance_id: str) -> None:
        print(f'Parando spider #{instance_id}...')
        self.__processes[instance_id].terminate()

    def stop_all_spider(self):
        for instance_id in self.__processes:
            self.stop_spider(instance_id)
