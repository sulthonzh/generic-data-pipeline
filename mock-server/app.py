import os
import orjson
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')

FIRST_NAMES = ['James', 'Sarah', 'Michael', 'Emma', 'David', 'Lisa', 'Robert', 'Jennifer', 'William', 'Emily']
LAST_NAMES = ['Anderson', 'Mitchell', 'Thompson', 'Wilson', 'Garcia', 'Martinez', 'Davis', 'Rodriguez', 'Taylor', 'Moore']
CITIES = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
STATES = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA']


def load_customers():
    try:
        with open(DATA_FILE, 'rb') as f:
            return orjson.loads(f.read())
    except FileNotFoundError:
        return []
    except Exception:
        return []


def generate_customer(i: int) -> dict:
    return {
        "customer_id": f"CUST{i:07d}",
        "first_name": FIRST_NAMES[i % len(FIRST_NAMES)],
        "last_name": LAST_NAMES[i % len(LAST_NAMES)],
        "email": f"customer{i}@example.com",
        "phone": f"1-555-{i:07d}",
        "address": f"{i % 9999} {STREETS[i % len(STREETS)]}, {CITIES[i % len(CITIES)]}, {STATES[i % len(STATES)]} {i % 99999:05d}",
        "date_of_birth": f"{1970 + (i % 40):04d}-{1 + (i % 12):02d}-{1 + (i % 28):02d}",
        "account_balance": 1000.0 + (i % 50000) + (i % 100) / 100,
        "created_at": datetime.now(timezone.utc).isoformat()
    }


STREETS = ['Main Street', 'Oak Avenue', 'Pine Road', 'Maple Drive', 'Cedar Lane', 'Elm Boulevard', 'Washington Street', 'Lake View Drive']


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'flask-mock-server',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = load_customers()

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100

    total = len(customers)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    paginated_customers = customers[start_idx:end_idx]

    return jsonify({
        'data': paginated_customers,
        'total': total,
        'page': page,
        'limit': limit,
        'has_next': end_idx < total,
        'has_prev': page > 1
    }), 200


@app.route('/api/customers/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customers = load_customers()

    customer = next((c for c in customers if c.get('customer_id') == customer_id), None)

    if not customer:
        return jsonify({
            'error': 'Customer not found',
            'customer_id': customer_id
        }), 404

    return jsonify({'data': customer}), 200


@app.route('/api/customers/all', methods=['GET'])
def get_all_customers():
    customers = load_customers()

    json_data = orjson.dumps({
        'data': customers,
        'total': len(customers)
    })

    return Response(json_data, mimetype='application/json'), 200


@app.route('/api/customers/large', methods=['GET'])
def get_large_dataset():
    size = min(int(request.args.get('size', 100000)), 10000000)
    batch_size = int(request.args.get('batch', 10000))
    page = int(request.args.get('page', 1))

    start_time = time.time()

    start_idx = (page - 1) * batch_size
    end_idx = min(start_idx + batch_size, size)

    customers = [generate_customer(start_idx + i) for i in range(end_idx - start_idx)]

    generation_time = time.time() - start_time

    json_data = orjson.dumps({
        'data': customers,
        'total': size,
        'page': page,
        'batch_size': batch_size,
        'has_more': end_idx < size,
        'performance': {
            'records_generated': len(customers),
            'generation_time_ms': round(generation_time * 1000, 2),
            'records_per_second': round(len(customers) / generation_time) if generation_time > 0 else 0
        }
    })

    return Response(json_data, mimetype='application/json'), 200


@app.route('/api/customers/stream', methods=['GET'])
def stream_large_dataset():
    size = min(int(request.args.get('size', 100000)), 1000000)

    def generate():
        yield b'{"data":['

        for i in range(size):
            if i > 0:
                yield b','
            customer = generate_customer(i)
            yield orjson.dumps(customer)

        yield b'],"total":' + orjson.dumps(size) + b'}'

    return Response(stream_with_context(generate()), mimetype='application/json'), 200


@app.route('/api/performance/test', methods=['GET'])
def performance_test():
    size = int(request.args.get('size', 10000))

    start = time.time()

    customers = [generate_customer(i) for i in range(size)]

    gen_time = time.time() - start

    start = time.time()
    json_bytes = orjson.dumps({'data': customers, 'total': size})
    serialize_time = time.time() - start

    return jsonify({
        'test': 'orjson + generation performance',
        'records': size,
        'results': {
            'generation_time_ms': round(gen_time * 1000, 2),
            'serialize_time_ms': round(serialize_time * 1000, 2),
            'total_time_ms': round((gen_time + serialize_time) * 1000, 2),
            'records_per_second': round(size / (gen_time + serialize_time)),
            'json_size_mb': round(len(json_bytes) / (1024 * 1024), 2)
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested URL was not found on the server'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
