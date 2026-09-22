FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt supamigrate.py ./
COPY modules ./modules
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home --uid 10001 supamigrate && mkdir -p /app/backups && chown -R supamigrate:supamigrate /app
USER supamigrate
ENTRYPOINT ["python", "/app/supamigrate.py"]
