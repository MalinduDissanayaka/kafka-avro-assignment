# 🚀 Complete Step-by-Step Run Guide

This guide walks you through running the entire Kafka-Avro Order Processing System with Real-time Dashboard.

---

## ✅ Prerequisites

Make sure you have:
- ✅ Python 3.13+ installed
- ✅ Docker Desktop installed and running
- ✅ All dependencies installed (run once at start)

---

## 📋 Step 1: Install Dependencies (First Time Only)

Run this command **once** at the beginning:

```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed confluent-kafka-2.6.0
Successfully installed flask-3.0.0
Successfully installed flask-socketio-5.4.0
...
```

---

## 🐳 Step 2: Start Docker & Kafka Infrastructure

Docker Desktop must be running. Then start Kafka services:

```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'
docker-compose up -d
```

**Expected Output:**
```
Creating kafka-avro-assignment_zookeeper_1 ... done
Creating kafka-avro-assignment_kafka_1 ... done
Creating kafka-avro-assignment_schema-registry_1 ... done
```

**Verify Kafka is running:**
```powershell
docker-compose ps
```

You should see 3 containers with status "Up":
```
NAME                                    STATUS
kafka-avro-assignment_zookeeper_1       Up 2 seconds
kafka-avro-assignment_kafka_1           Up 2 seconds
kafka-avro-assignment_schema-registry_1 Up 2 seconds
```

---

## 🎯 Step 3: Start the Dashboard Server (Terminal 1)

Open **Terminal 1** and run:

```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'
python app.py
```

**Expected Output:**
```
📁 Template directory: E:\8th sem\big data\assigment 01\kafka-avro-assignment\templates
📁 Static directory: E:\8th sem\big data\assigment 01\kafka-avro-assignment\static

======================================================================
KAFKA MONITORING DASHBOARD - STARTING
======================================================================
✅ Schema Registry connected
✅ Orders consumer connected
✅ DLQ consumer connected
✅ Kafka connection initialized successfully

📊 Dashboard running on http://localhost:5000
🔌 WebSocket server for real-time updates
======================================================================

 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

✅ **Dashboard is now running!** Keep this terminal open.

---

## 📊 Step 4: Open Dashboard in Browser

While Terminal 1 is running, open your browser and visit:

```
http://127.0.0.1:5000
```

**You should see:**
- 📈 6 stat cards (Total Orders, Revenue, Average Price, etc.)
- 📋 Recent Orders table (empty initially)
- 💀 DLQ Messages table
- 📊 Product Distribution chart

**Status:** "Disconnected" is normal - no orders yet.

---

## 🏭 Step 5: Start the Producer (Terminal 2)

Open **Terminal 2** and run:

```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'
python producer.py
```

**Expected Output:**
```
🚀 OrderProducer starting...
📤 Sending order #1: {"order_id": "ORD001", "product": "Laptop", "price": 1200.0, ...}
✅ Message delivered to topic 'orders' partition [0] at offset 1
📤 Sending order #2: {"order_id": "ORD002", "product": "Mouse", "price": 25.0, ...}
✅ Message delivered to topic 'orders' partition [0] at offset 2
...
📤 Sending order #20: {"order_id": "ORD020", ...}
✅ Message delivered to topic 'orders' partition [0] at offset 20
🏁 Producer finished! All 20 orders sent.
```

**This terminal completes after ~25 seconds.** You can close it.

---

## 👁️ Step 6: Watch Consumer Process Orders (Terminal 3)

While the producer is running, open **Terminal 3** to see the consumer processing:

```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'
python consumer.py
```

**Expected Output (runs continuously):**
```
🔄 OrderConsumer starting...
✅ Consumer subscribed to topic 'orders'
===== ORDER PROCESSING =====

📥 Received order: ORD001 | Product: Laptop | Price: $1200.00
✅ Order ORD001 processed successfully
   Running Average: $1200.00
   Total Revenue: $1200.00

📥 Received order: ORD002 | Product: Mouse | Price: $25.00
✅ Order ORD002 processed successfully
   Running Average: $612.50
   Total Revenue: $1225.00

...

📥 Received order: ORD015 (SIMULATED FAILURE - Max Retries Exceeded)
❌ Order ORD015 moved to DLQ after 3 retries
   Retry attempt 1 - Failed
   Retry attempt 2 - Failed
   Retry attempt 3 - Failed

...
```

**Keep this running!** This processes orders in real-time.

---

## 📊 Step 7: Watch Dashboard Update in Real-Time

Go back to your browser at `http://127.0.0.1:5000`

**You should see:**
- ✅ Status changes to **"Connected"** (green)
- 📈 **Total Orders** increases (1, 2, 3, ... 20)
- 💰 **Total Revenue** updates (adds each price)
- 📊 **Average Price** recalculates in real-time
- 📋 **Recent Orders** table populates with latest orders
- 💀 **DLQ Messages** shows failed orders (like ORD015, ORD030)
- 📊 **Product Distribution** pie chart updates with counts

