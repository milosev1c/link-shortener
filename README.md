# link-shortener

Async URL shortener API built with FastAPI. Supports Redis and PostgreSQL storage backends.

## Requirements

- Python 3.13+
- Docker (optional, for deployment)

## Setup

```bash
pip install -e ".[dev]"
```

## Run locally

```bash
# Redis backend (requires a running Redis instance)
STORAGE_BACKEND=redis REDIS_URL=redis://localhost:6379/0 link-shortener

# PostgreSQL backend
STORAGE_BACKEND=postgres POSTGRES_DSN=postgresql://postgres:postgres@localhost:5432/link_shortener link-shortener
```

## Tests

```bash
pytest
```

## API

```bash
# Shorten a URL (201 Created)
curl -i -X POST http://localhost:8000/links/shorten \
  -H 'Content-Type: application/json' \
  -d '{"long_url": "https://www.example.org"}'

# Shorten again (200 OK, same short_url)
curl -i -X POST http://localhost:8000/links/shorten \
  -H 'Content-Type: application/json' \
  -d '{"long_url": "https://www.example.org"}'

# Redirect (307 Temporary Redirect)
curl -i http://localhost:8000/u/<short_id>
```

## Docker

```bash
# Redis variant
docker compose -f docker-compose.redis.yml up --build

# PostgreSQL variant
docker compose -f docker-compose.postgres.yml up --build
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `STORAGE_BACKEND` | `redis` | `redis` or `postgres` |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `POSTGRES_DSN` | `postgresql://postgres:postgres@localhost:5432/link_shortener` | PostgreSQL DSN |
| `BASE_URL` | `http://localhost:8000` | Prefix for generated short URLs |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8000` | Server bind port |
| `SHORT_ID_LENGTH` | `8` | Length of generated short ids |

## AI usage

This project was built with assistance from Cursor (AI coding agent). AI was used to:

- Draft the initial architecture and implementation plan (layered API, pluggable storage, Docker deployment).
- Implement the application code, tests, and deployment configs in incremental commits.
- Refine design decisions during review (HTTP status codes, URL deduplication, documentation style).

All generated code was reviewed and verified locally (`pytest`, Docker build, compose smoke tests) before committing.
