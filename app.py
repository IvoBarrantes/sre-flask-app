from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps
import time
import random

app = Flask(__name__)

# ----------------- Prometheus Metrics -----------------

# Total HTTP requests by method + endpoint
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint"]
)

# Latency of HTTP requests per endpoint
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"]
)

# Total number of created orders (business metric)
ORDERS_CREATED_TOTAL = Counter(
    "orders_created_total",
    "Total number of created orders"
)

# Total number of error responses (5xx) per endpoint
HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Total number of HTTP 5xx errors",
    ["endpoint"]
)

# ----------------- In-memory 'database' -----------------

orders_db = {
    "total_orders": 0,
    "orders": []  # list of simple order dicts
}

# ----------------- Decorator for common metrics -----------------

def track_request(endpoint_name: str):
    """
    Decorator that:
    - measures request latency
    - counts total requests
    - counts errors (5xx)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            response = func(*args, **kwargs)

            # Determine HTTP status code
            if isinstance(response, tuple):
                # (data, status_code) or (data, status_code, headers)
                status_code = response[1]
            else:
                # Flask Response object
                status_code = getattr(response, "status_code", 200)

            duration = time.time() - start

            # Record latency
            HTTP_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint_name).observe(duration)

            # Count the request
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint_name
            ).inc()

            # Count errors (5xx)
            if status_code >= 500:
                HTTP_ERRORS_TOTAL.labels(endpoint=endpoint_name).inc()

            return response
        return wrapper
    return decorator

# ----------------- Endpoints -----------------

@app.route("/", methods=["GET"])
@track_request("/")
def home():
    return jsonify({"message": "Hello from Ivone's SRE Flask app!"}), 200


@app.route("/health", methods=["GET"])
@track_request("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/order", methods=["POST"])
@track_request("/order")
def create_order():
    """
    Creates a fake order.
    Body example: { "item": "pizza", "quantity": 2 }
    """
    data = request.get_json() or {}
    item = data.get("item", "unknown-item")
    quantity = int(data.get("quantity", 1))

    # Simulate processing time (like calling a DB or external API)
    time.sleep(random.uniform(0.05, 0.3))

    orders_db["total_orders"] += 1
    order_id = orders_db["total_orders"]

    order = {
        "id": order_id,
        "item": item,
        "quantity": quantity
    }
    orders_db["orders"].append(order)

    # Business metric
    ORDERS_CREATED_TOTAL.inc()

    return jsonify({
        "message": "order created",
        "order": order
    }), 201


@app.route("/orders", methods=["GET"])
@track_request("/orders")
def list_orders():
    """
    Returns the total number of orders and the list of orders.
    In a real app you'd paginate; here it's just for demo.
    """
    return jsonify({
        "total_orders": orders_db["total_orders"],
        "orders": orders_db["orders"]
    }), 200


@app.route("/sometimes-slow", methods=["GET"])
@track_request("/sometimes-slow")
def sometimes_slow():
    """
    30% of the time, this endpoint will sleep for 2 seconds.
    Great for testing latency alerts and graphs.
    """
    if random.random() < 0.3:
        time.sleep(2)

    return jsonify({"message": "sometimes I am slow"}), 200


@app.route("/always-error", methods=["GET"])
@track_request("/always-error")
def always_error():
    """
    Always returns an error (500).
    Great for testing error-rate alerts.
    """
    return jsonify({"error": "This endpoint always fails"}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    """
    Prometheus will scrape this.
    We intentionally do NOT decorate it with @track_request
    so we don't count scrapes as user traffic.
    """
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    # Using port 5001 as you selected earlier
    app.run(host="0.0.0.0", port=5001, debug=True)
