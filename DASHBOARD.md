# Dashboard Setup & Usage Guide

## 🎨 Dashboard Features

Your Kafka Avro assignment now includes a **professional web dashboard** with:

✅ **Real-time Metrics**
- Total orders processed
- Total revenue
- Average order price
- Error rate percentage
- DLQ message count
- Processing rate (orders/min)

✅ **Live Charts**
- Product distribution (doughnut chart)
- Real-time metrics display
- Auto-updating statistics

✅ **Data Tables**
- Recent orders (last 20)
- Dead Letter Queue messages
- Timestamps for tracking
- Live updates every 2-3 seconds

✅ **Connection Status**
- Real-time Kafka connection indicator
- Last update timestamp
- Processing statistics

✅ **Professional UI/UX**
- Modern gradient header
- Responsive design (mobile-friendly)
- Smooth animations
- Color-coded status indicators
- Clean, intuitive layout

---

## 🚀 Quick Start

### Step 1: Install Dashboard Dependencies

```powershell
pip install -r requirements.txt
```

This installs Flask, Socket.IO, and other required packages.

### Step 2: Start Kafka Infrastructure

```powershell
docker-compose up -d
```

Wait 30-40 seconds for containers to start.

### Step 3: Start Consumer (Terminal 1)

```powershell
python consumer.py
```

Keep this running - it processes messages from Kafka.

### Step 4: Start Dashboard Server (Terminal 2)

```powershell
python app.py
```

You'll see:
```
========================================================================
KAFKA MONITORING DASHBOARD API
========================================================================
📊 Dashboard running on http://localhost:5000
🔌 WebSocket server for real-time updates
========================================================================
```

### Step 5: Open Dashboard in Browser

Open your browser and go to:
```
http://localhost:5000
```

You should see the beautiful dashboard! 🎨

### Step 6: Start Producer (Terminal 3)

```powershell
python producer.py
```

Watch the dashboard update in real-time as orders are processed! 📊

---

## 📊 Dashboard Components Explained

### Top Stats Cards (6 Cards)
- **📦 Total Orders**: Count of all processed orders
- **💰 Total Revenue**: Sum of all order prices
- **📈 Average Price**: Running average of prices
- **⚠️ Error Rate**: Percentage of failed orders
- **💀 DLQ Messages**: Count of permanently failed messages
- **⚡ Processing Rate**: Orders processed per minute

### Charts Section
- **📊 Orders by Product**: Doughnut chart showing product distribution
- **📱 Real-time Metrics**: Live statistics and status display

### Data Tables
- **Recent Orders**: Last 20 processed orders with details
- **DLQ (Dead Letter Queue)**: Failed messages that couldn't be processed

---

## 🔌 Architecture

```
┌─────────────────┐
│   Kafka Broker  │
└────────┬────────┘
         │
    ┌────┴─────────────┬───────────────┐
    │                  │               │
┌───▼──────┐  ┌────────▼──────┐  ┌───▼─────────┐
│ Producer │  │   Consumer    │  │  DLQ Topic  │
│ (orders) │  │ (processes)   │  │  (failed)   │
└──────────┘  └────────┬──────┘  └───┬─────────┘
                       │              │
                  ┌────┴──────────────┘
                  │
          ┌───────▼────────┐
          │   Flask API    │
          │    (app.py)    │
          └────────┬───────┘
                   │
         ┌─────────┴──────────┐
         │                    │
    ┌────▼───────────┐  ┌────▼──────────┐
    │  REST API      │  │  WebSocket    │
    │  (/api/*)      │  │  Real-time    │
    └────────────────┘  └────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Web Dashboard     │
                    │  (HTML/CSS/JS)     │
                    │  http://localhost  │
                    │      :5000         │
                    └────────────────────┘
```

---

## 📡 API Endpoints

The dashboard uses these REST API endpoints:

### GET `/api/metrics`
Returns current metrics:
```json
{
  "total_orders": 50,
  "total_revenue": 2500.00,
  "running_average": 50.00,
  "status": "connected",
  "error_rate": 5.2,
  "dlq_count": 2,
  "processing_rate": 10
}
```

### GET `/api/orders`
Returns recent processed orders:
```json
{
  "orders": [
    {
      "id": "1",
      "product": "Laptop",
      "price": 1250.50,
      "timestamp": "2025-11-24T14:30:00"
    }
  ]
}
```

