"""
Configuration settings for Kafka producer and consumer
"""

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
SCHEMA_REGISTRY_URL = 'http://localhost:8081'

# Topic
ORDERS_TOPIC = 'orders'
DLQ_TOPIC = 'orders-dlq'

# Consumer Configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
CONSUMER_GROUP_ID = 'order-consumer-group'

# Producer Configuration
PRODUCER_FLUSH_TIMEOUT = 10

# Product catalog for random generation
PRODUCTS = [
    "Laptop",
    "Mouse",
    "Keyboard",
    "Monitor",
    "Headphones",
    "Webcam",
    "USB Cable",
    "External HDD",
    "SSD Drive",
    "Graphics Card"
]

# Price range for random generation
MIN_PRICE = 10.0
MAX_PRICE = 1500.0
