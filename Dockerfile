FROM python:3.12-slim

COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN useradd -m -U -d /app notifications
USER notifications
WORKDIR /app

COPY app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
