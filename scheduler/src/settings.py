import os

KAFKA_HOSTS = [x.strip() for x in os.getenv('KAFKA_HOSTS', 'kafka:9092').split(',')]
KAFKA_TOPIC_PREFIX = os.getenv('KAFKA_TOPIC_PREFIX', 'crawler_ufmg')
KAFKA_CONSUMER_AUTO_OFFSET_RESET = 'earliest'
KAFKA_CONSUMER_TIMEOUT = 120000
KAFKA_CONSUMER_COMMIT_INTERVAL_MS = 5000
KAFKA_CONSUMER_AUTO_COMMIT_ENABLE = True
KAFKA_CONSUMER_FETCH_MESSAGE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
KAFKA_PRODUCER_BATCH_LINGER_MS = 25  # 25 ms before flush
KAFKA_PRODUCER_BUFFER_BYTES = 4 * 1024 * 1024  # 4MB before blocking
KAFKA_CONNECTIONS_MAX_IDLE_MS = 10 * 60 * 1000
KAFKA_REQUEST_TIMEOUT_MS = 5 * 60 * 1000
KAFKA_SESSION_TIMEOUT_MS = 2 * 60 * 1000
TASK_TOPIC = os.getenv('TASK_TOPIC', KAFKA_TOPIC_PREFIX + 'task_topoc')
TASK_DATA_CONSUMER_GROUP = os.getenv('TASK_DATA_CONSUMER_DATA', KAFKA_TOPIC_PREFIX + '.task_data_group')
