"""
Kafka Consumer with Avro Deserialization
Features:
- Real-time running average calculation
- Retry logic for temporary failures
- Dead Letter Queue (DLQ) for permanently failed messages
"""

import time
from confluent_kafka import Consumer, Producer, KafkaException
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
import config


class OrderConsumer:
    def __init__(self):
        # Schema Registry Client
        schema_registry_conf = {'url': config.SCHEMA_REGISTRY_URL}
        self.schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        
        # Load Avro Schema
        with open('schemas/order.avsc', 'r') as f:
            schema_str = f.read()
        
        # Avro Deserializer
        self.avro_deserializer = AvroDeserializer(
            self.schema_registry_client,
            schema_str,
            lambda data, ctx: data
        )
        
        # Avro Serializer for DLQ
        self.avro_serializer = AvroSerializer(
            self.schema_registry_client,
            schema_str,
            lambda order, ctx: order
        )
        
        # Kafka Consumer
        consumer_conf = {
            'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': config.CONSUMER_GROUP_ID,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        self.consumer = Consumer(consumer_conf)
        
        # Kafka Producer for DLQ
        producer_conf = {
            'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'dlq-producer'
        }
        self.dlq_producer = Producer(producer_conf)
        
        # Aggregation state
        self.total_price = 0.0
        self.order_count = 0
        self.running_average = 0.0
        
        # Retry tracking
        self.retry_counts = {}
    
    def calculate_running_average(self, price):
        """Update running average with new price"""
        self.order_count += 1
        self.total_price += price
        self.running_average = self.total_price / self.order_count
        return self.running_average
    
    def send_to_dlq(self, order, error_message):
        """Send failed message to Dead Letter Queue"""
        try:
            # Add error information to the order
            dlq_message = {
                'orderId': order['orderId'],
                'product': order['product'],
                'price': order['price']
            }
            
            serialization_context = SerializationContext(
                config.DLQ_TOPIC,
                MessageField.VALUE
            )
            
            serialized_order = self.avro_serializer(
                dlq_message,
                serialization_context
            )
            
            self.dlq_producer.produce(
                topic=config.DLQ_TOPIC,
                value=serialized_order
            )
            self.dlq_producer.flush()
            
            print(f"💀 Sent to DLQ - Order ID: {order['orderId']}, Reason: {error_message}")
            
        except Exception as e:
            print(f"❌ Failed to send to DLQ: {e}")
    
    def process_order(self, order, retry_attempt=0):
        """
        Process an order with retry logic
        Simulates temporary failures for demonstration
        """
        order_id = order['orderId']
        
        # Simulate 30% chance of temporary failure on first attempt
        if retry_attempt == 0 and int(order_id) % 10 in [3, 7]:
            raise Exception("Simulated temporary processing failure")
        
        # Simulate permanent failure for specific orders
        if int(order_id) % 15 == 0:
            raise Exception("Simulated permanent failure - invalid order data")
        
        # Process successfully
        avg = self.calculate_running_average(order['price'])
        print(f"✅ Processed Order #{order_id} - Product: {order['product']}, "
              f"Price: ${order['price']:.2f} | Running Avg: ${avg:.2f}")
        
        return True
    
    def consume_orders(self):
        """Main consumer loop with retry and DLQ logic"""
        self.consumer.subscribe([config.ORDERS_TOPIC])
        
        print(f"🎧 Listening for orders on topic: {config.ORDERS_TOPIC}")
        print(f"📊 Calculating running average of prices...")
        print(f"🔄 Max retries: {config.MAX_RETRIES}")
        print(f"💀 DLQ topic: {config.DLQ_TOPIC}")
        print("-" * 70)
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    raise KafkaException(msg.error())
                
                try:
                    # Deserialize message
                    serialization_context = SerializationContext(
                        config.ORDERS_TOPIC,
                        MessageField.VALUE
                    )
                    order = self.avro_deserializer(
                        msg.value(),
                        serialization_context
                    )
                    
                    order_id = order['orderId']
                    retry_count = self.retry_counts.get(order_id, 0)
                    
                    # Try to process the order
                    try:
                        self.process_order(order, retry_count)
                        
                        # Success - commit offset and clear retry count
                        self.consumer.commit(msg)
                        if order_id in self.retry_counts:
                            del self.retry_counts[order_id]
                    
                    except Exception as e:
                        print(f"⚠️  Processing failed for Order #{order_id}: {e}")
                        
                        if retry_count < config.MAX_RETRIES:
                            # Retry logic
                            self.retry_counts[order_id] = retry_count + 1
                            print(f"🔄 Retry {retry_count + 1}/{config.MAX_RETRIES} for Order #{order_id}")
                            time.sleep(config.RETRY_DELAY_SECONDS)
                            
                            # Reprocess without committing
                            try:
                                self.process_order(order, retry_count + 1)
                                self.consumer.commit(msg)
                                del self.retry_counts[order_id]
                            except Exception as retry_error:
                                print(f"⚠️  Retry failed: {retry_error}")
                                continue
                        else:
                            # Max retries exceeded - send to DLQ
                            print(f"🚫 Max retries exceeded for Order #{order_id}")
                            self.send_to_dlq(order, str(e))
                            self.consumer.commit(msg)
                            if order_id in self.retry_counts:
                                del self.retry_counts[order_id]
                
                except Exception as e:
                    print(f"❌ Error deserializing message: {e}")
                    self.consumer.commit(msg)
        
        except KeyboardInterrupt:
            print("\n⚠️  Consumer interrupted by user")
        finally:
            print(f"\n📊 Final Statistics:")
            print(f"   Total Orders Processed: {self.order_count}")
            print(f"   Total Revenue: ${self.total_price:.2f}")
            print(f"   Average Order Price: ${self.running_average:.2f}")
            self.consumer.close()


def main():
    consumer = OrderConsumer()
    
    print("=" * 70)
    print("KAFKA ORDER CONSUMER WITH AVRO DESERIALIZATION")
    print("=" * 70)
    
    consumer.consume_orders()


if __name__ == "__main__":
    main()