### GET `/api/dlq`
Returns DLQ messages:
```json
{
  "dlq_messages": [
    {
      "id": "15",
      "product": "Monitor",
      "price": 299.99,
      "timestamp": "2025-11-24T14:31:00"
    }
  ]
}
```

### GET `/api/products`
Returns product statistics:
```json
{
  "products": [
    {
      "name": "Laptop",
      "count": 10,
      "percentage": 20.0
    }
  ]
}
```

---

## 🔄 Real-time Updates

The dashboard uses **WebSocket (Socket.IO)** for real-time updates:

**Connection**: Automatic WebSocket connection to Flask server
**Update Frequency**:
- Metrics: Every 2 seconds
- Charts: Every 5 seconds
- DLQ: Every 3 seconds

**Live Features**:
- Stat values update with animation
- Tables refresh with new data
- Charts recalculate automatically
- Status indicator shows connection

---

## 🎨 UI/UX Features

### Professional Design
- Modern gradient header
- Clean card-based layout
- Color-coded status badges
- Smooth hover effects

### Responsive Design
- Works on desktop, tablet, mobile
- Responsive grid layout
- Mobile-optimized tables
- Touch-friendly buttons

### Accessibility
- Clear color contrast
- Readable font sizes
- Logical information hierarchy
- Semantic HTML

### Performance
- Efficient DOM updates
- Optimized chart rendering
- Minimal network traffic
- Fast page load

---

## 🐛 Troubleshooting

### Dashboard won't load
```powershell
# 1. Check if Flask server is running
# Should show: 📊 Dashboard running on http://localhost:5000

# 2. Check if port 5000 is available
netstat -ano | findstr :5000

# 3. Kill process on port 5000 if needed
netstat -ano | findstr :5000 | findstr LISTENING
taskkill /PID <PID> /F

# 4. Restart Flask
python app.py
```

### Real-time updates not working
```powershell
# 1. Check Kafka is running
docker ps | findstr kafka

# 2. Verify consumer is running
# Should show: 🎧 Listening for orders

# 3. Check browser console for errors (F12)
```

### No data showing
```powershell
# 1. Start producer to generate orders
python producer.py

# 2. Wait 2-3 seconds for data to appear
# 3. Check Flask logs for errors
```

---

## 📈 Demo Workflow

1. **Show Dashboard** (http://localhost:5000)
   - Display clean, professional interface
   - Show all stat cards at 0

2. **Start Producer**
   - Orders start appearing in tables
   - Stat cards update in real-time
   - Product chart populates

3. **Show Real-time Processing**
   - Point out running average updating
   - Show processing rate increasing
   - Highlight error rate (some orders fail)

4. **Show DLQ**
   - Failed orders appear in DLQ table
   - Count increases
   - Error rate updates

5. **Show Charts**
   - Product distribution chart updates
   - Real-time metrics widget
   - All data live-synced

---

## 📊 Performance Metrics

The dashboard tracks:
- **Total Orders**: Cumulative count
- **Total Revenue**: Sum of all prices
- **Running Average**: Mean price (updated per order)
- **Processing Rate**: Orders/minute
- **Error Rate**: Failed orders percentage
- **DLQ Count**: Permanently failed messages

---

## 🎓 Assignment Completeness

✅ **Kafka System**: Producer, Consumer, DLQ
✅ **Avro Serialization**: Full Avro implementation
✅ **Real-time Aggregation**: Running average calculated live
✅ **Retry Logic**: 3 retries with 2-second delay
✅ **Dead Letter Queue**: Separate DLQ topic
✅ **Web Dashboard**: Professional UI with real-time updates
✅ **API**: REST API + WebSocket
✅ **Responsive**: Mobile-friendly design

---

## 🚀 Final Tips for Demo

1. **Have all terminals ready** before demo starts
2. **Open dashboard first** so it loads while Kafka starts
3. **Show metrics building** as producer runs
4. **Point out animations** on stat updates
5. **Highlight error handling** with DLQ
6. **Show mobile responsiveness** on different screen sizes
7. **Keep everything running** to show stability

---

Enjoy your professional Kafka dashboard! 🎉
