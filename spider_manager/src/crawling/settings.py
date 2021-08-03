from __future__ import absolute_import

REDIS_HOST = "localhost"
REDIS_PORT = "6379"
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_SOCKET_TIMEOUT = 10
KAFKA_HOSTS = ['localhost:9092']
KAFKA_TOPIC_PREFIX = "crawler_ufmg_sc"
KAFKA_APPID_TOPICS = False
KAFKA_BASE_64_ENCODE = False
KAFKA_PRODUCER_BATCH_LINGER_MS = 25
KAFKA_PRODUCER_BUFFER_BYTES = 4194304
KAFKA_PRODUCER_MAX_REQUEST_SIZE = 1048576
ZOOKEEPER_ASSIGN_PATH = "/scrapy-cluster/crawler/"
ZOOKEEPER_ID = "all"
ZOOKEEPER_HOSTS = "localhost:2181"
PUBLIC_IP_URL = "http://ip.42.pl/raw"
IP_ADDR_REGEX = "(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_REFRESH = 10
QUEUE_HITS = 1000000
QUEUE_WINDOW = 1
QUEUE_MODERATED = True
DUPEFILTER_TIMEOUT = 600
GLOBAL_PAGE_PER_DOMAIN_LIMIT = None
GLOBAL_PAGE_PER_DOMAIN_LIMIT_TIMEOUT = 600
DOMAIN_MAX_PAGE_TIMEOUT = 600
SCHEDULER_IP_REFRESH = 60
SCHEDULER_BACKLOG_BLACKLIST = True
SCHEDULER_TYPE_ENABLED = True
SCHEDULER_IP_ENABLED = True
SCHEUDLER_ITEM_RETRIES = 3
SCHEDULER_QUEUE_TIMEOUT = 7200
SC_LOGGER_NAME = "sc-crawler"
SC_LOG_DIR = "logs"
SC_LOG_FILE = "sc_crawler.log"
SC_LOG_MAX_BYTES = 10485760
SC_LOG_BACKUPS = 5
SC_LOG_STDOUT = True
SC_LOG_JSON = False
SC_LOG_LEVEL = "DEBUG"
STATS_STATUS_CODES = True
STATS_RESPONSE_CODES = [200, 404, 403, 504]
STATS_CYCLE = 5
STATS_TIMES = ['SECONDS_15_MINUTE', 'SECONDS_1_HOUR', 'SECONDS_6_HOUR', 'SECONDS_12_HOUR', 'SECONDS_1_DAY', 'SECONDS_1_WEEK']
BOT_NAME = "crawling"
SPIDER_MODULES = ['crawling.spiders']
NEWSPIDER_MODULE = "crawling.spiders"
SCHEDULER = "crawling.distributed_scheduler.DistributedScheduler"
ITEM_PIPELINES = {'crawling.pipelines.KafkaPipeline': 100, 'crawling.pipelines.LoggingBeforePipeline': 1}
SPIDER_MIDDLEWARES = {'scrapy.spidermiddlewares.depth.DepthMiddleware': None, 'crawling.meta_passthrough_middleware.MetaPassthroughMiddleware': 100, 'crawling.redis_stats_middleware.RedisStatsMiddleware': 101}
DOWNLOADER_MIDDLEWARES = {'scrapy.downloadermiddlewares.retry.RetryMiddleware': None, 'crawling.redis_retry_middleware.RedisRetryMiddleware': 510, 'crawling.log_retry_middleware.LogRetryMiddleware': 520, 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None, 'crawling.custom_cookies.CustomCookiesMiddleware': 700}
LOG_ENABLED = True
LOG_LEVEL = "DEBUG"
HTTPERROR_ALLOW_ALL = True
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 30
DNSCACHE_ENABLED = True
LOGGING_TOPIC = "crawler_ufmg_logs"
COMMANDS_TOPIC = "crawler_ufmg_commands"
NOTIFICATIONS_TOPIC = "crawler_ufmg_notifications"
DYNAMIC_PROCESSING = False
DYNAMIC_PROCESSING_STEPS = {}