# Use an official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output for real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and templates
COPY main.py .
COPY templates/ ./templates/

# Expose FastAPI default port
EXPOSE 8000

# Run Uvicorn server binding to 0.0.0.0 to allow container network routing
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
