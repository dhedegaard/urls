FROM python:3.14
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PORT=8080 \
  DATABASE_URL=''

COPY . ./
RUN uv sync --frozen && \
  uv run ruff check . && \
  uv run pyright . && \
  uv run manage.py test && \
  uv run manage.py collectstatic -c --noinput

EXPOSE ${PORT}

CMD ["sh", "-c", "uv run manage.py migrate && uv run gunicorn urls.wsgi --bind 0.0.0.0:$PORT --access-logfile -"]
