"""
Flask API Server for Kafka Monitoring Dashboard
Provides real-time metrics and statistics
"""

from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
import json
import traceback
import os
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import config

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

print(f"📁 Template directory: {TEMPLATE_DIR}")
print(f"📁 Static directory: {STATIC_DIR}")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global metrics state
metrics = {
    'total_orders': 0,
    'total_revenue': 0.0,
    'running_average': 0.0,
    'orders_by_product': {},
    'processed_orders': [],
    'failed_orders': [],
    'dlq_orders': [],
    'retry_attempts': 0,
    'status': 'disconnected',
    'last_update': None,
    'processing_rate': 0,
    'error_rate': 0
}

# Thread-safe metrics lock
metrics_lock = threading.Lock()

class MetricsCollector:
    """Collects metrics from Kafka without blocking"""
    
    def __init__(self):
        self.consumer = None
        self.dlq_consumer = None
        self.avro_deserializer = None
        self.schema_registry_client = None
        self.initialized = False
        self.last_process_time = time.time()
        self.orders_in_last_minute = 0
    
    def initialize(self):
        """Initialize Kafka connection - called on first use"""
        if self.initialized:
            return True
        
        try:
            print("🔧 Initializing Kafka connection...")
            
            # Load Avro Schema
            with open('schemas/order.avsc', 'r') as f:
                schema_str = f.read()
            
            # Schema Registry Client
            schema_registry_conf = {'url': config.SCHEMA_REGISTRY_URL}
            self.schema_registry_client = SchemaRegistryClient(schema_registry_conf)
            print("✅ Schema Registry connected")
            
            # Avro Deserializer
            self.avro_deserializer = AvroDeserializer(
                self.schema_registry_client,
                schema_str,
                lambda data, ctx: data
            )
            
            # Kafka Consumer for orders
            consumer_conf = {
                'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
                'group.id': 'dashboard-consumer-group',
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False,
                'session.timeout.ms': 6000,
                'api.version.request.timeout.ms': 10000
            }
            self.consumer = Consumer(consumer_conf)
            self.consumer.subscribe([config.ORDERS_TOPIC])
            print("✅ Orders consumer connected")
            
            # Kafka Consumer for DLQ
            dlq_consumer_conf = {
                'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
                'group.id': 'dlq-dashboard-group-' + str(int(time.time())),  # Unique group per session
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False,
                'session.timeout.ms': 6000,
                'api.version.request.timeout.ms': 10000
            }
            self.dlq_consumer = Consumer(dlq_consumer_conf)
            self.dlq_consumer.subscribe([config.DLQ_TOPIC])
            print("✅ DLQ consumer connected")
            
            self.initialized = True
            with metrics_lock:
                metrics['status'] = 'connected'
            print("✅ Kafka connection initialized successfully")
            return True
            
        except Exception as e:
            print(f"⚠️  Kafka initialization error: {e}")
            print(traceback.format_exc())
            return False
    
    def collect_metrics(self):
        """Collect metrics from Kafka topics"""
        if not self.initialized:
            return
        
        try:
            # Collect from orders topic
            msg = self.consumer.poll(timeout=0.05)
            if msg and not msg.error():
                try:
                    serialization_context = SerializationContext(
                        config.ORDERS_TOPIC,
                        MessageField.VALUE
                    )
                    order = self.avro_deserializer(msg.value(), serialization_context)
                    
                    with metrics_lock:
                        metrics['total_orders'] += 1
                        metrics['total_revenue'] += float(order['price'])
                        metrics['running_average'] = metrics['total_revenue'] / metrics['total_orders']
                        
                        # Track by product
                        product = order['product']
                        if product not in metrics['orders_by_product']:
                            metrics['orders_by_product'][product] = 0
                        metrics['orders_by_product'][product] += 1
                        
                        # Add to processed orders
                        order_record = {
                            'id': str(order['orderId']),
                            'product': str(order['product']),
                            'price': float(order['price']),
                            'timestamp': datetime.now().isoformat()
                        }
                        metrics['processed_orders'].append(order_record)
                        if len(metrics['processed_orders']) > 100:
                            metrics['processed_orders'] = metrics['processed_orders'][-100:]
                        
                        metrics['status'] = 'connected'
                        metrics['last_update'] = datetime.now().isoformat()
                        self.orders_in_last_minute += 1
                        
                        # Log for debugging
                        print(f"✅ Collected Order #{order['orderId']} - Total: {metrics['total_orders']}")
                    
                    self.consumer.commit(msg)
                except Exception as e:
                    print(f"❌ Error processing order: {e}")
            
            # Collect from DLQ - poll multiple times to catch all messages
            for _ in range(5):
                dlq_msg = self.dlq_consumer.poll(timeout=0.1)
                if dlq_msg and not dlq_msg.error():
                    try:
                        serialization_context = SerializationContext(
                            config.DLQ_TOPIC,
                            MessageField.VALUE
                        )
                        dlq_order = self.avro_deserializer(dlq_msg.value(), serialization_context)
                        
                        with metrics_lock:
                            dlq_record = {
                                'id': str(dlq_order['orderId']),
                                'product': str(dlq_order['product']),
                                'price': float(dlq_order['price']),
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Check if this order is already in DLQ
                            existing = [d for d in metrics['dlq_orders'] if d['id'] == dlq_record['id']]
                            if not existing:
                                metrics['dlq_orders'].append(dlq_record)
                                if len(metrics['dlq_orders']) > 100:
                                    metrics['dlq_orders'] = metrics['dlq_orders'][-100:]
                                
                                print(f"💀 Collected DLQ Order #{dlq_order['orderId']} - DLQ Total: {len(metrics['dlq_orders'])}")
                        
                        self.dlq_consumer.commit(dlq_msg)
                    except Exception as e:
                        print(f"❌ Error processing DLQ message: {e}")
        
        except Exception as e:
            print(f"❌ Collection error: {e}")
    
    def calculate_rates(self):
        """Calculate processing rate (orders per minute)"""
        current_time = time.time()
        if current_time - self.last_process_time >= 60:
            with metrics_lock:
                metrics['processing_rate'] = self.orders_in_last_minute
                
                # Calculate error rate
                total = metrics['total_orders']
                if total > 0:
                    error_count = len(metrics['dlq_orders']) + len(metrics['failed_orders'])
                    metrics['error_rate'] = (error_count / total) * 100
            
            self.orders_in_last_minute = 0
            self.last_process_time = current_time


def metrics_collection_loop():
    """Background thread to collect metrics"""
    while True:
        try:
            collector.collect_metrics()
            collector.calculate_rates()
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Metrics collection error: {e}")
            time.sleep(1)  # Wait before retrying if error

# ============================================================================
# INITIALIZE COLLECTOR
# ============================================================================

print("\n" + "="*70)
print("KAFKA MONITORING DASHBOARD - STARTING")
print("="*70)

collector = MetricsCollector()

def metrics_collection_loop():
    """Background thread to collect metrics"""
    retry_count = 0
    while True:
        try:
            if not collector.initialized:
                if retry_count % 10 == 0:  # Log every 10 attempts
                    print(f"🔄 Attempting Kafka connection... (attempt {retry_count})")
                collector.initialize()
                if collector.initialized:
                    print("✅ Connected to Kafka!")
                retry_count += 1
            else:
                retry_count = 0  # Reset on success
                collector.collect_metrics()
                collector.calculate_rates()
            
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️  Metrics loop error: {e}")
            time.sleep(1)

# Start background thread
collector_thread = threading.Thread(target=metrics_collection_loop, daemon=True)
collector_thread.start()

print("✅ Metrics collector thread started")

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    try:
        print("🌐 Rendering dashboard HTML...")
        return render_template('dashboard.html')
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
        import traceback
        traceback.print_exc()
        # Return a simple HTML if template rendering fails
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Kafka Dashboard - Error Loading</title>
            <style>
                body {{ font-family: Arial; padding: 20px; }}
                .error {{ color: red; }}
                .info {{ color: blue; }}
            </style>
        </head>
        <body>
            <h1>⚠️ Dashboard Loading Error</h1>
            <p class="error">Error: {str(e)}</p>
            <p class="info">Trying to load: {TEMPLATE_DIR}/dashboard.html</p>
            <p>Check Flask terminal for more details.</p>
            <p><a href="javascript:location.reload()">Refresh Page</a></p>
        </body>
        </html>
        """, 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get current metrics"""
    try:
        with metrics_lock:
            data = {
                'total_orders': metrics['total_orders'],
                'total_revenue': round(metrics['total_revenue'], 2),
                'running_average': round(metrics['running_average'], 2),
                'orders_by_product': metrics['orders_by_product'],
                'status': metrics['status'],
                'last_update': metrics['last_update'],
                'processing_rate': metrics['processing_rate'],
                'error_rate': round(metrics['error_rate'], 2),
                'dlq_count': len(metrics['dlq_orders']),
                'failed_count': len(metrics['failed_orders'])
            }
        print(f"📊 Metrics API called - Orders: {data['total_orders']}, Revenue: ${data['total_revenue']}")
        return jsonify(data)
    except Exception as e:
        print(f"❌ Error in get_metrics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get recent processed orders"""
    try:
        with metrics_lock:
            orders = metrics['processed_orders'][-20:]
        print(f"📋 Orders API called - Returned {len(orders)} orders")
        return jsonify({'orders': orders})
    except Exception as e:
        print(f"❌ Error in get_orders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dlq', methods=['GET'])
def get_dlq():
    """Get DLQ messages"""
    try:
        with metrics_lock:
            dlq_msgs = metrics['dlq_orders'][-20:]
        print(f"💀 DLQ API called - Returned {len(dlq_msgs)} DLQ messages")
        return jsonify({'dlq_messages': dlq_msgs})
    except Exception as e:
        print(f"❌ Error in get_dlq: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get product statistics"""
    try:
        with metrics_lock:
            product_stats = []
            for product, count in metrics['orders_by_product'].items():
                product_stats.append({
                    'name': product,
                    'count': count,
                    'percentage': round((count / metrics['total_orders'] * 100), 1) if metrics['total_orders'] > 0 else 0
                })
            
            product_stats.sort(key=lambda x: x['count'], reverse=True)
        print(f"📊 Products API called - Returned {len(product_stats)} products")
        return jsonify({'products': product_stats})
    except Exception as e:
        print(f"❌ Error in get_products: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('✅ WebSocket client connected')
    emit('connection_response', {'data': 'Connected to dashboard'})
    
    # Send initial metrics
    with metrics_lock:
        emit('metrics_update', {
            'total_orders': metrics['total_orders'],
            'total_revenue': round(metrics['total_revenue'], 2),
            'running_average': round(metrics['running_average'], 2),
            'status': metrics['status'],
            'dlq_count': len(metrics['dlq_orders'])
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('❌ WebSocket client disconnected')

def emit_metrics_update():
    """Emit metrics to all connected clients"""
    try:
        with metrics_lock:
            socketio.emit('metrics_update', {
                'total_orders': metrics['total_orders'],
                'total_revenue': round(metrics['total_revenue'], 2),
                'running_average': round(metrics['running_average'], 2),
                'status': metrics['status'],
                'processing_rate': metrics['processing_rate'],
                'error_rate': round(metrics['error_rate'], 2),
                'dlq_count': len(metrics['dlq_orders']),
                'recent_orders': metrics['processed_orders'][-5:]
            }, to=None, namespace='/')
    except Exception as e:
        print(f"❌ Error emitting metrics: {e}")

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    print(f"❌ 404 Error: {error}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    print(f"❌ 500 Error: {error}")
    import traceback
    traceback.print_exc()
    return jsonify({'error': f'Server error: {str(error)}'}), 500

# Add request import at top if missing
from flask import request

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("📊 Dashboard running on http://localhost:5000")
    print("🔌 WebSocket server for real-time updates")
    print("="*70)
    print("\n✨ Waiting for Kafka connection...")
    print("   Consumer will connect when Kafka is ready\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
