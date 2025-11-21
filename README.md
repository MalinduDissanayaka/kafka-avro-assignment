# Kafka Avro Assignment - Order Processing System

A complete Kafka-based system for processing order messages with Avro serialization, featuring real-time price aggregation, retry logic, and Dead Letter Queue (DLQ) support.

## 🎯 Features

- ✅ **Avro Serialization**: Messages serialized using Apache Avro schema
- ✅ **Real-time Aggregation**: Running average calculation of order prices
- ✅ **Retry Logic**: Automatic retry mechanism for temporary failures (max 3 retries)
- ✅ **Dead Letter Queue (DLQ)**: Failed messages routed to separate topic
- ✅ **Schema Registry**: Centralized schema management
- ✅ **Docker Setup**: Easy deployment with Docker Compose

## 📋 Prerequisites

- Docker Desktop
- Python 3.8+
- Git

## 🚀 Quick Start

### 1. Clone and Setup

```powershell
cd "e:\8th sem\big data\assigment 01\kafka-avro-assignment"
```

### 2. Start Kafka Infrastructure

```powershell
docker-compose up -d
```

This starts:
- Zookeeper (port 2181)
- Kafka broker (port 9092)
- Schema Registry (port 8081)

Verify all containers are running:
```powershell
docker-compose ps
```

### 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the System

#### Terminal 1 - Start Consumer
```powershell
python consumer.py
```

The consumer will:
- Subscribe to the `orders` topic
- Calculate running average of prices
- Retry failed messages up to 3 times
- Send permanently failed messages to DLQ

#### Terminal 2 - Start Producer
```powershell
python producer.py
```

The producer will:
- Generate 20 random order messages
- Serialize with Avro
- Publish to `orders` topic

## 📊 Project Structure

```
kafka-avro-assignment/
├── docker-compose.yml          # Kafka, Zookeeper, Schema Registry setup
├── schemas/
│   └── order.avsc              # Avro schema definition
├── config.py                   # Configuration settings
├── producer.py                 # Order producer with Avro serialization
├── consumer.py                 # Order consumer with retry & DLQ
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📝 Order Schema (order.avsc)

```json
{
  "type": "record",
  "name": "Order",
  "namespace": "com.bigdata.kafka",
  "fields": [
    {"name": "orderId", "type": "string"},
    {"name": "product", "type": "string"},
    {"name": "price", "type": "float"}
  ]
}
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
SCHEMA_REGISTRY_URL = 'http://localhost:8081'
ORDERS_TOPIC = 'orders'
DLQ_TOPIC = 'orders-dlq'
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
```

## 🎬 Live Demo Flow

### Expected Output

**Producer:**
```
🚀 Starting to produce 20 orders...
📦 Order #1 - ID: 1, Product: Laptop, Price: $1245.67
✅ Message delivered to orders [partition 0] at offset 0
📦 Order #2 - ID: 2, Product: Mouse, Price: $25.99
✅ Message delivered to orders [partition 0] at offset 1
...
```

**Consumer:**
```
🎧 Listening for orders on topic: orders
✅ Processed Order #1 - Product: Laptop, Price: $1245.67 | Running Avg: $1245.67
✅ Processed Order #2 - Product: Mouse, Price: $25.99 | Running Avg: $635.83
⚠️  Processing failed for Order #3: Simulated temporary processing failure
🔄 Retry 1/3 for Order #3
✅ Processed Order #3 - Product: Keyboard, Price: $89.50 | Running Avg: $453.72
...
🚫 Max retries exceeded for Order #15
💀 Sent to DLQ - Order ID: 15, Reason: Simulated permanent failure
```

## 🧪 Testing Features

### 1. Retry Logic
- Orders with ID ending in 3 or 7 (e.g., 3, 7, 13, 17) will fail initially
- System automatically retries up to 3 times with 2-second delay
- Watch the consumer logs for retry messages

### 2. Dead Letter Queue
- Orders divisible by 15 (e.g., 15, 30) will permanently fail
- These are automatically sent to `orders-dlq` topic
- Check DLQ messages:
  ```powershell
  docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders-dlq --from-beginning
  ```

### 3. Running Average
- Consumer calculates and displays running average after each order
- Formula: `Running Avg = Total Price / Order Count`

## 🐛 Troubleshooting

### Kafka not accessible
```powershell
# Restart containers
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs kafka
```

### Schema Registry errors
```powershell
# Verify Schema Registry is running
curl http://localhost:8081/subjects

# Check Schema Registry logs
docker-compose logs schema-registry
```

### Python dependencies issues
```powershell
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📦 Viewing Messages

### View all orders:
```powershell
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders --from-beginning
```

### View DLQ messages:
```powershell
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders-dlq --from-beginning
```

### List all topics:
```powershell
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list
```

## 🛑 Cleanup

Stop and remove all containers:
```powershell
docker-compose down -v
```

## 📚 Technologies Used

- **Apache Kafka**: Distributed streaming platform
- **Apache Avro**: Data serialization framework
- **Confluent Platform**: Schema Registry for Avro schemas
- **Python**: Programming language
- **confluent-kafka-python**: Kafka client library
- **Docker**: Containerization

## 🎓 Assignment Requirements Checklist

- ✅ Kafka-based producer and consumer
- ✅ Avro serialization for messages
- ✅ Real-time aggregation (running average of prices)
- ✅ Retry logic for temporary failures
- ✅ Dead Letter Queue for permanently failed messages
- ✅ Live demonstration capability
- ✅ Git repository ready for submission

## 👨‍💻 Author

Big Data Assignment - 8th Semester

## 📄 License

This project is for educational purposes.
