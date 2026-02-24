FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY config.py .
COPY pinecone_client.py .
COPY embedding_client.py .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5002

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5002", "--timeout", "60", "app:app"]
