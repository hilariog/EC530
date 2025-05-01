# Use a slim, Python 3 base
FROM python:3.10-slim

WORKDIR /app

# Install system deps (for SQLite etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the application code
COPY p2p.py . 

# Expose both possible ports
EXPOSE 8000 9001

# Default entrypoint: pass through args to the script
ENTRYPOINT ["python", "p2p.py"]
CMD ["--mode", "discovery", "--host", "0.0.0.0", "--port", "8000"]
