"""
Test script to verify DLQ messages are being created
"""
from confluent_kafka import Consumer
import config
import json

# Consumer for DLQ topic
dlq_consumer_conf = {
    'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'test-dlq-reader',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

consumer = Consumer(dlq_consumer_conf)
consumer.subscribe([config.DLQ_TOPIC])

print(f"🔍 Reading from DLQ topic: {config.DLQ_TOPIC}")
print(f"📊 Consumer group: test-dlq-reader")
print(f"⏳ Waiting for DLQ messages...")
print("-" * 70)

dlq_count = 0
timeout = 0

try:
    while timeout < 30:  # Wait max 30 seconds
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            timeout += 1
            print(f"⏳ Waiting... ({timeout}s)")
            continue
        
        if msg.error():
            print(f"❌ Consumer error: {msg.error()}")
            continue
        
        timeout = 0  # Reset timer if we get a message
        dlq_count += 1
        
        try:
            # Try to deserialize as JSON for debugging
            value = msg.value().decode('utf-8') if isinstance(msg.value(), bytes) else msg.value()
            print(f"💀 DLQ Message #{dlq_count}:")
            print(f"   Topic: {msg.topic()}")
            print(f"   Partition: {msg.partition()}")
            print(f"   Offset: {msg.offset()}")
            print(f"   Value: {value}")
            print()
        except Exception as e:
            print(f"💀 DLQ Message #{dlq_count} (binary): {msg.value()}")
            print()

except KeyboardInterrupt:
    print("\n⚠️  Test interrupted by user")
finally:
    print(f"\n✅ Total DLQ messages found: {dlq_count}")
    consumer.close()
