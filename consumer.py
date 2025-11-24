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
            
            # Define callback for delivery confirmation
            def delivery_callback(err, msg):
                if err:
                    print(f"❌ Failed to deliver DLQ message for Order #{order['orderId']}: {err}")
                else:
                    print(f"✅ DLQ message delivered - Order ID: {order['orderId']}, "
                          f"Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}")
            
            self.dlq_producer.produce(
                topic=config.DLQ_TOPIC,
                value=serialized_order,
                callback=delivery_callback,
                partition=0  # Force to partition 0 for consistency
            )
            
            # Flush with longer timeout
            remaining = self.dlq_producer.flush(timeout=10)
            if remaining > 0:
                print(f"⚠️  Warning: {remaining} messages still in DLQ producer queue after flush")
            
            print(f"💀 Order #{order['orderId']} queued for DLQ - Reason: {error_message}")
            
        except Exception as e:
            print(f"❌ Failed to send to DLQ: {e}")
            import traceback
            traceback.print_exc()
    
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
                    
                    # Retry loop for this specific message - LOCAL RETRY LOGIC
                    sent_to_dlq = False
                    for attempt in range(config.MAX_RETRIES + 1):
                        try:
                            self.process_order(order, attempt)
                            # Success - commit and exit retry loop
                            self.consumer.commit(msg)
                            break
                        
                        except Exception as e:
                            error_msg = str(e)
                            if attempt == 0:
                                print(f"⚠️  Processing failed for Order #{order_id}: {error_msg}")
                            
                            if attempt < config.MAX_RETRIES:
                                # Not the last attempt, retry
                                attempt_num = attempt + 1
                                print(f"🔄 Retry {attempt_num}/{config.MAX_RETRIES} for Order #{order_id}")
                                time.sleep(config.RETRY_DELAY_SECONDS)
                                # Continue to next iteration of retry loop
                            else:
                                # Max retries exceeded - send to DLQ
                                print(f"🚫 Max retries exceeded for Order #{order_id}")
                                self.send_to_dlq(order, error_msg)
                                self.consumer.commit(msg)
                                sent_to_dlq = True
                                break
                
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
