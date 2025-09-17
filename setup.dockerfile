# Use official Python image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install pip, and dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]