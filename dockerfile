# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY ./app ./app
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]