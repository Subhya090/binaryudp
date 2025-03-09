#!/bin/bash

# Set installation paths
DROPBEAR_DIR="$HOME/dropbear"
NGROK_DIR="$HOME/ngrok"

# Create necessary directories
mkdir -p $DROPBEAR_DIR && cd $DROPBEAR_DIR

# Install Dropbear
echo "[+] Downloading and installing Dropbear SSH..."
wget -q https://matt.ucc.asn.au/dropbear/releases/dropbear-2022.83.tar.bz2
tar -xjf dropbear-2022.83.tar.bz2 && cd dropbear-2022.83
./configure --prefix=$DROPBEAR_DIR && make && make install

# Generate SSH keys for Dropbear
echo "[+] Generating Dropbear SSH keys..."
$DROPBEAR_DIR/bin/dropbearkey -t rsa -f $DROPBEAR_DIR/dropbear_rsa_host_key

# Start Dropbear on port 4646
echo "[+] Starting Dropbear SSH on port 4646..."
nohup $DROPBEAR_DIR/bin/dropbear -p 4646 -r $DROPBEAR_DIR/dropbear_rsa_host_key > /dev/null 2>&1 &

# Move back to home directory
cd $HOME

# Install ngrok
echo "[+] Downloading and installing ngrok..."
wget -q -O ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip
unzip -q ngrok.zip -d $NGROK_DIR && rm ngrok.zip

# Prompt for ngrok authentication token
echo "[+] Enter your ngrok auth token: "
read NGROK_AUTH_TOKEN
$NGROK_DIR/ngrok authtoken $NGROK_AUTH_TOKEN

# Start ngrok TCP forwarding for Dropbear (port 4646)
echo "[+] Starting ngrok TCP tunnel for SSH..."
nohup $NGROK_DIR/ngrok tcp 4646 > /dev/null 2>&1 &

echo "[✔] Setup complete! Use 'ssh -p 4646 your-vps-user@your-vps-ip' to connect."
