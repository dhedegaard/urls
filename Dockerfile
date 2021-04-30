FROM python:3.6

COPY . ./
RUN pip install -r requirements.txt

ENV PORT 8080
EXPOSE ${PORT}

RUN python manage.py test && \
  python manage.py collectstatic -c --noinput

CMD python manage.py migrate && \
  gunicorn urls.wsgi
