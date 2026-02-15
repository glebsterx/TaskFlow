FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directory for SQLite database
RUN mkdir -p /app/data

# Expose port for web API
EXPOSE 8000

# Run application (both bot and API)
CMD ["python", "-m", "app.main"]
