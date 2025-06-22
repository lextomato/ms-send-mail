FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mail_service.py .

CMD ["uvicorn", "mail_service:app", "--host", "0.0.0.0", "--port", "9000"]
