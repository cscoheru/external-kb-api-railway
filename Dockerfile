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

# Get PORT from environment or default to 5002
ENV PORT=5002
CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 60 --access-logfile - --error-logfile - app:app"]
