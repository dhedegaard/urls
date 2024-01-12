FROM python:3.12

ENV PORT=8080 \
  DATABASE_URL=''
EXPOSE ${PORT}

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
RUN python manage.py test && \
  python manage.py collectstatic -c --noinput

CMD python manage.py migrate && \
  gunicorn urls.wsgi
