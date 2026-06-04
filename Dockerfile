# Use a slim, secure official Python runtime
FROM python:3.11-slim

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application architecture files
COPY ./app /code/app
COPY ./index.html /code/index.html

# Expose the internal port for Uvicorn
EXPOSE 8000

# Run the FastAPI production server instance
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]