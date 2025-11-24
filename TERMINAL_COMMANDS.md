# COMPLETE STEP-BY-STEP TERMINAL COMMANDS

## 📋 Prerequisites
- Docker Desktop must be running
- Python 3.11+ installed
- All files from the assignment in place

---

## ✅ STEP 1: Verify Setup (Optional but Recommended)

### Check Docker is Running
```powershell
docker --version
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

### Check Python is Installed
```powershell
python --version
```

Expected: `Python 3.11.x` or higher

---

## 🚀 STEP 2: Navigate to Project Directory

```powershell
cd "e:\8th sem\big data\assigment 01\kafka-avro-assignment"
```

Verify you're in correct directory:
```powershell
pwd
ls
```

You should see these files:
- `producer.py`
- `consumer.py`
- `app.py` (dashboard)
- `config.py`
- `docker-compose.yml`
- `requirements.txt`
- etc.

---

## 📦 STEP 3: Install Python Dependencies (First Time Only)

```powershell
pip install -r requirements.txt
```

Wait for completion. You should see:
```
Successfully installed confluent-kafka flask flask-cors flask-socketio ...
```

**Note**: You only need to do this once. Skip if already installed.

---

## 🐳 STEP 4: Start Kafka Infrastructure

```powershell
docker-compose up -d
```

You'll see:
```
[+] Running 3/3
 ✔ Container zookeeper  Started
 ✔ Container kafka      Started
 ✔ Container schema-registry  Started
```

### Verify Kafka is Running
```powershell
docker-compose ps
```

Expected output:
```
NAME              IMAGE                             STATUS
zookeeper         confluentinc/cp-zookeeper:7.5.0   Up 1 minute
kafka             confluentinc/cp-kafka:7.5.0       Up 1 minute
schema-registry   confluentinc/cp-schema-registry   Up 1 minute
```

### Wait 30-40 seconds for services to fully start

```powershell
Start-Sleep -Seconds 40
```

---

## 🎯 STEP 5: Open 3-4 Terminal Windows

You need multiple terminals for:
1. **Dashboard Server** (Flask)
2. **Consumer** (Kafka message processing)
3. **Producer** (Generate test orders)
4. (Optional) **Monitoring**

**In PowerShell, you can open new tabs:**
- `Ctrl+Shift+2` or use menu to add new tabs

Or open new PowerShell windows manually.

---

## 📊 STEP 6: Start Dashboard Server (Terminal 1)

**Make sure you're in the project directory**

```powershell
python app.py
```

Expected output:
```
========================================================================
KAFKA MONITORING DASHBOARD API
========================================================================
📊 Dashboard running on http://localhost:5000
🔌 WebSocket server for real-time updates
========================================================================
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

**Keep this terminal open**

---

## 🎧 STEP 7: Start Consumer (Terminal 2)

```powershell
cd "e:\8th sem\big data\assigment 01\kafka-avro-assignment"
python consumer.py
```

Expected output:
```
======================================================================
KAFKA ORDER CONSUMER WITH AVRO DESERIALIZATION
======================================================================
🎧 Listening for orders on topic: orders
📊 Calculating running average of prices...
🔄 Max retries: 3
💀 DLQ topic: orders-dlq
----------------------------------------------------------------------
```

**Keep this terminal open** - It will process messages as producer sends them

---

## 🌐 STEP 8: Open Dashboard in Browser

In your web browser, go to:

```
http://localhost:5000
```

You should see:
- **Header**: "Kafka Order Processing Dashboard"
- **Stat Cards**: All showing 0 values (no data yet)
- **Status**: "Disconnected" (will change when producer starts)

**Keep dashboard open in browser**

---

## 📦 STEP 9: Start Producer (Terminal 3)

```powershell
cd "e:\8th sem\big data\assigment 01\kafka-avro-assignment"
python producer.py
```

Expected output:
```
======================================================================
KAFKA ORDER PRODUCER WITH AVRO SERIALIZATION
======================================================================
🚀 Starting to produce 20 orders...
📡 Publishing to topic: orders
----------------------------------------------------------------------
📦 Order #1 - ID: 1, Product: Laptop, Price: $1245.67
✅ Message delivered to orders [partition 0] at offset 0
📦 Order #2 - ID: 2, Product: Mouse, Price: $25.99
✅ Message delivered to orders [partition 0] at offset 1
...
```

**Watch the terminal for order confirmations**

---

## 🔄 STEP 10: Watch Real-time Updates

### Check Consumer Terminal (Terminal 2)
You should see orders being processed:
```
✅ Processed Order #1 - Product: Laptop, Price: $1245.67 | Running Avg: $1245.67
✅ Processed Order #2 - Product: Mouse, Price: $25.99 | Running Avg: $635.83
⚠️  Processing failed for Order #3: Simulated temporary processing failure
🔄 Retry 1/3 for Order #3
✅ Processed Order #3 - Product: Keyboard, Price: $89.50 | Running Avg: $453.72
```