The dashboard updates **every 1-2 seconds** automatically!

---

## 🔄 System Architecture Overview

```
┌──────────────┐
│  Producer    │  Generates 20 orders with 1-second delay
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│   Kafka Topic: "orders"              │
│   - Avro Serialization               │
│   - Schema Registry Integration      │
└──────────┬───────────────────────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌─────────┐
│Consumer │  │Dashboard│
│Process  │  │ (Flask) │
│Orders   │  │  + API  │
└────┬────┘  └────┬────┘
     │            │
     ├──────┬─────┤
     ▼      ▼     ▼
  Running  DLQ   Browser
  Average
  (Agg)
```

---

## 📊 Key Features Demonstrated

### ✅ Avro Serialization
- Orders serialized with Avro schema (order.avsc)
- Schema Registry validates structure
- Deserialization in consumer

### ✅ Real-Time Aggregation
- Running average price calculated per order
- Updates immediately on dashboard

### ✅ Retry Logic
- Max 3 retries with 2-second delays
- Simulated failures on orders: 3, 7, 13, 17
- Visual logging of retry attempts

### ✅ Dead Letter Queue (DLQ)
- Orders that fail after 3 retries go to DLQ
- Orders 15, 30 intentionally fail completely
- DLQ messages visible in dashboard

### ✅ Real-Time Dashboard
- WebSocket connection for live updates
- REST API fallback (every 1 second)
- Professional responsive design

---

## 🧪 Test Scenarios

### Scenario 1: Full Flow (25 seconds)
1. Start dashboard (Terminal 1)
2. Start consumer (Terminal 3)
3. Start producer (Terminal 2) - runs 20 orders over ~25 seconds
4. Watch dashboard update in real-time
5. See DLQ messages appear for failed orders

### Scenario 2: Multiple Producers
Run producer multiple times:
```powershell
python producer.py
python producer.py
python producer.py
```
This generates 60 total orders. Consumer processes all of them.

### Scenario 3: Manual Testing
Run consumer alone, then send individual orders with Kafka CLI (advanced).

---

## 🛑 Stop Everything (When Done)

### Stop Consumer (Terminal 3)
```powershell
Ctrl+C
```

### Stop Producer (Terminal 2)
```powershell
Ctrl+C
```

### Stop Dashboard (Terminal 1)
```powershell
Ctrl+C
```

### Stop Kafka Services
```powershell
docker-compose down
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused" or Kafka not found
**Solution:**
```powershell
docker-compose ps
docker-compose restart
```

### Problem: Dashboard shows "Disconnected"
**Solution:**
- Make sure consumer.py is running (Terminal 3)
- Refresh browser (F5 or Ctrl+Shift+R)
- Check if Flask terminal (Terminal 1) has errors

### Problem: "Port 5000 already in use"
**Solution:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Problem: Python dependencies issue
**Solution:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## 📈 Expected Results After Full Run

When all 20 orders are processed:

| Metric | Expected Value |
|--------|-----------------|
| **Total Orders** | 20 |
| **Total Revenue** | ~$5,000-$10,000 (depends on products) |
| **Average Price** | ~$300-$500 |
| **Processed Orders** | 17-18 (some fail) |
| **DLQ Orders** | 2-3 (intentional failures) |
| **Products** | 5 different product types |

---

## 📝 Files Reference

- **producer.py** - Generates and sends orders
- **consumer.py** - Processes orders, calculates average, handles retries
- **app.py** - Flask dashboard server
- **config.py** - Kafka & configuration settings
- **order.avsc** - Avro schema for orders
- **templates/dashboard.html** - Dashboard UI
- **static/dashboard.js** - Real-time updates
- **static/style.css** - Dashboard styling

---

## 🎓 Assignment Completion Checklist

- ✅ **Kafka Producer**: Generates orders with Avro serialization
- ✅ **Kafka Consumer**: Processes orders, calculates running average
- ✅ **Avro Schema**: order.avsc defines message structure
- ✅ **Retry Logic**: Max 3 retries with 2-second delays
- ✅ **Dead Letter Queue**: Failed orders routed to DLQ topic
- ✅ **Real-Time Aggregation**: Running average updated per order
- ✅ **Dashboard**: Professional web UI with live metrics
- ✅ **Docker**: Full infrastructure in docker-compose.yml

---

## 🎬 Quick Start (Copy & Paste)

**Terminal 1:**
```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'; docker-compose up -d; python app.py
```

**Terminal 2:**
```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'; python producer.py
```

**Terminal 3:**
```powershell
cd 'e:\8th sem\big data\assigment 01\kafka-avro-assignment'; python consumer.py
```

Then open browser: `http://127.0.0.1:5000`

---

**All set! 🚀 Your Kafka system is ready to demo!**
