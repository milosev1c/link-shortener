from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_exists():
    assert (ROOT / "Dockerfile").is_file()


def test_dockerfile_uses_uv_lock():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "uv.lock" in dockerfile
    assert "uv sync --frozen" in dockerfile
    assert 'python", "-m", "uvicorn"' in dockerfile


def _assert_app_healthcheck(compose: dict) -> None:
    healthcheck = compose["services"]["app"]["healthcheck"]
    probe = healthcheck["test"][-1]
    assert "/health" in probe


def test_compose_redis_is_valid():
    compose = yaml.safe_load((ROOT / "docker-compose.redis.yml").read_text())
    app_env = compose["services"]["app"]["environment"]
    assert app_env["STORAGE_BACKEND"] == "redis"
    assert "REDIS_URL" in app_env
    assert "redis" in compose["services"]
    assert compose["services"]["app"]["depends_on"]["redis"]["condition"] == "service_healthy"
    assert "healthcheck" in compose["services"]["redis"]
    _assert_app_healthcheck(compose)


def test_compose_postgres_is_valid():
    compose = yaml.safe_load((ROOT / "docker-compose.postgres.yml").read_text())
    app_env = compose["services"]["app"]["environment"]
    assert app_env["STORAGE_BACKEND"] == "postgres"
    assert "POSTGRES_DSN" in app_env
    assert "postgres" in compose["services"]
    _assert_app_healthcheck(compose)
