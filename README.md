# link-shortener

Async URL shortener API built with FastAPI. Supports Redis and PostgreSQL storage backends.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (dependency management)
- Docker (optional, for deployment)

## Setup

```bash
uv sync --extra dev
```

Settings can be loaded from a `.env` file in the project root.

## Run locally

```bash
# Redis backend (requires a running Redis instance)
STORAGE_BACKEND=redis REDIS_URL=redis://localhost:6379/0 uv run link-shortener

# PostgreSQL backend
STORAGE_BACKEND=postgres POSTGRES_DSN=postgresql://postgres:postgres@localhost:5432/link_shortener uv run link-shortener
```

## Tests

```bash
uv run pytest
```

## API

```bash
# Health check (200 OK, or 503 if storage is unavailable)
curl -i http://localhost:8000/health

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

Images are built from `uv.lock` for reproducible dependency versions. Compose stacks include healthchecks for the app (`GET /health`) and the storage backend.

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
| `POSTGRES_POOL_MIN_SIZE` | `2` | PostgreSQL connection pool minimum size |
| `POSTGRES_POOL_MAX_SIZE` | `10` | PostgreSQL connection pool maximum size |
| `BASE_URL` | `http://localhost:8000` | Prefix for generated short URLs |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8000` | Server bind port |
| `SHORT_ID_LENGTH` | `8` | Length of generated short ids |

## Logging

Application logs use the `link_shortener` logger. DEBUG and INFO go to stdout; WARNING and above go to stderr.

## AI usage

This project was built with assistance from Cursor (AI coding agent). AI was used to:

- Draft the initial architecture and implementation plan (layered API, pluggable storage, Docker deployment).
- Implement the application code, tests, and deployment configs in incremental commits.
- Refine design decisions during review (HTTP status codes, URL deduplication, documentation style).

All generated code was reviewed and verified locally (`uv run pytest`, Docker build, compose smoke tests) before committing.
