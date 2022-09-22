FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir;
COPY . .
