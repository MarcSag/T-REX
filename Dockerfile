# Use an official Python image as the base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Define the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    dcm2niix \
    fsl-core \
    ants \
    curl \
    git \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install HD-BET (as an example for external dependencies)
RUN pip install hd-bet

# Copy the requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire T-REX project into the container
COPY . .

# Set the default working directory for the container
WORKDIR /app

# Expose a port (if needed, e.g., for a service/API)
EXPOSE 8000

# Specify the default command for the container
CMD ["python", "trex.py", "--help"]