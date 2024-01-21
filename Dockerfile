FROM python:3.11-slim

RUN useradd -m -U -d /app notifications
USER notifications
WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
