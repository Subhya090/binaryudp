# Use a base image with necessary dependencies
FROM ubuntu:latest

# Install dependencies (e.g., gcc for compilation, python for Telegram bot)
RUN apt-get update && apt-get install -y \
    gcc \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy sharp.c and compile it
COPY sharp.c /app/sharp.c
WORKDIR /app
RUN gcc -o sharp sharp.c -lpthread

# Copy Telegram bot script
COPY bot.py /app/bot.py

# Install Python dependencies for the Telegram bot
RUN pip3 install python-telegram-bot

# Set the entrypoint to run the bot
ENTRYPOINT ["python3", "/app/bot.py"]
