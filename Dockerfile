FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ".[api]"
ENV PORT=8080
# Cloud Run sets $PORT; bind to it.
CMD ["sh", "-c", "uvicorn satorl.api.app:app --host 0.0.0.0 --port ${PORT}"]
