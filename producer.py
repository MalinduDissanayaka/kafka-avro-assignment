"""
Kafka Producer with Avro Serialization
Generates random order messages and publishes them to Kafka
"""

import time
import random
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import config


class OrderProducer:
    def __init__(self):
        # Schema Registry Client
        schema_registry_conf = {'url': config.SCHEMA_REGISTRY_URL}
        self.schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        
        # Load Avro Schema
        with open('schemas/order.avsc', 'r') as f:
            schema_str = f.read()
        
        # Avro Serializer
        self.avro_serializer = AvroSerializer(
            self.schema_registry_client,
            schema_str,
            lambda order, ctx: order
        )
        
        # Kafka Producer
        producer_conf = {
            'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'order-producer'
        }
        self.producer = Producer(producer_conf)
    
    def delivery_report(self, err, msg):
        """Callback for message delivery reports"""
        if err is not None:
            print(f'❌ Message delivery failed: {err}')
        else:
            print(f'✅ Message delivered to {msg.topic()} [partition {msg.partition()}] at offset {msg.offset()}')
    
    def generate_order(self, order_id):
        """Generate a random order"""
        return {
            'orderId': str(order_id),
            'product': random.choice(config.PRODUCTS),
            'price': round(random.uniform(config.MIN_PRICE, config.MAX_PRICE), 2)
        }
    
    def produce_orders(self, num_orders=10, delay=1):
        """Produce a specified number of orders with a delay between each"""
        print(f"🚀 Starting to produce {num_orders} orders...")
        print(f"📡 Publishing to topic: {config.ORDERS_TOPIC}")
        print("-" * 70)
        
        for i in range(1, num_orders + 1):
            try:
                order = self.generate_order(i)
                
                # Serialize and send
                serialization_context = SerializationContext(
                    config.ORDERS_TOPIC,
                    MessageField.VALUE
                )
                
                serialized_order = self.avro_serializer(
                    order,
                    serialization_context
                )
                
                self.producer.produce(
                    topic=config.ORDERS_TOPIC,
                    value=serialized_order,
                    on_delivery=self.delivery_report
                )
                
                print(f"📦 Order #{i} - ID: {order['orderId']}, Product: {order['product']}, Price: ${order['price']:.2f}")
                
                # Flush to ensure delivery
                self.producer.poll(0)
                
                time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Error producing order {i}: {e}")
        
        # Final flush to ensure all messages are sent
        print("\n⏳ Flushing remaining messages...")
        self.producer.flush(config.PRODUCER_FLUSH_TIMEOUT)
        print(f"✅ Successfully produced {num_orders} orders!")


def main():
    producer = OrderProducer()
    
    print("=" * 70)
    print("KAFKA ORDER PRODUCER WITH AVRO SERIALIZATION")
    print("=" * 70)
    
    try:
        # Produce 20 orders with 1 second delay between each
        producer.produce_orders(num_orders=20, delay=1)
    except KeyboardInterrupt:
        print("\n⚠️  Producer interrupted by user")
    except Exception as e:
        print(f"\n❌ Producer error: {e}")


if __name__ == "__main__":
    main()
