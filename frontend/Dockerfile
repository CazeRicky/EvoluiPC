FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

EXPOSE 4173

CMD ["python", "-m", "http.server", "4173", "--bind", "0.0.0.0", "--directory", "/app"]
