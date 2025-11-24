/* ============================================================================
   DASHBOARD JAVASCRIPT - REAL-TIME UPDATES
   ============================================================================ */

// Initialize Socket.IO connection with proper settings
const socket = io({
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity,
    transports: ['websocket', 'polling']
});

// Chart instances
let productChart = null;

// Connection status
let isConnected = false;

/* ============================================================================
   SOCKET.IO EVENT HANDLERS
   ============================================================================ */

socket.on('connect', () => {
    console.log('✅ Connected to dashboard server');
    isConnected = true;
    updateConnectionStatus(true);
    
    // Request initial data
    fetchMetrics();
    fetchOrders();
    fetchDLQ();
    fetchProducts();
});

socket.on('disconnect', () => {
    console.log('⚠️  Disconnected from dashboard server');
    isConnected = false;
    updateConnectionStatus(false);
});

socket.on('metrics_update', (data) => {
    console.log('📊 Metrics update received:', data);
    updateDashboard(data);
});

socket.on('connection_response', (data) => {
    console.log('✅ Server response:', data.data);
});

socket.on('error', (error) => {
    console.error('Socket error:', error);
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
});


/* ============================================================================
   API FUNCTIONS
   ============================================================================ */

/**
 * Fetch metrics from the API
 */
async function fetchMetrics() {
    try {
        const response = await fetch('/api/metrics');
        if (!response.ok) {
            console.error('API error:', response.status);
            return;
        }
        const data = await response.json();
        if (data.error) {
            console.error('Error from API:', data.error);
            return;
        }
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching metrics:', error);
    }
}

/**
 * Fetch recent orders from the API
 */
async function fetchOrders() {
    try {
        const response = await fetch('/api/orders');
        if (!response.ok) {
            console.error('Orders API error:', response.status);
            return;
        }
        const data = await response.json();
        if (data.error) {
            console.error('Error from API:', data.error);
            return;
        }
        updateOrdersTable(data.orders || []);
    } catch (error) {
        console.error('Error fetching orders:', error);
    }
}

/**
 * Fetch DLQ messages from the API
 */
async function fetchDLQ() {
    try {
        const response = await fetch('/api/dlq');
        if (!response.ok) {
            console.error('DLQ API error:', response.status);
            return;
        }
        const data = await response.json();
        if (data.error) {
            console.error('Error from API:', data.error);
            return;
        }
        updateDLQTable(data.dlq_messages || []);
    } catch (error) {
        console.error('Error fetching DLQ:', error);
    }
}

/**
 * Fetch product statistics from the API
 */
async function fetchProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) {
            console.error('Products API error:', response.status);
            return;
        }
        const data = await response.json();
        if (data.error) {
            console.error('Error from API:', data.error);
            return;
        }
        updateProductChart(data.products || []);
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

/* ============================================================================
   UPDATE FUNCTIONS
   ============================================================================ */

/**
 * Update all dashboard metrics
 */
function updateDashboard(metrics) {
    // Update stat cards
    updateElement('total-orders', metrics.total_orders || 0);
    updateElement('total-revenue', `$${(metrics.total_revenue || 0).toFixed(2)}`);
    updateElement('avg-price', `$${(metrics.running_average || 0).toFixed(2)}`);
    updateElement('error-rate', `${(metrics.error_rate || 0).toFixed(1)}%`);
    updateElement('dlq-count', metrics.dlq_count || 0);
    updateElement('processing-rate', `${metrics.processing_rate || 0}/min`);

    // Update live metrics
    updateElement('processed-count', metrics.total_orders || 0);
    updateElement('dlq-live-count', metrics.dlq_count || 0);
    updateElement('kafka-status', metrics.status === 'connected' ? '🟢 Connected' : '🔴 Disconnected');

    // Update last update time
    if (metrics.last_update) {
        const time = new Date(metrics.last_update).toLocaleTimeString();
        updateElement('last-update', `Last update: ${time}`);
    }

    // Update connection status
    updateConnectionStatus(metrics.status === 'connected');

    // Update connection status indicator
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    if (metrics.status === 'connected') {
        statusIndicator.className = 'status-badge status-connected';
        statusText.textContent = 'Connected';
    } else {
        statusIndicator.className = 'status-badge status-disconnected';
        statusText.textContent = 'Disconnected';
    }

    // Update recent orders if provided
    if (metrics.recent_orders) {
        updateOrdersTable(metrics.recent_orders);
    }

    // Fetch additional data
    fetchProducts();
    fetchDLQ();
}

