FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates netcat-traditional curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
ENV PYTHONPATH=/srv/app

ENV PORT=8080
ENV GUNICORN_CMD_ARGS="--config app/gunicorn_conf.py"

CMD ["gunicorn", "app.main:app"]
