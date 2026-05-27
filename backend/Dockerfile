FROM python:3.12.13-slim-trixie

RUN pip install --no-cache-dir uv==0.11.14

WORKDIR /app

RUN groupadd --system app && useradd --system --create-home --gid app app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
