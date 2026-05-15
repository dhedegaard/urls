FROM python:3.14

ENV PORT=8080 \
  DATABASE_URL=''
EXPOSE ${PORT}

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . ./
RUN uv run ruff check . && \
  uv run pyright . && \
  uv run manage.py test && \
  uv run manage.py collectstatic -c --noinput

CMD uv run manage.py migrate && \
  uv run gunicorn urls.wsgi