### Check Dashboard in Browser
The stats should update in real-time:
- ✅ Total Orders increases
- 💰 Total Revenue increases
- 📈 Average Price updates
- ⚠️ Error Rate shows percentage
- 💀 DLQ Count increases (for failed orders)
- ⚡ Processing Rate shows orders/minute

### Watch the Tables
- **Recent Orders table** fills with order data
- **DLQ table** shows failed orders (orders 15, 30, etc.)

---

## 💀 STEP 11: Optional - Monitor DLQ Messages

In a 4th terminal:

```powershell
cd "e:\8th sem\big data\assigment 01\kafka-avro-assignment"
python dlq_monitor.py
```

This shows failed messages that went to Dead Letter Queue:
```
======================================================================
DEAD LETTER QUEUE MONITOR
======================================================================
Monitoring topic: orders-dlq
Press Ctrl+C to stop

💀 DLQ Message #1
   Order ID: 15
   Product: Monitor
   Price: $299.99
   Partition: 0, Offset: 0
```

---

## 📊 STEP 12: View Live Statistics

### In Dashboard Browser (http://localhost:5000)

You'll see:
1. **Top 6 Stat Cards** - All updating in real-time
2. **Product Distribution Chart** - Doughnut chart updating
3. **Real-time Metrics Widget** - Live counters
4. **Recent Orders Table** - New orders appearing
5. **DLQ Table** - Failed orders showing up

---

## 🛑 STEP 13: Stop Everything (When Done)

### In Producer Terminal (Ctrl+C)
```
^C
```

Wait for completion message.

### In Consumer Terminal (Ctrl+C)
```
^C
```

You'll see final statistics:
```
📊 Final Statistics:
   Total Orders Processed: 20
   Total Revenue: $10,250.45
   Average Order Price: $512.52
```

### In Dashboard Terminal (Ctrl+C)
```
^C
```

### Stop Kafka Infrastructure
```powershell
docker-compose down
```

To also remove volumes:
```powershell
docker-compose down -v
```

---

## ⚡ QUICK COMMAND SUMMARY

**Copy & paste these in order:**

```powershell
# Terminal 1 - Start Kafka
docker-compose up -d
Start-Sleep -Seconds 40

# Terminal 1 - Start Dashboard
python app.py

# Terminal 2 - Start Consumer
python consumer.py

# Terminal 3 - Start Producer
python producer.py

# Terminal 4 (Optional) - Monitor DLQ
python dlq_monitor.py
```

---

## 🎯 Expected Timeline

| Step | Time | Action | Result |
|------|------|--------|--------|
| 1 | 0s | Start Kafka | Containers starting |
| 2 | 40s | Start Dashboard | Server listening on 5000 |
| 3 | 45s | Open Browser | Dashboard loads (empty) |
| 4 | 50s | Start Consumer | Waiting for messages |
| 5 | 55s | Start Producer | Orders generating |
| 6 | 60s | → | **Dashboard updates LIVE!** |
| 7 | 75s | Producer completes | 20 orders sent |
| 8 | 80s | → | **Consumer finishes processing** |
| 9 | 85s | View Results | All stats complete |

---

## ✅ Verification Checklist

Before starting demo:

- [ ] Docker Desktop is running
- [ ] Project directory is correct
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Kafka started and running (`docker-compose ps`)
- [ ] Dashboard running on http://localhost:5000
- [ ] Consumer waiting for messages
- [ ] Browser dashboard loads without errors
- [ ] Producer ready to generate orders

---

## 🎬 DEMO FLOW

1. **Show Kafka running** - `docker-compose ps`
2. **Show Dashboard** - Open http://localhost:5000
3. **Show Consumer waiting** - Pointing to Terminal 2
4. **Start Producer** - Show orders being generated
5. **Point out Dashboard updates** - Real-time metrics
6. **Show Retry Logic** - Orders 3, 7, 13 failing then retrying
7. **Show DLQ** - Orders 15, 30 in DLQ
8. **Show Final Stats** - After producer completes
9. **Highlight Features** - Charts, tables, status indicator

---

## 🐛 TROUBLESHOOTING DURING EXECUTION

### Dashboard won't load (http://localhost:5000)
```powershell
# Check if Flask is running
netstat -ano | findstr :5000

# Kill process if needed and restart
taskkill /PID <PID> /F
python app.py
```

### Consumer not showing messages
```powershell
# Check Kafka is running
docker ps | findstr kafka

# Restart if needed
docker-compose restart kafka
```

### Producer fails to send
```powershell
# Wait 40 seconds after docker-compose up
# Kafka needs time to initialize

# Or restart producer
# python producer.py
```

### No updates in dashboard
```powershell
# Check browser console (F12)
# Check Flask logs in terminal
# Make sure consumer is running
```

---

## 📝 NOTES

- **Producer sends 20 orders** with 1-second delay
- **Consumer processes** and shows running average
- **Retry logic**: Orders 3, 7, 13, 17, 23, 27 will fail initially
- **DLQ routing**: Orders 15, 30 will permanently fail
- **Dashboard updates** every 2-3 seconds
- **Keep terminals open** to show live processing

---

Good luck with your demo! 🚀
