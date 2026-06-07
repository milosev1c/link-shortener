import pytest
from pydantic import ValidationError

from link_shortener.config import Settings, get_settings


def test_settings_defaults():
    settings = Settings()
    assert settings.app_name == "link-shortener"
    assert settings.storage_backend == "redis"
    assert str(settings.base_url).rstrip("/") == "http://localhost:8000"
    assert settings.short_id_length == 8


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "postgres")
    monkeypatch.setenv("BASE_URL", "https://short.example.com")
    monkeypatch.setenv("SHORT_ID_LENGTH", "12")

    settings = Settings()

    assert settings.storage_backend == "postgres"
    assert str(settings.base_url).rstrip("/") == "https://short.example.com"
    assert settings.short_id_length == 12


def test_invalid_storage_backend_raises():
    with pytest.raises(ValidationError):
        Settings(storage_backend="mysql")


def test_get_settings_is_cached():
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert first is second
    get_settings.cache_clear()
