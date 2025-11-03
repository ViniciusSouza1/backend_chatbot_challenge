# Use an official lightweight Python image
FROM python:3.11-slim

# Prevents Python from writing .pyc files and enables unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies needed for some Python packages
# You can remove or adjust these depending on your requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libffi-dev libssl-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements first (for better build cache efficiency)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Start the FastAPI app with Uvicorn
# ⚠️ Adjust "app.main:app" to match your actual module path if different
# Example: if your file is src/app/main.py, use "src.app.main:app"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]