# Customer Data Pipeline

Production-grade data pipeline with clean architecture, generic sources/sinks, and comprehensive testing.

## Quick Start

```bash
docker-compose up -d

curl http://localhost:5001/api/health
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/ingest
```

## Architecture

Clean architecture with separation of concerns:

```
pipeline-service/
├── config/
│   └── settings.py          # Pydantic settings
├── models/
│   ├── customer.py          # SQLAlchemy entity
│   └── schemas.py           # Pydantic schemas
├── repositories/
│   ├── base.py              # Generic repository
│   └── customer.py          # Customer repository
├── sources/
│   ├── base.py              # Abstract source
│   └── http_source.py       # HTTP source
├── sinks/
│   ├── base.py              # Abstract sink
│   └── postgres_sink.py     # PostgreSQL sink
├── services/
│   ├── pipeline.py          # Orchestrator
│   └── ingestion.py         # Ingestion service
├── database.py              # Connection management
└── main.py                  # FastAPI app
```

## Configuration

Environment variables (`.env`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=customer_db
DATABASE_URL=postgresql://postgres:password@postgres:5432/customer_db

MOCK_SERVER_URL=http://mock-server:5000
BATCH_SIZE=1000
TIMEOUT=60.0

WORKERS=4
LOG_LEVEL=INFO
```

## API Endpoints

### Flask Mock Server (localhost:5001)

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/customers?page=1&limit=10` | Paginated customers |
| `GET /api/customers/{id}` | Single customer |
| `GET /api/customers/all` | All customers (for ingestion) |

### FastAPI Pipeline Service (localhost:8000)

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `POST /api/ingest` | Ingest data from mock server |
| `GET /api/customers?page=1&limit=10` | Paginated customers from DB |
| `GET /api/customers/{id}` | Single customer from DB |

## Testing

```bash
# Unit tests
docker-compose exec pipeline-service pytest tests/test_unit/ -v

# Integration tests
docker-compose exec pipeline-service pytest tests/test_integration/ -v

# E2E tests
pytest tests/test_e2e/ -v -m e2e

# All tests with coverage
docker-compose exec pipeline-service pytest tests/ -v --cov=. --cov-report=html
```

## Features

- **Generic Pipeline**: Easy to add new sources/sinks
- **Repository Pattern**: Base repository with generics
- **Service Layer**: Business logic separated from API
- **Orchestrator**: Pipeline execution with validation
- **Pydantic Settings**: Type-safe configuration
- **Production Server**: Gunicorn + Uvicorn workers
- **orjson**: Fast JSON serialization
- **Polars**: Efficient DataFrame operations

## Database Schema

```sql
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    account_balance DECIMAL(15,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Production Deployment

The pipeline service uses Gunicorn with Uvicorn workers:

```bash
gunicorn main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120
```

## Cleanup

```bash
docker-compose down
docker-compose down -v  # removes data
```