/**
 * Update element text content
 */
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        const oldValue = element.textContent;
        element.textContent = value;
        
        // Add animation effect if value changed
        if (oldValue !== String(value)) {
            element.classList.add('updated');
            setTimeout(() => element.classList.remove('updated'), 300);
        }
    }
}

/**
 * Update connection status
 */
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (!statusIndicator || !statusText) return;
    
    if (connected) {
        statusIndicator.className = 'status-badge status-connected';
        statusText.textContent = 'Connected';
        console.log('✅ Status updated to Connected');
    } else {
        statusIndicator.className = 'status-badge status-disconnected';
        statusText.textContent = 'Disconnected';
        console.log('❌ Status updated to Disconnected');
    }
}

/**
 * Update orders table
 */
function updateOrdersTable(orders) {
    const tbody = document.getElementById('orders-tbody');
    
    if (!orders || orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No orders yet...</td></tr>';
        return;
    }

    let html = '';
    orders.forEach(order => {
        const time = new Date(order.timestamp).toLocaleTimeString();
        html += `
            <tr>
                <td><strong>${order.id}</strong></td>
                <td>${order.product}</td>
                <td>$${parseFloat(order.price).toFixed(2)}</td>
                <td>${time}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

/**
 * Update DLQ table
 */
function updateDLQTable(dlqOrders) {
    const tbody = document.getElementById('dlq-tbody');
    
    if (!dlqOrders || dlqOrders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No failed orders yet...</td></tr>';
        return;
    }

    let html = '';
    dlqOrders.forEach(order => {
        const time = new Date(order.timestamp).toLocaleTimeString();
        html += `
            <tr>
                <td><strong>${order.id}</strong></td>
                <td>${order.product}</td>
                <td>$${parseFloat(order.price).toFixed(2)}</td>
                <td>${time}</td>
                <td><span class="status-badge status-failed">❌ Failed</span></td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

/**
 * Update product chart
 */
function updateProductChart(products) {
    const ctx = document.getElementById('productChart').getContext('2d');

    if (!products || products.length === 0) {
        products = [];
    }

    const labels = products.map(p => p.name);
    const data = products.map(p => p.count);
    const colors = [
        '#3498db',
        '#27ae60',
        '#f39c12',
        '#e74c3c',
        '#2980b9',
        '#16a085',
        '#8e44ad',
        '#d35400',
        '#c0392b',
        '#2c3e50'
    ];

    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Orders',
            data: data,
            backgroundColor: colors.slice(0, labels.length),
            borderColor: '#fff',
            borderWidth: 2
        }]
    };

    // Destroy old chart if exists
    if (productChart) {
        productChart.destroy();
    }

    // Create new chart
    productChart = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/* ============================================================================
   INITIALIZATION
   ============================================================================ */

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('📊 Initializing dashboard...');

    // Add update animation styles
    const style = document.createElement('style');
    style.textContent = `
        .updated {
            animation: updateFlash 0.3s ease-out;
        }
        @keyframes updateFlash {
            0% {
                background-color: rgba(52, 152, 219, 0.3);
                transform: scale(1.05);
            }
            100% {
                background-color: transparent;
                transform: scale(1);
            }
        }
    `;
    document.head.appendChild(style);

    // Initial data fetch
    console.log('📡 Fetching initial data...');
    fetchMetrics();
    fetchOrders();
    fetchDLQ();
    fetchProducts();

    // Refresh metrics every 1 second (faster updates)
    setInterval(() => {
        console.log('🔄 Polling metrics...');
        fetchMetrics();
        fetchOrders();
    }, 1000);

    // Refresh product stats every 3 seconds
    setInterval(() => {
        console.log('📊 Updating product chart...');
        fetchProducts();
    }, 3000);

    // Refresh DLQ every 2 seconds
    setInterval(() => {
        console.log('💀 Checking DLQ...');
        fetchDLQ();
    }, 2000);

    console.log('✅ Dashboard initialized with polling');
});

/* ============================================================================
   ERROR HANDLING
   ============================================================================ */

window.addEventListener('error', (event) => {
    console.error('Dashboard error:', event.error);
});

socket.on('error', (error) => {
    console.error('Socket error:', error);
});
