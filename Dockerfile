# Use a small, stable Python base image
FROM python:3.11-slim

# Don't buffer Python output (important for logs)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Expose the port your app uses (5001)
EXPOSE 5001

# Use gunicorn for production-like behavior
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]

