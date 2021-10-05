import os


KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')

# Redis host information
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT', 10))

# django application port
SERVER_NEW_PAGE_FOUND_URL = os.getenv('SERVER_NEW_PAGE_FOUND_URL',
                                      'http://web_server:8000/download/pages/found/{instance_id}/{num_pages}')

# Kafka topics
LINK_GENERATOR_TOPIC = os.getenv('LINK_GENERATOR_TOPIC', KAFKA_TOPIC_PREFIX + '.link_generator')
