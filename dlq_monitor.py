"""
Monitor Dead Letter Queue (DLQ) messages
Reads and displays messages that failed permanently
"""

from confluent_kafka import Consumer, KafkaException
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import config


def monitor_dlq():
    """Monitor and display DLQ messages"""
    # Schema Registry Client
    schema_registry_conf = {'url': config.SCHEMA_REGISTRY_URL}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    
    # Load Avro Schema
    with open('schemas/order.avsc', 'r') as f:
        schema_str = f.read()
    
    # Avro Deserializer
    avro_deserializer = AvroDeserializer(
        schema_registry_client,
        schema_str,
        lambda data, ctx: data
    )
    
    # Kafka Consumer for DLQ
    consumer_conf = {
        'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'dlq-monitor-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([config.DLQ_TOPIC])
    
    print("=" * 70)
    print("DEAD LETTER QUEUE MONITOR")
    print("=" * 70)
    print(f"Monitoring topic: {config.DLQ_TOPIC}")
    print("Press Ctrl+C to stop\n")
    
    message_count = 0
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                raise KafkaException(msg.error())
            
            try:
                # Deserialize message
                serialization_context = SerializationContext(
                    config.DLQ_TOPIC,
                    MessageField.VALUE
                )
                order = avro_deserializer(msg.value(), serialization_context)
                
                message_count += 1
                print(f"💀 DLQ Message #{message_count}")
                print(f"   Order ID: {order['orderId']}")
                print(f"   Product: {order['product']}")
                print(f"   Price: ${order['price']:.2f}")
                print(f"   Partition: {msg.partition()}, Offset: {msg.offset()}")
                print("-" * 70)
                
            except Exception as e:
                print(f"❌ Error processing DLQ message: {e}")
    
    except KeyboardInterrupt:
        print(f"\n\n📊 Total DLQ messages: {message_count}")
    finally:
        consumer.close()


if __name__ == "__main__":
    monitor_dlq()
