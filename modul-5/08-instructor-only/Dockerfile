FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data
COPY samples ./samples

# Writable state (database, outbox, uploads) lives here.
RUN useradd --uid 10001 --no-create-home app && mkdir -p /app/runtime && chown -R app:app /app/runtime

# STARTER STATE: the container runs as ROOT with a writable filesystem and all capabilities.
# That is deliberate. Lab step 2 (Layer 5) asks you to harden it:
# see instructor/solution/docker-compose.hardened.yml for the pattern once you have tried yourself.

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app"]
