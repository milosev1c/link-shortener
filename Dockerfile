FROM python:3.13-slim AS builder

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.13-slim AS runtime

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY --from=builder /install /usr/local

USER appuser

EXPOSE 8000

CMD ["uvicorn", "link_shortener.main:app", "--host", "0.0.0.0", "--port", "8000"]
