# Quick Start Guide - Kafka Avro Assignment

## 🚀 Super Quick Start (5 minutes)

### 1️⃣ Setup Everything
Open PowerShell in the project folder and run:
```powershell
.\setup.ps1
```

### 2️⃣ Run Consumer (Terminal 1)
```powershell
python consumer.py
```

### 3️⃣ Run Producer (Terminal 2)
```powershell
python producer.py
```

### 4️⃣ Monitor DLQ (Optional - Terminal 3)
```powershell
python dlq_monitor.py
```

---

## 📋 Manual Setup (If setup.ps1 fails)

### Step 1: Start Kafka
```powershell
docker-compose up -d
```

Wait 30 seconds for services to start.

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the System
See steps 2-4 above.

---

## 🎯 What to Observe

### In Consumer Terminal:
- ✅ Successfully processed orders with running average
- ⚠️ Retry attempts for failed orders (IDs: 3, 7, 13, 17, 23, 27)
- 💀 DLQ messages for permanently failed orders (IDs: 15, 30)

### In Producer Terminal:
- 📦 Generated orders with random products and prices
- ✅ Delivery confirmations

### Expected Behavior:
- **20 orders** will be produced
- **~18 orders** will be successfully processed
- **~2-4 orders** will trigger retry logic
- **~1-2 orders** will go to DLQ

---

## 🧪 Test Scenarios

### 1. Retry Logic Test
Orders with IDs ending in 3 or 7 will fail initially:
- Watch for "⚠️ Processing failed"
- Then "🔄 Retry 1/3"
- Finally "✅ Processed" (after retry succeeds)

### 2. DLQ Test
Orders divisible by 15 will permanently fail:
- Watch for "🚫 Max retries exceeded"
- Then "💀 Sent to DLQ"
- Run `dlq_monitor.py` to see these messages

### 3. Running Average Test
Watch the running average change with each order:
```
✅ Processed Order #1 - Price: $1245.67 | Running Avg: $1245.67
✅ Processed Order #2 - Price: $25.99 | Running Avg: $635.83
✅ Processed Order #3 - Price: $89.50 | Running Avg: $453.72
```

---

## 🐛 Troubleshooting

### Problem: "Docker is not running"
**Solution:** Start Docker Desktop and wait for it to fully start.

### Problem: Import errors
**Solution:** 
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problem: Connection refused
**Solution:** 
```powershell
docker-compose down
docker-compose up -d
# Wait 30 seconds
docker-compose ps
```

### Problem: Schema Registry errors
**Solution:**
```powershell
# Check if Schema Registry is healthy
docker-compose logs schema-registry
# Restart if needed
docker-compose restart schema-registry
```

---

## 🛑 Stop Everything

```powershell
# Stop consumer (Ctrl+C in consumer terminal)
# Stop producer (Ctrl+C in producer terminal)
# Stop Kafka infrastructure
docker-compose down -v
```

---

## 📊 View Kafka Topics

### List all topics:
```powershell
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list
```

### View messages in orders topic:
```powershell
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders --from-beginning
```

### View messages in DLQ:
```powershell
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic orders-dlq --from-beginning
```

---

## ✅ Verification Checklist

Before your demo, verify:
- [ ] Docker Desktop is running
- [ ] All 3 containers are up: `docker-compose ps`
- [ ] Consumer is listening (shows "🎧 Listening...")
- [ ] Producer sends messages (shows "✅ Message delivered")
- [ ] Running average is calculated correctly
- [ ] Retry logic works (watch for orders 3, 7, 13, etc.)
- [ ] DLQ receives failed messages (order 15)

---

## 🎬 Demo Script

1. **Show Infrastructure**
   ```powershell
   docker-compose ps
   ```

2. **Start Consumer** (explain what it does)
   ```powershell
   python consumer.py
   ```

3. **Start Producer** (in new terminal)
   ```powershell
   python producer.py
   ```

4. **Point out key features** as they happen:
   - Real-time processing
   - Running average calculation
   - Retry attempts
   - DLQ routing

5. **Show DLQ Monitor** (in new terminal)
   ```powershell
   python dlq_monitor.py
   ```

6. **Show Final Statistics** in consumer terminal

---

Good luck with your assignment! 🎓
