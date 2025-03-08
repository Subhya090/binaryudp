# Use a base image with necessary dependencies
FROM ubuntu:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for the Telegram bot
RUN pip3 install python-telegram-bot psutil flask

# Copy the sharp.c file and compile it
COPY sharp.c /app/sharp.c
WORKDIR /app
RUN gcc -o sharp sharp.c -lpthread

# Copy the Telegram bot script
COPY bot.py /app/bot.py

# Set the working directory
WORKDIR /app

# Set the entrypoint to run the bot
ENTRYPOINT ["python3", "bot.py"]
