# Use a base image with necessary dependencies
FROM ubuntu:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate the virtual environment and install Python packages
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install python-telegram-bot psutil flask

# Copy the sharp.c file and compile it
COPY sharp.c /app/sharp.c
WORKDIR /app
RUN gcc -o sharp sharp.c -lpthread

# Copy the Telegram bot script
COPY bot.py /app/bot.py

# Set the working directory
WORKDIR /app

# Expose port 8080 for the Flask app
EXPOSE 8080

# Set the entrypoint to run the bot
ENTRYPOINT ["python3", "bot.py"]
